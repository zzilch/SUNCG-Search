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

cmd_query = """
SELECT
	rooms.scene_id,
    rooms.level_num,
    rooms.room_num,
    area
FROM
	rooms
JOIN room_types ON
	rooms.scene_id = room_types.scene_id AND
    rooms.level_num = room_types.level_num AND
    rooms.room_num = room_types.room_num
WHERE
	room_types.room_type_id IN (SELECT * FROM t1)
ORDER BY
	area %s
LIMIT
    300
"""

def exec_cmd_createtable(roomtype):
    cursor.execute(cmd_createtable, (roomtype, roomtype))

def exec_cmd_query(order):
    cursor.execute(cmd_query % order)

class RoomGreaterArea(Resource):
    room_greater_area_args = {
        'roomtype': fields.Str(required=True)
    }
    @cors.crossdomain(origin='*')
    @use_kwargs(room_greater_area_args)
    def get(self, roomtype):
        exec_cmd_createtable(roomtype)
        exec_cmd_query('DESC')
        data = cursor.fetchall()
        
        scene_return, level_return, room_return = parseData(data)
        return jsonify({'scene_results': scene_return,
                'level_results': level_return,
                'room_results' : room_return}), 200

class RoomLesserArea(Resource):
    room_lesser_area_args = {
        'roomtype': fields.Str(required=True)
    }
    @cors.crossdomain(origin='*')
    @use_kwargs(room_lesser_area_args)
    def get(self, roomtype):
        exec_cmd_createtable(roomtype)
        exec_cmd_query('ASC')
        data = cursor.fetchall()
        
        scene_return, level_return, room_return = parseData(data)
        return jsonify({'scene_results': scene_return,
                'level_results': level_return,
                'room_results' : room_return}), 200




