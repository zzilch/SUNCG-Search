from flask import jsonify

from flask_restful import Resource
from flask_restful.utils import cors

from db_api import cursor

cmd_query = """
SELECT
    id AS scene_id,
    hash
FROM
    scenes
"""

class Hashes(Resource):
    @cors.crossdomain(origin='*')
    def get(self):
        cursor.execute(cmd_query)
        data = cursor.fetchall()
        
        sceneid_to_hash = {}

        for row in data:
            sceneid_to_hash[row[0]] = row[1]
        
        return jsonify({
            'hashes' : sceneid_to_hash
        }), 200
