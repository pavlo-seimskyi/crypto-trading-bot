# Trading Bot

## Data Scraper

### Description
Loads and saves data from several sources. Right now, the sources are:
- Binance API: Gets exchange rates between selected currencies in `config.ALL_CURRENCIES` and `config.CURRENCY_TO_SELL`.
- Twitter: 
  - Generic tweets: Tweets written by anyone that contain selected keywords from `config.KEYWORDS`. By default is restricte to verified users.
  - Tweets from selected profiles: Tweets written only by selected profiles from `config.SELECTED_TWITTER_PROFILES`.
- Google Trends: WIP.

## Feature Extractor

### Description
Module that generates new features from raw dataset.
Divided into two elements:

- Feature service: Orchestrates the feature generators.
- Feature generators: Objects that map data to a new feature. The idea is to have different ones depending the libraries, the data sources, etc.

### Key design principles
- Easy to add new features
- No need to reprocess the whole dataset when adding new data


