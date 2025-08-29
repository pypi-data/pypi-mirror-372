from evolution.main.server.models.PredictionResult import PredictionResult
from evolution.plugin.model.ModelDataGenerator import ModelDataGenerator


class PredictionService:
    #model_data_generator: ModelDataGenerator = None

    def __init__(self):
        pass

    def predict(self, data: dict) -> PredictionResult:
        feature_data = data.get('feature_data')
        identifier = data.get('identifier')
        #model_data = self.model_data_generator.generate_model_readable_data(feature_data)

        prediction_result: PredictionResult = PredictionResult("9830188417", 75.82)
        return prediction_result

