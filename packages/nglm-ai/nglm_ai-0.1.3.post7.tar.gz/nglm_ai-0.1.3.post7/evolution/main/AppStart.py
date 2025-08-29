

from pandas import DataFrame

from evolution.plugin.inputs.DataExplorer import DataExplorer
from evolution.plugin.inputs.DataCleaner import DataCleaner
from evolution.plugin.inputs.file.FileInputDataReader import FileInputDataReader
from evolution.plugin.inputs.InputDataReader import InputDataReader
from evolution.utility import load_class


class AppStart:
    input_data_reader: InputDataReader = None
    data_cleaner: DataCleaner = None
    data_explorer: DataExplorer = None
    config: dict = None

    def __init__(self, config: dict):
        self.config = config
        input_type = self.config["input_type"]
        if input_type == 'file':
            self.input_data_reader = load_class('evolution.plugin.inputs.file.FileInputDataReader', 'FileInputDataReader', FileInputDataReader);
        else:
            self.input_data_reader = load_class('evolution.plugin.inputs.file.FileInputDataReader', 'FileInputDataReader', FileInputDataReader);
        self.input_data_reader.load_configs(config)

        self.load_plugins()
        print("plugins loaded")

    def load_plugins(self):
        self.data_cleaner = load_class(self.config["cleaner_package"], self.config["cleaner_class"], DataCleaner)
        self.data_explorer = load_class(self.config["explorer_package"], self.config["explorer_class"], DataExplorer)

    def clean_data(self, dataframe: DataFrame) -> DataFrame:
        return self.data_cleaner.clean_data(dataframe)

    def explore_data(self, dataframe: DataFrame) -> DataFrame:
        return self.data_explorer.explore_data(dataframe)



    def validate_data(self, dataframe: DataFrame) -> DataFrame:
        print("validating data - final dataframe")
        print(dataframe)
        return dataframe

    def run(self):
        self.input_data_reader.read_data()
        data_frame = self.input_data_reader.get_data()
        data_frame = self.clean_data(data_frame)
        data_frame = self.explore_data(data_frame)
        self.validate_data(data_frame)
        print("all done")
        pass


my_config = {
    'input_type':'file',
    'file_path':'C:\\Users\\rmitra.INDIA\\PycharmProjects\\nglm-ai\\support\\input-data.json',
    'cleaner_package':'qa.plugins.cleaner.QACleaner',
    'cleaner_class':'QACleaner1',
    'explorer_package':'qa.plugins.explorer.QADataExplorer',
    'explorer_class':'QADataExplorer',
    'output_path':'C:\\Users\\rmitra.INDIA\\PycharmProjects\\nglm-ai\\support\\'
}
#app_start = AppStart(my_config)
#app_start.run()

