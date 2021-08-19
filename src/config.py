from talipp.indicators import EMA, RSI

from src.feature_extractor.feature_generators import TalippGenerator

# TO TRADE
CURRENCY_TO_BUY = 'BTC'
CURRENCY_TO_SELL = 'EUR'

# SAVING THE DATA
ALL_CURRENCIES = ["BTC", "ADA", "LINK", "LTC", "BNB", "ETH", "XRP", "DOGE"]

# TO BE USED IN TWITTER AND GOOGLE TRENDS SEARCH
KEYWORDS = ['bitcoin', 'crypto', 'cryptocurrency', 'dogecoin', 'ethereum', 'litecoin']

# SELECTED PROFILES IN TWITTER TO FOLLOW
SELECTED_TWITTER_PROFILES = [
    "VitalikButerin",
    "aantonop",
    "balajis",
    "AndreCronjeTech",
    "michael_saylor",
    "cz_binance",
    "dannyryan",
    "Bitcoin",
    "ethereum",
    "BTCTN",
    "binance",
    "coinbase",
    "SatoshiLite",
    "elonmusk",
    "jack"
]

# HISTORICAL TRAINING DATA
# START_DATE = '2019-07-22'
# END_DATE = '2021-07-24'
INTERVAL = '1m' # 1m, 5m, 15m, 1h, 2h, 4h, 6h, 8h, 1d, 3d, etc.
DAYS_BACK = 365 * 2 # 2 years back -> 365 * 2
FOLDER_TO_SAVE = 'data'

# REAL-TIME DATA
LATEST_DATA_LOOKBACK_MIN = 20

# Will be the common column in different datasets to merge on
MERGE_DATA_ON = 'exact_time'

# Feature generators test
FEATURE_GENERATORS = [TalippGenerator(EMA, input_column_names="BTCEUR_Close", period=5),
                      TalippGenerator(EMA, input_column_names="BTCEUR_Close", period=15),
                      TalippGenerator(EMA, input_column_names="BTCEUR_Close", period=30),
                      TalippGenerator(RSI, input_column_names="BTCEUR_Close", period=5),
                      TalippGenerator(RSI, input_column_names="BTCEUR_Close", period=15),
                      TalippGenerator(RSI, input_column_names="BTCEUR_Close", period=30)]