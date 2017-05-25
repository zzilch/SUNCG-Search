from flask import jsonify

from flask_restful import Resource
from flask_restful.utils import cors

from webargs import fields, validate
from webargs.flaskparser import use_args, use_kwargs, parser

from db_api import cursor
from ..util import parseData, parse_data_vis

cmd_createtable = """
DROP TABLE IF EXISTS t1;
CREATE TEMPORARY TABLE t1 (
	SELECT
		id,
        num_objects
	FROM
		scenes
    WHERE
        scenes.num_objects != 0
	ORDER BY
		scenes.num_objects %s
	LIMIT
		300
);
"""

cmd_empty = """
DROP TABLE IF EXISTS t1;
CREATE TEMPORARY TABLE t1 (
	SELECT
		id,
        num_objects
	FROM
		scenes
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
	rooms.scene_id = t1.id
"""

def exec_cmd_createtables(order):
    cursor.execute(cmd_createtable % order)

def exec_cmd_query():
    cursor.execute(select_rooms_cmd)

def exec_cmd_empty():
    cursor.execute(cmd_empty)

cmd_createtable2 = """
DROP TABLE IF EXISTS t1;
CREATE TEMPORARY TABLE t1 (
	SELECT
		stddev,
        average
	FROM
		fine_class_stats
	WHERE
		class = %s
);
"""

cmd_2 = """
DROP TABLE IF EXISTS t2;
CREATE TEMPORARY TABLE t2 (
	SELECT
		*
	FROM
	(
		SELECT
			scene_id,
			level_num,
			room_num,
			COUNT(*) AS amount
		FROM 
			objects
		JOIN models
			ON objects.model_id = models.model_id
		WHERE
			fine_grained_class = %s
		GROUP BY
			objects.model_id,
			scene_id,
			level_num,
			room_num
		ORDER BY
			amount DESC
	) a
	WHERE
		amount > (SELECT 3*stddev + average FROM t1)
);
"""

cmd_21 = """
SELECT 
	objects.scene_id,
    objects.level_num,
    objects.room_num,
    node_id
FROM objects
JOIN t2 ON
	objects.scene_id = t2.scene_id AND
    objects.level_num = t2.level_num AND
    objects.room_num = t2.room_num
"""

def call_many_by_object(object):
    cursor.execute(cmd_createtable2, (object))
    cursor.execute(cmd_2, (object))
    cursor.execute(cmd_21)

    data = cursor.fetchall()

    scene_return, level_return, room_return = parse_data_vis(data)
    return jsonify({'scene_results': scene_return,
                'level_results': level_return,
                'room_results' : room_return}), 200


class SceneManyObjects(Resource):
    scene_many_objects_args = {
        'object': fields.Str(required=False)
    }
    @use_kwargs(scene_many_objects_args)
    @cors.crossdomain(origin='*')
    def get(self, object):
        if isinstance(object, basestring):
            return call_many_by_object(object)

        exec_cmd_createtables('DESC')
        exec_cmd_query()
        data = cursor.fetchall()
        
        scene_return, level_return, room_return = parseData(data)
        return jsonify({'scene_results': scene_return,
                'level_results': level_return,
                'room_results' : room_return}), 200
cmd_3 = """
DROP TABLE IF EXISTS t2;
CREATE TEMPORARY TABLE t2 (
	SELECT
		*
	FROM
	(
		SELECT
			scene_id,
			level_num,
			room_num,
			COUNT(*) AS amount
		FROM 
			objects
		JOIN models
			ON objects.model_id = models.model_id
		WHERE
			fine_grained_class = %s
		GROUP BY
			objects.model_id,
			scene_id,
			level_num,
			room_num
		ORDER BY
			amount DESC
	) a
	WHERE
		amount < (SELECT average FROM t1)
        AND amount != 0
);
"""

cmd_31 = """
SELECT 
	objects.scene_id,
    objects.level_num,
    objects.room_num,
    node_id
FROM objects
JOIN t2 ON
	objects.scene_id = t2.scene_id AND
    objects.level_num = t2.level_num AND
    objects.room_num = t2.room_num
"""

def call_few_by_object(object):
    cursor.execute(cmd_createtable2, (object))
    cursor.execute(cmd_3, (object))
    cursor.execute(cmd_31)

    data = cursor.fetchall()

    scene_return, level_return, room_return = parseData(data)
    return jsonify({
                'enhanced_vis': True,
                'scene_results': scene_return,
                'level_results': level_return,
                'room_results' : room_return
            }), 200

class SceneFewObjects(Resource):
    scene_few_objects_args = {
        'object': fields.Str(required=False)
    }
    @use_kwargs(scene_few_objects_args)
    @cors.crossdomain(origin='*')
    def get(self, object):
        if isinstance(object, basestring):
            return call_few_by_object(object)

        exec_cmd_createtables('ASC')
        exec_cmd_query()
        data = cursor.fetchall()
        
        scene_return, level_return, room_return = parseData(data)
        return jsonify({'scene_results': scene_return,
                'level_results': level_return,
                'room_results' : room_return}), 200

class SceneEmpty(Resource):
    @cors.crossdomain(origin='*')
    def get(self):
        exec_cmd_empty()
        exec_cmd_query()
        data = cursor.fetchall()
        
        scene_return, level_return, room_return = parseData(data)
        return jsonify({'scene_results': scene_return,
                'level_results': level_return,
                'room_results' : room_return}), 200

