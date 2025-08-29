from abc import abstractmethod, ABC


class ModelDataGenerator(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def generate_model_readable_data(self, data: dict) -> dict | None:
        pass
