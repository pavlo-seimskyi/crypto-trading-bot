import copy


class FeatureService:

    def __init__(self, *feature_generators):
        self.feature_generators = feature_generators
        # Value used to reset the service
        self._empty_feature_generators = copy.deepcopy(feature_generators)

    def reset(self):
        self.feature_generators = self._empty_feature_generators

    def initialize(self, data):
        for feature_generator in self.feature_generators:
            feature_generator.initialize(data)

    def add_value(self, data_row, purging=False):
        for feature_generator in self.feature_generators:
            feature_generator.add_value(data_row, purging)

    @property
    def all_data(self):
        return {feature_generator.name: feature_generator.output_values for feature_generator in self.feature_generators}

    @property
    def status(self):
        return {feature_generator.name: feature_generator.last_value for feature_generator in self.feature_generators}

