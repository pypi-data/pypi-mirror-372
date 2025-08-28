import pandas as pd
import numpy as np
from munch import Munch
from .constant import *
from .ibapi.contract import *
import re
from .base_manager import BaseManager

class ContractManager(BaseManager):
    def __init__(self, main_trade) -> None:
        super().__init__(main_trade)

        self.symbol_detail_map = {}
        self.symbol_market_map = {}

    def contract(self, symbol):
        market = self.market(symbol)
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "STK"
        contract.currency = "USD" if market == Market.US else 'HKD'
        contract.exchange = market

        # 形式：'COIN230815C82000'
        result = re.match("(\w+)(\d{6})([C|P])(\d+)", symbol)
        if result: 
            contract.secType = "OPT"
            symbol, expiry, right, strike = result.groups()
            contract.symbol = symbol
            contract.lastTradeDateOrContractMonth = '20' + expiry
            contract.right = right
            contract.strike = int(strike)/1000

        return contract

    def update_detail(self, req_id, detail):
        symbol = self.get_symbol(req_id)
        if not symbol:
            return
        
        self.symbol_detail_map[symbol] = detail
        self.main_trade.on_contract_detail(detail)

    def detail(self, symbol):
        detail = self.symbol_detail_map.get(symbol)
        if not detail:
            self.main_trade.stock(symbol)
        return detail
    
    def set_market(self, symbol, market):
        self.symbol_market_map[symbol] = market
    
    def market(self, symbol):
        return self.symbol_market_map.get(symbol) or Market.US
    
    # 股票的symbol就是symbol，期权要加上三要素
    def c2s(self, contract):
        if contract.secType == SecurityType.OPT:
            return f'{contract.symbol}{contract.lastTradeDateOrContractMonth[2:]}{contract.right}{int(contract.strike*1000)}'
        return contract.symbol