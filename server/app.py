#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
api = Api(app)

db.init_app(app)

class Campers(Resource):
    def get(self):
        campers = [camper.to_dict(only=('id', 'name', 'age')) for camper in Camper.query.all()]
        return campers, 200
    
    def post(self):
        try:
            data = request.get_json()
            camper = Camper(name=data['name'], age=data['age'])
            db.session.add(camper)
            db.session.commit()
            return camper.to_dict(only=('id', 'name', 'age')), 201
        except Exception:
            return {'errors': ['validation errors']}, 400

class CamperByID(Resource):
    def get(self, id):
        camper = Camper.query.filter_by(id=id).first()
        if not camper:
            return {'error': 'Camper not found'}, 404
        return camper.to_dict(), 200
    
    def patch(self, id):
        camper = Camper.query.filter_by(id=id).first()
        if not camper:
            return {'error': 'Camper not found'}, 404
        try:
            data = request.get_json()
            for key in data:
                setattr(camper, key, data[key])
            db.session.commit()
            return camper.to_dict(only=('id', 'name', 'age')), 202
        except Exception:
            return {'errors': ['validation errors']}, 400

class Activities(Resource):
    def get(self):
        activities = [activity.to_dict(only=('id', 'name', 'difficulty')) for activity in Activity.query.all()]
        return activities, 200

class ActivityByID(Resource):
    def delete(self, id):
        activity = Activity.query.filter_by(id=id).first()
        if not activity:
            return {'error': 'Activity not found'}, 404
        db.session.delete(activity)
        db.session.commit()
        return '', 204

class Signups(Resource):
    def post(self):
        try:
            data = request.get_json()
            signup = Signup(
                camper_id=data['camper_id'],
                activity_id=data['activity_id'],
                time=data['time']
            )
            db.session.add(signup)
            db.session.commit()
            return signup.to_dict(), 201
        except Exception:
            return {'errors': ['validation errors']}, 400

api.add_resource(Campers, '/campers')
api.add_resource(CamperByID, '/campers/<int:id>')
api.add_resource(Activities, '/activities')
api.add_resource(ActivityByID, '/activities/<int:id>')
api.add_resource(Signups, '/signups')

@app.route('/')
def home():
    return ''

if __name__ == '__main__':
    app.run(port=5555, debug=True)
