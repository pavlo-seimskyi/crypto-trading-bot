# Rename this file to credentials.py after you've inserted the credentials
import config_coinbase

# Can be created at https://public.sandbox.pro.coinbase.com/profile/api
if not config_coinbase.SANDBOX :
    KEY = '######'
    SECRET = '######'
    PASSPHRASE = '######'

# Can be created at https://pro.coinbase.com/profile/api
elif config_coinbase.SANDBOX :
    KEY = '######'
    SECRET = '######'
    PASSPHRASE = '######'
