#!/bin/bash

# echo "$USER"

# Enter the copied repo folder in Projects
# cd Projects/correct-ltv-automation

# Remove the environment folder if exists
if [ -d "trading-bot-env" ];
  then   rm -rf trading-bot-env
fi

# Install and activate virtual environment and packages
python -m pip install virtualenvwrapper
virtualenv --python=python3.8 trading-bot-env
source trading-bot-env/Scripts/activate
source trading-bot-env/bin/activate
python -m pip install -r requirements.txt

# # Copy the config file with private credentials
# cp /home/pavlo_seimskyi/ltv-automation/creds.py credentials/creds.py
# cp /home/pavlo_seimskyi/ltv-automation/client_secret_file.json credentials/client_secret_file.json
# cp /home/pavlo_seimskyi/ltv-automation/config.py src/config.py
#
# # And pickle file + make readable for everyone
# sudo cp /home/pavlo_seimskyi/ltv-automation/token_sheets_v4.pickle token_sheets_v4.pickle

# Give permissions to the file to everyone
# sudo chmod 755 token_sheets_v4.pickle

# Give permissions to the file only to jenkins
# sudo chown jenkins:admin token_sheets_v4.pickle

# Define the command to be run according to passed options and arguments
CMD="python -m src"

echo "Executing the following command:"
echo "${CMD}"
eval ${CMD}
