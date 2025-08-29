import unittest

from evolution.plugin.model.ModelDataGenerator import ModelDataGenerator


class TestModelDataGen(ModelDataGenerator):

    def __init__(self):
        super().__init__()

    def generate_model_readable_data(self, data: dict) -> dict | None:
        return data