# Trading Bot

## Feature Extractor

### Description
Module that generates new features from raw dataset.
Divided into two elements:

- Feature service: Orchestrates the feature generators.
- Feature generators: Objects that map data to a new feature. The idea is to have different ones depending the libraries, the data sources, etc.

### Key design principles
- Easy to add new features
- No need to reprocess the whole dataset when adding new data
