from flask import Blueprint

from evolution.main.server.controllers.v1.PredictionController import create_prediction_bp_v1


def create_prediction_bp(prediction_service, api_version: str) -> Blueprint | None:
    match api_version:
        case '1':
            return create_prediction_bp_v1(prediction_service)
    return None