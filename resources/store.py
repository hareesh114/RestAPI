import uuid
from flask import request
from flask_smorest import abort, Blueprint
from flask.views import MethodView
from schema import StoreSchema
from models import StoreModel
from db import db
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

blp = Blueprint("stores", __name__, description="Operations on store")


@blp.route("/store/<int:store_id>")
class Store(MethodView):

    @blp.response(200, StoreSchema)
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store

    def delete(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()    
        return {"message": "Store Deleted"}
        


@blp.route("/store")
class StoreList(MethodView):
    
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()
    
    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self, request_data):

        item = StoreModel(**request_data)

        try:
            db.session.add(item)
            db.session.commit()
            return item
        
        except IntegrityError:
            abort(400, message="Store already exists")

        except SQLAlchemyError:
            abort(500, message="An error occured creating Store")



        