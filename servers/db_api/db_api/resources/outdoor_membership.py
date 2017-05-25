from flask import Flask, jsonify

from flask_restful import Resource, Api
from flask_restful.utils import cors

from flaskext.mysql import MySQL

from webargs import fields, validate
from webargs.flaskparser import use_args, use_kwargs, parser, abort

import operator

from db_api import cursor
from ..util import parseData

cmd_createtables = """
DROP TABLE IF EXISTS t1;

CREATE TEMPORARY TABLE t1 (
    SELECT model_id
    FROM models
    WHERE
        fine_grained_class = %s
        OR coarse_grained_class = %s
);
"""

cmd_query = """
SELECT 
    scene_id,
	level_num,
	room_num,
	COUNT(*) as occurances
FROM objects
WHERE
	model_id IN (SELECT * FROM t1)
    AND room_num = -1
GROUP BY 
	scene_id,
	level_num,
	room_num
"""

def exec_cmd_createtables(object):
    cursor.execute(cmd_createtables, (object, object))

def exec_cmd_query(object):
    cursor.execute(cmd_query)

class OutdoorMembership(Resource):
    outdoorMembership_args = {
        'object': fields.Str(required=True)
    }
    @cors.crossdomain(origin='*')
    @use_kwargs(outdoorMembership_args)
    def get(self, object):
        exec_cmd_createtables(object)
        exec_cmd_query(object)
        data = cursor.fetchall()
        
        scene_return, level_return, room_return = parseData(data)
        return jsonify({'scene_results': scene_return,
                'level_results': level_return,
                'room_results' : room_return}), 200



