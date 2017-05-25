from flask import jsonify

from flask_restful import Resource
from flask_restful.utils import cors

from db_api import cursor

class DatabaseStats(Resource):
    @cors.crossdomain(origin='*')
    def get(self):
        cursor.execute('''SELECT COUNT(id) AS numScenes FROM scenes ''')
        data = cursor.fetchall()
        
        count = int(filter(str.isdigit, str(data)))
        return jsonify({'numScenes': count}), 200

class Ping(Resource):
    @cors.crossdomain(origin='*')
    def get(self):
        return jsonify({'status':'ok!'}), 200


