'''
Mined.

 ʕ•ﻌ•ʔ     ʕ•ﻌ•ʔ
( >  <) ♡ (>  < )
 u   u     u   u

feat. peepee
with love...
'''
import requests
import redis
import pandas as pd

from cryptography.fernet import Fernet
from mined.crypt_key import KEY

cipher_suite = Fernet(KEY)
cache_ip = b'gAAAAABbY9rCK6aXKuhZKupM3IpY5nhXakD2ID8V5RhNwm2ZqUR225eTc5HFQXJgmlr_fZG9GnMjJ6wFVAdlgWxZoJ2NQWb1jA=='
IP = cipher_suite.decrypt(cache_ip).decode()

cache_pw = b'gAAAAABbY9rwNjWChyC-LgHSh64oczJaJqf67T8lcceZ93Bda4v-1AG8xCU7zoLIyArDwfaTLpm4fQuBdJpyhASfZLABdfhKTsKH14WPj48HvjObgc9jltGLWFNWkHBMbmCWzq8J9G64jC-gkcrXz2hGOZ-rFewWbeuMMeYSJ4u_LIxFBfUREl4='
PW = cipher_suite.decrypt(cache_pw).decode()

DATA_MAPPER = {
    'tickers': 'TICKERS',
    'ohlcv': '_OHLCV'
}

class Data:

    def __init__(self):
        print('Connecting to cache server (Redis) on Gobble server')
        self.redis_client = redis.StrictRedis(host=IP,
                                              port=6379,
                                              password=PW)
        self.tickers = None

    def set_keys(self):
        self.keys = self.redis_client.keys()

    def set_tickers(self):
        tickers_key = DATA_MAPPER['tickers']
        response = self.redis_client.lrange(tickers_key, 0, -1)
        response = list(map(lambda x: x.decode('utf-8'), response))
        self.tickers = response

    def get_ohlcv(self, ticker):
        if self.tickers == None:
            self.set_tickers()
        # if ticker in self.tickers:
