from sys import api_version

from flask import Blueprint, request, jsonify

from evolution.main.server.services.PredictionService import PredictionService
api_version = "1"




def create_prediction_bp_v1(prediction_service: PredictionService):
    prediction_bp = Blueprint('prediction_bp', __name__, url_prefix='/churn_predictor/v1/')

    @prediction_bp.route('/predict', methods=['POST'])
    def predict():
        data = request.get_json()
        print(data.__class__.__name__)
        prediction_result = prediction_service.predict(data)
        prediction_result = prediction_service.predict(data)
        return jsonify(prediction_result.to_dict(api_version)), 200

    return prediction_bp


