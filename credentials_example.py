# Rename this file to credentials.py after you've inserted the credentials
import coinbase_config

# Can be created at https://public.sandbox.pro.coinbase.com/profile/api
if not coinbase_config.SANDBOX :
    KEY = '######'
    SECRET = '######'
    PASSPHRASE = '######'

# Can be created at https://pro.coinbase.com/profile/api
elif coinbase_config.SANDBOX :
    KEY = '######'
    SECRET = '######'
    PASSPHRASE = '######'
