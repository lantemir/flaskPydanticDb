# добавить валидацию для user используя библиотеку pydantic

from dataclasses import dataclass
from http import HTTPStatus
import json
from turtle import st
from flask import Flask, jsonify, request, make_response
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
from pydantic import BaseModel, EmailStr, Field, ValidationError
from pydantic.dataclasses import dataclass as pydantic_dataclass

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/test.db'
app.config['JSON_SORT_KEYS'] = False
db = SQLAlchemy(app)

@pydantic_dataclass
class UserDto:
    email: EmailStr
    username: str = Field(min_length=2, max_length=25)


@dataclass
class UserModel(db.Model):
    email: str
    id: int
    username: str

    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

class UserList(Resource):
    def get(self):
        users = UserModel.query.all()
        return jsonify(users) # TODO: jsonify replace json.dumps
    def post(self):
        u = request.json
        try:
            UserDto(**u)
            user = UserModel(**u)
            db.session.add(user)
            db.session.commit()
            return jsonify(user)
        except ValidationError as e:
            message = json.loads(e.json())
            code = HTTPStatus.BAD_REQUEST
            return make_response(jsonify({"error": message}), code)
        
        

class User(Resource):
    def get(self, user_id):
        user = UserModel.query.get(int(user_id))
        return jsonify(user)
    def put(self, user_id):
        try:
            UserDto(**request.json)
            user = UserModel.query.get(int(user_id))
            user.username = request.json["username"]
            user.email = request.json["email"]
            db.session.commit()
            return jsonify(user)
        except ValidationError as e:
            message = json.loads(e.json())
            code = HTTPStatus.BAD_REQUEST
            return make_response(jsonify({"error": message}), code)
    def delete(self, user_id):
        user = UserModel.query.get(int(user_id))
        db.session.delete(user)
        db.session.commit()
        return jsonify(user)


api.add_resource(UserList, '/users')
api.add_resource(User, '/users/<user_id>')

if __name__ == '__main__':
    app.run(debug=True)