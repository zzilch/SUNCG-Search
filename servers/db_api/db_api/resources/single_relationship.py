from flask import jsonify

from flask_restful import Resource
from flask_restful.utils import cors

from webargs import fields, validate
from webargs.flaskparser import use_args, use_kwargs, parser, abort

from db_api import cursor
from ..util import parseData

cmd_temptables = """
DROP TABLE IF EXISTS t1;
DROP TABLE IF EXISTS t2;
DROP TABLE IF EXISTS rel;

CREATE TEMPORARY TABLE t1 (
    SELECT model_id
    FROM models
    WHERE
        fine_grained_class = %s
        OR coarse_grained_class = %s
);

CREATE TEMPORARY TABLE t2 (
    SELECT model_id
    FROM models
    WHERE
        fine_grained_class = %s
        OR coarse_grained_class = %s
);

CREATE TEMPORARY TABLE rel (
    SELECT
        relations.id
    FROM relations
    WHERE
        relations.name = %s
)
"""

def exec_cmd_temptables(pri_class, sec_class, relationship):
    cursor.execute(cmd_temptables, (pri_class, pri_class, \
                                    sec_class, sec_class, \
                                    relationship))

cmd_query = """
SELECT
    scene_id,
    level_num,
    room_num,
    COUNT(*) AS occurences
FROM
    pairwise_rels pr
WHERE
    pr.primary_id IN (SELECT * FROM t1)
    AND pr.secondary_id IN (SELECT * FROM t2)
    AND pr.relation_id IN (SELECT * FROM rel)
GROUP BY
    scene_id,
    level_num,
    room_num
ORDER BY
    occurences DESC
"""

class SingleRelationship(Resource):
    singlerelationship_args = {
        'primary': fields.Str(required=True),
        'relationship': fields.Str(required=True),
        'secondary': fields.Str(required=True),
    }
    
    @cors.crossdomain(origin='*')
    @use_kwargs(singlerelationship_args)
    def get(self, primary, relationship, secondary):
        print "SingleRelationship"
        exec_cmd_temptables(primary, secondary, relationship)
        cursor.execute(cmd_query)
        data = cursor.fetchall()

        scene_return, level_return, room_return = parseData(data)
        return jsonify({'scene_results': scene_return,
                        'level_results': level_return,
                        'room_results' : room_return}), 200
    

