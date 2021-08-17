import datetime as dt

# TO TRADE
CURRENCY_TO_BUY = 'BTC'
CURRENCY_TO_SELL = 'EUR'
SPEND_PER_TRADE = 10.0

# SAVING THE DATA
ALL_CURRENCIES = ["BTC", "ETH", "BNB", "ADA", "XRP", "DOGE", "LINK", "LTC"]
KEYWORDS = ['bitcoin', 'crypto', 'cryptocurrency', 'dogecoin', 'ethereum', 'litecoin']

# HISTORICAL TRAINING DATA
START_DATE = '2019-06-01'
END_DATE = '2021-07-20'
INTERVAL = '1m' # 1m, 5m, 15m, 1h, 2h, 4h, 6h, 8h, 1d, 3d, etc.
DAYS_BACK = 2 # 365*2 # 2 years back
FOLDER_TO_SAVE = 'SavingTest'

# REAL TIME DATA
LATEST_DATA_LOOKBACK_MIN = 10