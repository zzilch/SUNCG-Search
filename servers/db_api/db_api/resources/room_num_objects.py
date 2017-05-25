from flask import jsonify

from flask_restful import Resource
from flask_restful.utils import cors

from webargs import fields
from webargs.flaskparser import use_args, use_kwargs, parser

from db_api import cursor
from ..util import parseData

cmd_createtable = """
DROP TABLE IF EXISTS t1;
CREATE TEMPORARY TABLE t1 (
    SELECT 
		room_types_names.id
    FROM 
		room_types_names
    WHERE
		%s = "room"
		OR %s = room_types_names.name
);
"""

select_rooms_cmd = """
SELECT
	rooms.scene_id,
    rooms.level_num,
    rooms.room_num,
    rooms.num_objects
FROM
	rooms
JOIN room_types ON
	rooms.scene_id = room_types.scene_id AND
    rooms.level_num = room_types.level_num AND
    rooms.room_num = room_types.room_num
WHERE
	room_types.room_type_id IN (SELECT * FROM t1) AND
    rooms.num_objects != 0
ORDER BY
	num_objects %s
LIMIT
    300
"""

cmd_empty = """
SELECT
	rooms.scene_id,
    rooms.level_num,
    rooms.room_num,
    rooms.num_objects
FROM
	rooms
JOIN room_types ON
	rooms.scene_id = room_types.scene_id AND
    rooms.level_num = room_types.level_num AND
    rooms.room_num = room_types.room_num
WHERE
	room_types.room_type_id IN (SELECT * FROM t1) AND
    rooms.num_objects = 0
"""

def exec_cmd_createtables(roomtype):
    cursor.execute(cmd_createtable, (roomtype, roomtype))

def exec_cmd_query(order):
    cursor.execute(select_rooms_cmd % order)

def exec_cmd_empty():
    cursor.execute(cmd_empty)

class RoomManyObjects(Resource):
    room_many_objects_args = {
        'roomtype': fields.Str(required=True)
    }
    @cors.crossdomain(origin='*')
    @use_kwargs(room_many_objects_args)
    def get(self, roomtype):
        exec_cmd_createtables(roomtype)
        exec_cmd_query('DESC')
        data = cursor.fetchall()
        
        scene_return, level_return, room_return = parseData(data)
        return jsonify({'scene_results': scene_return,
                'level_results': level_return,
                'room_results' : room_return}), 200

class RoomFewObjects(Resource):
    room_few_objects_args = {
        'roomtype': fields.Str(required=True)
    }
    @cors.crossdomain(origin='*')
    @use_kwargs(room_few_objects_args)
    def get(self, roomtype):
        exec_cmd_createtables(roomtype)
        exec_cmd_query('ASC')
        data = cursor.fetchall()
        
        scene_return, level_return, room_return = parseData(data)
        return jsonify({'scene_results': scene_return,
                'level_results': level_return,
                'room_results' : room_return}), 200

class RoomEmpty(Resource):
    room_empty_args = {
        'roomtype': fields.Str(required=True)
    }
    @cors.crossdomain(origin='*')
    @use_kwargs(room_empty_args)
    def get(self, roomtype):
        exec_cmd_createtables(roomtype)
        exec_cmd_empty()
        data = cursor.fetchall()
        
        scene_return, level_return, room_return = parseData(data)
        return jsonify({'scene_results': scene_return,
                'level_results': level_return,
                'room_results' : room_return}), 200






