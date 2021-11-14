import os


class Logger:

    FOLDER = "logs"

    def __init__(self, file_name):
        self.file_name = file_name
        self.file = None

    def initialize(self):
        os.makedirs(f'{Logger.FOLDER}', exist_ok=True)
        self.file = open(f"{Logger.FOLDER}/{self.file_name}", "w")

    def log(self, feature_service, portfolio_manager):
        self.file.write(str(feature_service.status) + "\n")