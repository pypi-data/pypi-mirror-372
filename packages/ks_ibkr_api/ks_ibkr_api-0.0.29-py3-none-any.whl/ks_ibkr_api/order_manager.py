from datetime import datetime
import pandas as pd
import numpy as np
from munch import Munch

from .base_manager import BaseManager

class OrderManager(BaseManager):
    def __init__(self, main_trade) -> None:
        super().__init__(main_trade)

        self.symbol_open_order_map = {}

        self.order_id_symbol_map = {}

        self.symbol_deal_map = {}

    def add_open_order(self, data):
        symbol = data.symbol
        if not self.symbol_open_order_map.get(symbol):
            self.symbol_open_order_map[symbol] = []
        
        self.order_id_symbol_map[data.orderId] = symbol

        # 先删除再添加，相当于更新
        self.symbol_open_order_map[symbol] = list(filter(lambda x: not x.orderId == data.orderId, self.symbol_open_order_map[symbol])) 
        self.symbol_open_order_map[symbol].append(data)

        self.main_trade.on_order_detail(data)

    def remove_open_order(self, order_id):
        symbol = self.order_id_symbol_map.get(order_id)
        if not symbol:
            return
        
        if self.symbol_open_order_map[symbol]:
            self.symbol_open_order_map[symbol] = list(filter(lambda x: not x.orderId == order_id, self.symbol_open_order_map[symbol]))

    def open_orders(self, symbol):
        return self.symbol_open_order_map.get(symbol) or []
    
    def add_deal(self, data):
        symbol = data.symbol
        if not self.symbol_deal_map.get(symbol):
            self.symbol_deal_map[symbol] = []

        deal = Munch.fromDict({
            'orderId': data.orderId,
            'symbol': symbol,
            'qty': data.qty,
            'datetime': data.datetime
        })

        self.symbol_deal_map[symbol].append(deal)

        self.main_trade.on_deal(deal)

    def deal(self, symbol):
        return self.symbol_deal_map.get(symbol)