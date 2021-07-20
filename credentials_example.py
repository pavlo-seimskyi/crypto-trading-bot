# Rename this file to credentials.py after you've inserted the credentials
import config

# Can be created at https://public.sandbox.pro.coinbase.com/profile/api
if not config.SANDBOX :
    KEY = '######'
    SECRET = '######'
    PASSPHRASE = '######'

# Can be created at https://pro.coinbase.com/profile/api
elif config.SANDBOX :
    KEY = '######'
    SECRET = '######'
    PASSPHRASE = '######'
