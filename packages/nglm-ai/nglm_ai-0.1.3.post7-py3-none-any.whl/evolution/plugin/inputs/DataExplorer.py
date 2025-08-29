from abc import abstractmethod, ABC

from pandas import DataFrame


class DataExplorer(ABC):

    @abstractmethod
    def explore_data(self, data_frame: DataFrame) -> DataFrame:
        pass
