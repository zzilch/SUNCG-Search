from flask import jsonify

from flask_restful import Resource
from flask_restful.utils import cors

from webargs import fields
from webargs.flaskparser import use_args, use_kwargs, parser

from db_api import cursor
from ..util import parseData

cmd_createtables = """
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

cmd_query = """
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
"""

def exec_cmd_createtables(object):
    cursor.execute(cmd_createtables, (object))

def exec_cmd_query(object):
    cursor.execute(cmd_query, (object))

class TooMany(Resource):
    sceneMembership_args = {
        'object': fields.Str(required=True)
    }
    @cors.crossdomain(origin='*')
    @use_kwargs(sceneMembership_args)
    def get(self, object):
        exec_cmd_createtables(object)
        exec_cmd_query(object)
        data = cursor.fetchall()
        
        scene_return, level_return, room_return = parseData(data)
        return jsonify({'scene_results': scene_return,
                'level_results': level_return,
                'room_results' : room_return}), 200



