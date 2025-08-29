from evolution.main.server.dto.PredictionResult import PredictionResult
from evolution.plugin.model.ModelDataGenerator import ModelDataGenerator
from evolution.utility import load_class


class PredictionService:
    model_data_generator: ModelDataGenerator = None
    config: dict = None

    def __init__(self, config: dict):
        self.config = config
        self.load_plugins()

    def load_plugins(self):
        self.model_data_generator = load_class(self.config["model_data_gen_module"], self.config["model_data_gen_class"], ModelDataGenerator)

    def predict(self, data: dict) -> PredictionResult:
        feature_data = data.get('feature_data')
        identifier = data.get('identifier')
        #model_data = self.model_data_generator.generate_model_readable_data(feature_data)

        prediction_result: PredictionResult = PredictionResult("9830188417", 75.82)
        return prediction_result

