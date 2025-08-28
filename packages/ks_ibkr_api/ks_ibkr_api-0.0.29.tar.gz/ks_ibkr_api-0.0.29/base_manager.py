from datetime import datetime
import pandas as pd
import numpy as np
from munch import Munch

REQ_ID = 9999

class BaseManager():
    # @staticmethod
    # def id():
    #     global req_id
    #     req_id += 1
    #     return req_id
    
    def __init__(self, main_trade) -> None:
        self.main_trade = main_trade

        self.symbol_req_map = {}
        self.req_symbol_map = {}

    def next_id(self, symbol):
        global REQ_ID
        REQ_ID += 1

        self.symbol_req_map[symbol] = REQ_ID
        self.req_symbol_map[REQ_ID] = symbol

        return REQ_ID
    
    def get_symbol(self, req_id):
        return self.req_symbol_map.get(req_id)

    