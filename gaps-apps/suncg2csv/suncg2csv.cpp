// Source file for the scene converter program

// Include files 

#include "R3Graphics/R3Graphics.h"
#include "unistd.h"
#include <vector>
#include <string>
#include <string.h>
#include <fstream>

// Application Variables

static std::vector<std::string> project_ids;
static std::vector<std::string> model_ids;
static std::vector<std::string> rtype_ids;

// Program Variables
static const char *output_directory = NULL;

static const char *project_list = "../../../data/list-of-projects.txt";
static const char *rtype_list = "../../../data/list-of-rtypes.txt";

static int print_verbose = 0;

////////////////////////////////////////////////////////////////////////
// Load Data
////////////////////////////////////////////////////////////////////////

static int LoadRTypes() {
    std::ifstream file(rtype_list);
    std::string str;
    while (std::getline(file, str))
    {
        rtype_ids.push_back(str);
    }

    return 1;
}

static int LoadProjects() {
    std::ifstream file(project_list);
    std::string str;
    while (std::getline(file, str))
    {
        project_ids.push_back(str);
    }

    return 1;
}

////////////////////////////////////////////////////////////////////////
// Get Data
////////////////////////////////////////////////////////////////////////

static int 
getRTypeId(const char* name)
{
    if (!name)
        return -1;

    for (size_t i = 0; i < rtype_ids.size(); i++) {
        if (strcmp(rtype_ids[i].c_str(), name) == 0) return i+1;
    }

    return -1;
}

static int 
getSceneId(const char* name)
{
    for (size_t i = 0; i < project_ids.size(); i++) {
        if (strcmp(project_ids[i].c_str(), name) == 0) return i;
    }

    return -1;
}

////////////////////////////////////////////////////////////////////////
// CSV HEADERS
////////////////////////////////////////////////////////////////////////

void PrintScenesHeader(FILE* scenes_file){
    fprintf(scenes_file, "id,num_levels,num_rooms,num_objects,hash\n");
}

void PrintLevelsHeader(FILE* levels_file){
    fprintf(levels_file, "scene_id,level_num,num_rooms,num_objects,area\n");
}

void PrintRoomsHeader(FILE* rooms_file){
    fprintf(rooms_file, "scene_id,level_num,room_num,num_objects,area,node_id\n");
}

void PrintObjectsHeader(FILE* objects_file){
    fprintf(objects_file, "scene_id,level_num,room_num,object_num,model_id,node_id\n");
}

void PrintRoomTypesHeader(FILE* objects_file){
    fprintf(objects_file, "scene_id,level_num,room_num,room_type_id\n");
}


////////////////////////////////////////////////////////////////////////
// MAIN LOOP
////////////////////////////////////////////////////////////////////////

static int
ParseScene(R3Scene *scene, FILE* scenes_file, FILE* levels_file, FILE* rooms_file, FILE* objects_file, FILE* room_types_file )
{
    PrintScenesHeader(scenes_file);
    PrintLevelsHeader(levels_file);
    PrintRoomsHeader(rooms_file);
    PrintObjectsHeader(objects_file);
    PrintRoomTypesHeader(room_types_file);
    
    R3SceneNode* root = scene->Node(0);
    const char* suncg_hash = root->Name();
    int scene_id = getSceneId(suncg_hash);

    int num_levels = root->NChildren();
    int num_rooms_total = 0;
    int num_objects_total = 0;

    int outdoor_object_num = 0;

    // Levels
    for (int level_num = 0; level_num < root->NChildren(); level_num++) {
        R3SceneNode* level_node = root->Child(level_num);
        int num_objects_level = 0;
        int num_rooms = 0;
        
        // Rooms
        for (int room_num = 0; room_num < level_node->NChildren(); room_num++) {
            R3SceneNode* node = level_node->Child(room_num);
            const char* node_id = node->Name(); 

            if (strstr(node_id, "Ground")) { // Ignore "Ground"
                continue;
            } else if (strstr(node_id, "Object")) { // "Outdoor" Objects, not associated with a room
                num_objects_level++;
                
                if (node->NReferences() == 0) // Ignore Wall, Floor, Ceiling
                    continue;
                
                const char* model_id = node->Reference(0)->ReferencedScene()->Name();
                int object_num = outdoor_object_num++;

                fprintf(objects_file, "%d,%d,%d,%d,%s,%s\n",
                        scene_id,level_num,-1,object_num,model_id,node_id);

                continue;
            } else if (strstr(node_id, "Room")) {
                num_rooms++;
                int num_objects_room = 0;

                // Objects
                for (int object_num = 0; object_num < node->NChildren(); object_num++) {
                    R3SceneNode* object_node = node->Child(object_num);

                    if (object_node->NReferences() == 0) // Wall, Floor, Ceiling
                        continue;
                    num_objects_room++;

                    const char* model_id = object_node->Reference(0)->ReferencedScene()->Name();
                    const char* object_id = object_node->Name();
                    
                    fprintf(objects_file, "%d,%d,%d,%d,%s,%s\n",
                            scene_id,level_num,room_num,object_num,model_id,object_id);
                }

                int room_type = 0;
                if (!node->FixedInfo("roomTypes").empty()) {
                    room_type = getRTypeId(node->FixedInfo("roomTypes").c_str());
                }

                double room_area = node->Area();
                fprintf(rooms_file, "%d,%d,%d,%d,%f,%s\n",
                        scene_id,level_num,room_num,num_objects_room,room_area,node_id);
                fprintf(room_types_file, "%d,%d,%d,%d\n",
                        scene_id,level_num,room_num,room_type);

                num_objects_level += num_objects_room;

                continue;
            }
        }

        double level_area = level_node->Area();
    
        fprintf(levels_file, "%d,%d,%d,%d,%f\n",
                scene_id,level_num,num_rooms,num_objects_level,level_area);

        num_rooms_total += num_rooms;
        num_objects_total += num_objects_level;
    }

    fprintf(scenes_file, "%d,%d,%d,%d,%s\n", 
            scene_id,num_levels,num_rooms_total,num_objects_total,suncg_hash);

    // Return OK status
    return 1;
}

