import json
import os
import time

import pandas as pd


class Logger:
    MAIN_FOLDER = "logs"

    def __init__(self, folder_name):
        self.folder_name = folder_name
        self.features_path = None
        self.portfolio_path = None


    def initialize(self):
        timestamp = int(time.time())
        os.makedirs(f'{Logger.MAIN_FOLDER}', exist_ok=True)
        subfolder_path = f'{Logger.MAIN_FOLDER}/{self.folder_name}_{timestamp}'
        os.makedirs(subfolder_path, exist_ok=True)

        self.features_path = f"{subfolder_path}/features.log"
        self.portfolio_path = f"{subfolder_path}/portfolio.log"

    def log(self, feature_service, portfolio_manager, price_data):
        with open(self.features_path, "a+") as f_features:
            f_features.write(json.dumps(feature_service.status) + "\n")
        with open(self.portfolio_path, "a+") as f_portfolio:
            f_portfolio.write(json.dumps(portfolio_manager.log_wallets(price_data)) + "\n")

        f_features.close()
        f_portfolio.close()

    def load_owner_wallet(self, owner_name):
        with open(self.portfolio_path, "r") as f:
            history = pd.read_json(f, lines=True)
        print(history)
        for column in history.columns:
            if column != "timestamp":
                history[column] = history[column].apply(lambda x: x[owner_name])
        return history


