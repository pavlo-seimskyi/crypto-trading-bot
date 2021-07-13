import cbpro
import pandas as pd
import os
import credentials
import datetime
import time
from dateutil import parser
import config

client = cbpro.AuthenticatedClient(key=credentials.KEY,
                                   b64secret=credentials.SECRET,
                                   passphrase=credentials.PASSPHRASE)

# start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').isoformat()
# end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').isoformat()

os.makedirs(PATH, exist_ok=True)

samples_backwards = config.GRANULARITY * config.POINTS_PER_DAY * config.DAYS_BACK # min * hours * days
cycles = int(samples_backwards / 300)
step = pd.to_timedelta(300, 'min') # pd.to_timedelta(int(min_backwards / 300), 'min')
first_date = datetime.datetime.now() - pd.to_timedelta(min_backwards, 'min')

for currency_pair in config.CURRENCY_PAIRS:
  df = pd.DataFrame()

  for cycle in range(cycles) :
    if cycle == 0 :
      start_date = first_date
    else:
      start_date = parser.parse(start_date) + step

    end_date = start_date + step

    start_date = start_date.isoformat()
    end_date = end_date.isoformat()

    response = client.get_product_historic_rates(currency_pair, start=start_date, end=end_date, granularity=GRANULARITY)
    temp_df = pd.DataFrame(response).sort_values(by=0)
    df = df.append(temp_df, ignore_index=True)
    time.sleep(0.2)

  df = df.rename(columns={0:'time', 1:'low', 2:'high', 3:'open', 4:'close', 5:'volume'})

  df.to_csv(f'{config.FOLDER_TO_SAVE}/{currency_pair}.csv', index=False)
