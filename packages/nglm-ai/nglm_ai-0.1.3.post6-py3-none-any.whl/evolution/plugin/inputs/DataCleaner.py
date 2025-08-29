from abc import abstractmethod, ABC

from pandas import DataFrame


class DataCleaner(ABC):

    @abstractmethod
    def clean_data(self, data_frame: DataFrame) -> DataFrame:
        pass