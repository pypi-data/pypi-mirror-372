from flask import Flask

from evolution.main.server.controllers.ControllerFactory import create_prediction_bp
from evolution.main.server.services.PredictionService import PredictionService


class PredictorServer:
    prediction_service: PredictionService = None
    app: Flask = None
    config: dict = None

    def __init__(self, config: dict):
        self.app = Flask(__name__)
        self.config = config

        #services
        prediction_service = PredictionService(config)

        self.app.register_blueprint(create_prediction_bp(prediction_service, "1"))
        
    def run(self):
        self.app.run(port=self.config['port'])

    def get_app(self) -> Flask:
        return self.app