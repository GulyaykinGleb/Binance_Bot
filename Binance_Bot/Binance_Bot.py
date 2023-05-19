
import time
from binance import Client
from datetime import datetime as dt
apikey = ''
secret = ''
client = Client(apikey, secret)

print('Start')

print('Receive data')
# receiving data
symbol, interval, period = 'BTCUSDT', Client.KLINE_INTERVAL_12HOUR, '1 Jan, 2020'

ETH = [(float(candle[1])+float(candle[4]))/2 for candle in client.get_historical_klines('ETHUSDT', interval, period)]
BTC = [(float(candle[1])+float(candle[4]))/2 for candle in client.get_historical_klines(symbol , interval, period)]

diff_BTC = []
for i in range(len(BTC)-1):
    diff_BTC.append(BTC[i+1]/BTC[i] - 1)

print('Calculate coefficient')

# finding coefficient of dependency
def finding_coefficient(precision=3, k_max_range=10, k_min_range = None, diff_BTC=diff_BTC, ETH=ETH, step=None):
    k = k_max_range
    if step is None:
        step = 1
    if k_min_range is None:
        k_min_range = -k_max_range
    k_dct = {}
    while k >= k_min_range:
        ranges = []
        for i in range(len(diff_BTC)):
            alp = abs( ETH[i+1] - ETH[i] - k*diff_BTC[i]*ETH[i] ) / (ETH[i])
            ranges.append(alp) 
        avg_ranges = sum(ranges)/len(ranges)
        k_dct[avg_ranges] = k
        k -= 10**(-step)
    k = k_dct[min(k_dct.keys())]
    if step < precision:
        k = finding_coefficient(precision=precision, k_max_range=k+10**(-step), k_min_range=k-10**(-step), diff_BTC=diff_BTC, ETH=ETH, step=step+1)
    return k
k = finding_coefficient(precision=3)

print(f'coefficient = {k}\n')

# endless cycle
ETH_price = float(client.get_ticker(symbol='ETHUSDT')['lastPrice'])
BTC_price = float(client.get_ticker(symbol=symbol)['lastPrice'])

while True:
    new_ETH_price = float(client.get_ticker(symbol='ETHUSDT')['lastPrice'])
    new_BTC_price = float(client.get_ticker(symbol=symbol)['lastPrice'])
    close_time = dt.fromtimestamp(int(str(client.get_ticker(symbol='ETHUSDT')['closeTime'])[:10])) 
    diff_ETH_price_self =  (new_ETH_price - k*(new_BTC_price/BTC_price - 1)*ETH_price - ETH_price) / ETH_price * 100
    if diff_ETH_price_self >= 1:
        string = '%.2f' % diff_ETH_price_self
        print(f'the price has increased by {string} percent at {close_time}')
        ETH_price, BTC_price = new_ETH_price, new_BTC_price    
    else:
        print(f'Without changes {close_time}\n')
    time.sleep(600)

        
