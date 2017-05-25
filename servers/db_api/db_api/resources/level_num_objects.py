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
		scene_id,
        level_num,
        num_objects
	FROM
		levels
    WHERE
        levels.num_objects != 0
	ORDER BY
		num_objects %s
	LIMIT
		300
);
"""

cmd_empty = """
DROP TABLE IF EXISTS t1;
CREATE TEMPORARY TABLE t1 (
	SELECT
		scene_id,
        level_num,
        num_objects
	FROM
		levels
    WHERE 
        num_objects = 0
);
"""

select_rooms_cmd = """
SELECT
	rooms.scene_id,
    rooms.level_num,
    rooms.room_num,
    t1.num_objects
FROM
	rooms
JOIN t1 ON
	rooms.scene_id = t1.scene_id
    AND rooms.level_num = t1.level_num
"""

def exec_cmd_createtables(order):
    cursor.execute(cmd_createtable % order)

def exec_cmd_empty():
    cursor.execute(cmd_empty)

def exec_cmd_query():
    cursor.execute(select_rooms_cmd)

class LevelManyObjects(Resource):
    @cors.crossdomain(origin='*')
    def get(self):
        exec_cmd_createtables('DESC')
        exec_cmd_query()
        data = cursor.fetchall()
        
        scene_return, level_return, room_return = parseData(data)
        return jsonify({'scene_results': scene_return,
                'level_results': level_return,
                'room_results' : room_return}), 200

class LevelFewObjects(Resource):
    @cors.crossdomain(origin='*')
    def get(self):
        exec_cmd_createtables('ASC')
        exec_cmd_query()
        data = cursor.fetchall()
        
        scene_return, level_return, room_return = parseData(data)
        return jsonify({'scene_results': scene_return,
                'level_results': level_return,
                'room_results' : room_return}), 200

class LevelEmpty(Resource):
    @cors.crossdomain(origin='*')
    def get(self):
        exec_cmd_empty()
        exec_cmd_query()
        data = cursor.fetchall()
        
        scene_return, level_return, room_return = parseData(data)
        return jsonify({'scene_results': scene_return,
                'level_results': level_return,
                'room_results' : room_return}), 200

