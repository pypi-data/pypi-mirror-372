class PredictionResult:
    identifier: str = None
    prediction: float = None

    def __init__(self, identifier: str, prediction: float):
        self.prediction = prediction
        self.identifier = identifier

    def to_dict(self, api_version: str) -> dict:
        return {"identifier" : self.identifier, "prediction" : self.prediction, "api_version" : api_version}