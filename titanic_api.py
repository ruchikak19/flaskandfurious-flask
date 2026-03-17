from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource

# IMPORT YOUR MODEL (adjust path if needed)
from model.titanic import TitanicModel

# Create Blueprint
titanic_api = Blueprint('titanic_api', __name__, url_prefix='/api/titanic')
api = Api(titanic_api)

# Create endpoint
class Predict(Resource):
    def post(self):
        try:
            # Get JSON data from frontend
            passenger = request.get_json()

            # Get trained model (singleton)
            model = TitanicModel.get_instance()

            # Run prediction
            result = model.predict(passenger)

            # Return JSON response
            return jsonify(result)

        except Exception as e:
            return {"error": str(e)}, 400


# Route: /api/titanic/predict
api.add_resource(Predict, '/predict')