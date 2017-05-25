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
		area
	FROM 
		levels
	ORDER BY
		area %s
	LIMIT 300
);
"""

cmd_query = """
SELECT
	rooms.scene_id,
    rooms.level_num,
    rooms.room_num,
    t1.area
FROM
	rooms
JOIN t1
	ON rooms.scene_id = t1.scene_id
    AND rooms.level_num = t1.level_num 
ORDER BY
	t1.area
"""

def exec_cmd_createtables(order):
    cursor.execute(cmd_createtable % order)

def exec_cmd_query():
    cursor.execute(cmd_query)

class LevelGreaterArea(Resource):
    @cors.crossdomain(origin='*')
    def get(self):
        exec_cmd_createtables('DESC')
        exec_cmd_query()
        data = cursor.fetchall()
        
        scene_return, level_return, room_return = parseData(data)
        return jsonify({'scene_results': scene_return,
                'level_results': level_return,
                'room_results' : room_return}), 200

class LevelLesserArea(Resource):
    @cors.crossdomain(origin='*')
    def get(self):
        exec_cmd_createtables('ASC')
        exec_cmd_query()
        data = cursor.fetchall()
        
        scene_return, level_return, room_return = parseData(data)
        return jsonify({'scene_results': scene_return,
                'level_results': level_return,
                'room_results' : room_return}), 200




