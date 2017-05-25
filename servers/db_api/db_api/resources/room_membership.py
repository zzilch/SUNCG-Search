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

DROP TABLE IF EXISTS t2;
CREATE TEMPORARY TABLE t2 (
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
    objects.scene_id,
    objects.`level_num`,
    objects.`room_num`,
    COUNT(*) 
FROM 
	objects
JOIN room_types on 
    objects.scene_id = room_types.scene_id and
    objects.level_num = room_types.level_num and
    objects.room_num = room_types.room_num
WHERE 
    model_id IN (SELECT * FROM t1)
    AND room_types.room_type_id IN (SELECT * FROM t2)
GROUP BY 
    objects.scene_id,
    objects.`level_num`,
    objects.`room_num`;
"""

cmd_query2 = """
SELECT 
    objects.scene_id,
    objects.`level_num`,
    objects.`room_num`,
	node_id
FROM 
	objects
JOIN room_types on 
    objects.scene_id = room_types.scene_id and
    objects.level_num = room_types.level_num and
    objects.room_num = room_types.room_num
WHERE 
    model_id IN (SELECT * FROM t1)
    AND room_types.room_type_id IN (SELECT * FROM t2)
"""

def exec_cmd_createtables(roomtype, object):
    cursor.execute(cmd_createtables, (object, object, roomtype, roomtype))

def exec_cmd_query():
    cursor.execute(cmd_query2)

class RoomMembership(Resource):
    room_membership_args = {
        'roomtype': fields.Str(required=True),
        'object': fields.Str(required=True)
    }
    @cors.crossdomain(origin='*')
    @use_kwargs(room_membership_args)
    def get(self, roomtype, object):
        exec_cmd_createtables(roomtype, object)
        exec_cmd_query()
        data = cursor.fetchall()
        
        scene_return, level_return, room_return = util.parse_data_vis(data)
        #scene_return, level_return, room_return = parseData(data)
        #test_results = parseData2(data)
        return jsonify({
                'enhanced_vis': True,
                'scene_results': scene_return,
                'level_results': level_return,
                'room_results' : room_return,
                }), 200


