from binance.client import Client
from secrets import api_key, api_secret
import time

client = Client(api_key, api_secret)

# pegar informações da conta
account = client.get_account()

# pegar informações do saldo
balance = account['balances']

for asset in balance:
    if float(asset['free']) > 0.0:
        print(f"{asset['asset']}: {asset['free']}")