////////////////////////////////////////////////////////////////////////
// PROGRAM ARGUMENT PARSING
////////////////////////////////////////////////////////////////////////

static int
ParseArgs(int argc, char **argv)
{
    // Parse arguments
    argc--; argv++;
    while (argc > 0) {
        if ((*argv)[0] == '-') {
            if (!strcmp(*argv, "-v")) print_verbose = 1;
            else { fprintf(stderr, "Invalid program argument: %s", *argv); exit(1); }
            argv++; argc--;
        }
        else {
            if (!output_directory) output_directory = *argv;
            else { fprintf(stderr, "Invalid program argument: %s", *argv); exit(1); }
            argv++; argc--;
        }
    }

    // Check input filename
    if (!output_directory) {
        fprintf(stderr, "Usage: suncg2csv output_directory [options]\n");
        return 0;
    }

    // Return OK status 
    return 1;
}



////////////////////////////////////////////////////////////////////////
// MAIN
////////////////////////////////////////////////////////////////////////


int main(int argc, char **argv)
{
    // Check number of arguments
    if (!ParseArgs(argc, argv)) exit(1);
    
    // Rename to actual projectname.csv 
    // because not loading everything, but individually
    char output_scenes_filename[1024];
    sprintf(output_scenes_filename, "%s/scenes.csv", output_directory);

    char output_levels_filename[1024];
    sprintf(output_levels_filename, "%s/levels.csv", output_directory);

    char output_rooms_filename[1024];
    sprintf(output_rooms_filename, "%s/rooms.csv", output_directory);

    char output_objects_filename[1024];
    sprintf(output_objects_filename, "%s/objects.csv", output_directory);

    char output_room_types_filename[1024];
    sprintf(output_room_types_filename, "%s/room_types.csv", output_directory);

    // Open the csv files
    FILE *scenes_fp = fopen(output_scenes_filename, "w");
    if (!scenes_fp) {
        fprintf(stderr, "Unable to open output file %s\n", output_scenes_filename);
        exit(-1);
    }
    FILE *levels_fp = fopen(output_levels_filename, "w");
    if (!levels_fp) {
        fprintf(stderr, "Unable to open output file %s\n", output_levels_filename);
        exit(-1);
    }
    FILE *rooms_fp = fopen(output_rooms_filename, "w");
    if (!rooms_fp) {
        fprintf(stderr, "Unable to open output file %s\n", output_rooms_filename);
        exit(-1);
    }
    FILE *objs_fp = fopen(output_objects_filename, "w");
    if (!objs_fp) {
        fprintf(stderr, "Unable to open output file %s\n", output_objects_filename);
        exit(-1);
    }
    FILE *rtypes_fp = fopen(output_room_types_filename, "w");
    if (!rtypes_fp) {
        fprintf(stderr, "Unable to open output file %s\n", output_room_types_filename);
        exit(-1);
    }

    // Load data for assingment of ids
    if(!LoadProjects()) exit(-1);
    if(!LoadRTypes()) exit(-1);

    // Allocate scene
    R3Scene *scene = new R3Scene();
    if (!scene) {
        fprintf(stderr, "Unable to allocate scene.\n");
        exit(-1);
    } 
    if (!scene->ReadSUNCGFile("house.json")) {
        fprintf(stderr, "Unable to read SUNCG file  %s\n", "house.json");
        exit(-1);
    }

    ParseScene(scene, scenes_fp, levels_fp, rooms_fp, objs_fp, rtypes_fp);

    // Return success 
    return 0;
}
