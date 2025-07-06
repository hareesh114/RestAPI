from flask_smorest import abort, Blueprint
from flask.views import MethodView
from schema import UserSchema
from models import UserModel
from sqlalchemy.exc import SQLAlchemyError
from db import db 
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, get_jwt_identity
from blocklist import BLOCKLIST


blp = Blueprint("users", __name__, description="Operations on users")


@blp.route("/register")
class UserRegister(MethodView):

    @blp.arguments(UserSchema)
    @blp.response(201, UserSchema)
    def post(self, user_data):
        print("register")
        if UserModel.query.filter(UserModel.name == user_data["username"]).first():
            abort(409, message="Username exists")
        
        user = UserModel(name=user_data["username"], password=pbkdf2_sha256.hash(user_data["password"]))
        db.session.add(user)
        db.session.commit()

        return user

@blp.route("/login")
class UserLogin(MethodView):

    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(UserModel.name == user_data["username"]).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=str(user.id), fresh=True)
            refresh_token = create_access_token(identity=str(user.id))
            return {"access_taken" : access_token, "refresh_token": refresh_token}

        abort(401, message="Invalid credentials")

@blp.route("/logout")
class UserLogOut(MethodView):

    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"message": "Successfully logged out"}, 200


@blp.route("/refresh")
class Refresh(MethodView):

    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token()
        jti = get_jwt()['jti']
        BLOCKLIST.add(jti)
        return {"access_token": access_token}, 200



@blp.route("/user/<int:user_id>")
class User(MethodView):

    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user
    
    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User removed"}, 200
    
    

@blp.route("/test")
class Test(MethodView):

    def get(self):
        user = UserModel.query.all()
        user = user[0]
        return {"username": user.name, "password": user.password}
    