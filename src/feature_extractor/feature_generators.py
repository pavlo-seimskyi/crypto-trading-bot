from src.data_scraper import time_helpers


class TalippGenerator:

    def __init__(self, talipp_class, input_column_names, **talipp_arguments):
        self.name = talipp_class.__name__ + TalippGenerator.args_to_string(talipp_arguments)
        self.input_column_names = input_column_names
        self.talipp_instance = talipp_class(input_values=[], **talipp_arguments)
        self.output_values = self.talipp_instance.output_values

    def initialize(self, data):
        for i, data_row in data.iterrows():
            self.add_value(data_row, purging=False)

    def add_value(self, data_row, purging):
        self.talipp_instance.add_input_value(float(data_row[self.input_column_names]))
        if purging:
            self.talipp_instance.purge_oldest(1)

    @staticmethod
    def args_to_string(arguments):
        suffix = "_"
        for k,v in arguments.items():
            suffix += f"{k}_{v}_"
        return suffix[:-1]

    @property
    def last_value(self):
        if len(self.talipp_instance.output_values) == 0:
            return None
        return self.talipp_instance.output_values[-1]


class TimestampGenerator:

    def __init__(self, input_column_names):
        self.name = "timestamp"
        self.input_column_names = input_column_names
        self.output_values = []

    def initialize(self, data):
        for i, data_row in data.iterrows():
            self.add_value(data_row, purging=False)

    def add_value(self, data_row, purging):
        timestamp = int(data_row[self.input_column_names])
        self.output_values.append(time_helpers.timestamp_to_str(timestamp, format="exact_time"))
        if purging:
            self.output_values = self.output_values[1:]

    @property
    def last_value(self):
        return self.output_values[-1]