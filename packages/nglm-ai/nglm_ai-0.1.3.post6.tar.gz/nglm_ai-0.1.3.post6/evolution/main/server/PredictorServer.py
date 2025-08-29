from flask import Flask

from evolution.main.server.controllers.ControllerFactory import create_prediction_bp
from evolution.main.server.services.PredictionService import PredictionService


class PredictorServer:
    prediction_service: PredictionService = None

    def __init__(self):
        self.app = None
        app = Flask(__name__)

        #services
        prediction_service = PredictionService()

        app.register_blueprint(create_prediction_bp(prediction_service, "1"))
        app.run(port=5000)
        
    def run(self):
        self.app.run(port=5000)