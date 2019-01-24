import datetime, time
import pandas as pd

from .cache import RedisClient

from algorithms.data import DATA_MAPPER, MARKET_CODES, Data

from mined.settings import RAVEN_CONFIG
from algorithms.etc import KeystETCAlgorithm
from raven import Client
client = Client(RAVEN_CONFIG['dsn'])

MKT_DF_KEY = "MKTCAP_DF"
PRI_DF_KEY = "PRI_SELL_DF"
FRG_DF_KEY = "FRG_NET_DF"
INS_DF_KEY = "INS_NET_DF"

PRI_RECENT_DF = 'recent_pri_df'
FRG_RECENT_DF = 'recent_fir_df'
INS_RECENT_DF = 'recent_ins_df'

etc_algo = KeystETCAlgorithm()

class Reducers:

    def __init__(self, action_type, env_type):
        # action_type should be a str
        self.ACTION = action_type.lower()

        self.ENV = env_type.lower() # this is so you can run Node crawler app (Gobble) from local env
        # set ENV to local if you with to run on a local machine

        # define cache
        self.redis = RedisClient()
        self.pri_df = self.redis.get_df(PRI_DF_KEY)
        self.frg_df = self.redis.get_df(FRG_DF_KEY)
        self.ins_df = self.redis.get_df(INS_DF_KEY)
        self.mkt_cap_df = self.redis.get_df(MKT_DF_KEY)

    def has_reducer(self):
        # return True if reducer is defined, else False
        if hasattr(self, self.ACTION):
            return True
        else:
            return False

    def reduce(self):
        try:
            reducer = getattr(self, self.ACTION)
            # run reducer
            reducer() # pass in ENV to run locally if told to
        except:
            client.captureException()
            return False # return False on error

        # return True when function ran properly
        return True

    ##### Preprocessing Process #####
    def cache_buysell_mkt(self):
        success = False
        pri_rank_df = etc_algo.make_cache_data('pri')
        frg_rank_df = etc_algo.make_cache_data('frg')
        ins_rank_df = etc_algo.make_cache_data('ins')

        for task in [PRI_RECENT_DF, FRG_RECENT_DF, INS_RECENT_DF]:
            response = lf.redis.redis_client.exists(task)
            if response != False:
                self.redis.redis_client.delete(key)
                print('{} 이미 있음, 삭제하는 중...'.format(key))

        self.redis.set_df(PRI_RECENT_DF, pri_rank_df)
        self.redis.set_df(FRG_RECENT_DF, frg_rank_df)
        self.redis.set_df(INS_RECENT_DF, ins_rank_df)
        success = True
        return success
