from flask import Flask, jsonify

from flask_restful import Resource, Api
from flask_restful.utils import cors

from flaskext.mysql import MySQL

from webargs import fields, validate
from webargs.flaskparser import use_args, use_kwargs, parser, abort

import operator

from db_api import cursor
from .. import util

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
GROUP BY 
	scene_id,
	level_num,
	room_num
"""

cmd_query2 = """
SELECT 
    scene_id,
	level_num,
	room_num,
    node_id
FROM objects
WHERE
	model_id IN (SELECT * FROM t1)
"""


def exec_cmd_createtables(object):
    cursor.execute(cmd_createtables, (object, object))

def exec_cmd_query(object):
    cursor.execute(cmd_query)

def exec_cmd_query2(object):
    cursor.execute(cmd_query2)

class SceneMembership(Resource):
    scene_membership_args = {
        'object': fields.Str(required=True)
    }
    @cors.crossdomain(origin='*')
    @use_kwargs(scene_membership_args)
    def get(self, object):
        exec_cmd_createtables(object)
        exec_cmd_query2(object)
        data = cursor.fetchall()
        
        scene_return, level_return, room_return = util.parse_data_vis(data)
        return jsonify({
            'enhanced_vis': True,
            'scene_results': scene_return,
            'level_results': level_return,
            'room_results': room_return
            }), 200

#class SceneMembership(Resource):
#    sceneMembership_args = {
#        'object': fields.Str(required=True)
#    }
#    @cors.crossdomain(origin='*')
#    @use_kwargs(sceneMembership_args)
#    def get(self, object):
#        exec_cmd_createtables(object)
#        exec_cmd_query(object)
#        data = cursor.fetchall()
#        
#        scene_return, level_return, room_return = util.parseData(data)
#        return jsonify({'scene_results': scene_return,
#                'level_results': level_return,
#                'room_results' : room_return}), 200

class LevelMembership(Resource):
    levelMembership_args = {
        'object': fields.Str(required=True)
    }
    @cors.crossdomain(origin='*')
    @use_kwargs(levelMembership_args)
    def get(self, object):
        exec_cmd_createtables(object)
        exec_cmd_query(object)
        data = cursor.fetchall()
        
        scene_return, level_return, room_return = util.parse_data_vis(data)
        return jsonify({
            'enhanced_vis' : True,
            'scene_results': scene_return,
            'level_results': level_return,
            'room_results' : room_return}), 200



