from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from munch import Munch
from util_py.security import handify
import math
import random

class TickManager():
    def __init__(self, main_trade) -> None:
        self.main_trade = main_trade

        self.symbol_req_map = {}
        self.req_symbol_map = {}

        self.symbol_datetime_map = {} # 最新的时间
        self.symbol_price_map = {} # 最新的成交价
        self.symbol_last_volume_map = {} # 最近的成交量

        self.symbol_ticks_map = {} # 当日历史ticks

        self.symbol_bid_map = {} # 当买一盘口
        self.symbol_ask_map = {} # 当卖一盘口
        self.symbol_order_book_map = {} # 集合买一和卖一

        self.symbol_pre_close_map = {} # 昨收
        self.symbol_volume_map = {} # 当日累计成交量
        self.symbol_quote_map = {} # 当天日行情

        self.symbol_rt_data_map = {} # 用于分时数据

    def bind(self, symbol, req_id):
        self.symbol_req_map[symbol] = req_id
        self.req_symbol_map[req_id] = symbol

    def update_time(self, req_id, timestamp):
        symbol = self.req_symbol_map.get(req_id)
        if not symbol:
            return
        
        self.symbol_datetime_map[symbol] = datetime.fromtimestamp(int(timestamp))
        self.update_tick(req_id)

    def update_pre_close(self, req_id, price):
        symbol = self.req_symbol_map.get(req_id)
        if not symbol:
            return
        
        self.symbol_pre_close_map[symbol] = price
        self.update_tick(req_id)

    def update_volume(self, req_id, volume):
        symbol = self.req_symbol_map.get(req_id)
        if not symbol:
            return
        
        self.symbol_volume_map[symbol] = float(volume)
        self.update_tick(req_id)

    def update_last_price(self, req_id, price):
        symbol = self.req_symbol_map.get(req_id)
        if not symbol:
            return
        
        self.symbol_price_map[symbol] = price
        self.update_tick(req_id)
        
    def update_last_volume(self, req_id, volume):
        symbol = self.req_symbol_map.get(req_id)
        if not symbol:
            return
        
        self.symbol_last_volume_map[symbol] = float(volume)
        self.update_tick(req_id)

    def update_bid(self, req_id, price):
        symbol = self.req_symbol_map.get(req_id)
        if not symbol:
            return
        
        self.symbol_bid_map[symbol] = price
        self.update_order_book(req_id)

    def update_ask(self, req_id, price):
        symbol = self.req_symbol_map.get(req_id)
        if not symbol:
            return
        
        self.symbol_ask_map[symbol] = price
        self.update_order_book(req_id)

    def update_order_book(self, req_id):
        symbol = self.req_symbol_map.get(req_id)
        if not symbol:
            return
        
        bid = self.symbol_bid_map.get(symbol)
        ask = self.symbol_ask_map.get(symbol)

        if bid is None or ask is None:
            return
        
        self.symbol_order_book_map[symbol] = Munch.fromDict({
            'symbol': symbol,
            'asks': [{'price': ask}],
            'bids': [{'price': bid }]
        })

        # print(f'self.symbol_order_book_map[{symbol}]', self.symbol_order_book_map[symbol])
        self.main_trade.on_order_book(self.symbol_order_book_map[symbol])
    
    def update_tick(self, req_id):
        symbol = self.req_symbol_map.get(req_id)
        if not symbol:
            return
        
        detail = self.main_trade.contract_manager.detail(symbol)
        if not detail:
            return
        
        datetime = self.symbol_datetime_map.get(symbol)
        last_price = self.symbol_price_map.get(symbol)
        last_volume = self.symbol_last_volume_map.get(symbol)
        pre_close = self.symbol_pre_close_map.get(symbol)
        volume = self.symbol_volume_map.get(symbol)
        
        if datetime is None or last_price is None or last_volume is None or pre_close is None or volume is None:
            return
        
        if self.symbol_ticks_map.get(symbol) is None:
            self.symbol_ticks_map[symbol] = pd.DataFrame()

        # 如果最后一个时间相同，则更新值，如果时间戳不同，则增加值
        new_tick = pd.DataFrame({
            'symbol': [symbol],
            'datetime': [datetime],
            'volume': [volume],
            'last_price': [last_price],
            'last_volume': [last_volume],
            'pre_close': [pre_close],
            'per_volume_random': 0
        })
        self.symbol_ticks_map[symbol] = pd.concat([self.symbol_ticks_map[symbol], new_tick], ignore_index=True)[:30]

        # 因为要更新新的tick，所以要标记过时
        del(self.symbol_datetime_map[symbol])
        del(self.symbol_price_map[symbol])
        del(self.symbol_last_volume_map[symbol])
        
        # 计算只能算法拆单量
        # lot_size = 1 if detail.stock_type == SecurityType.OPT else detail.info.lot_size # todo期权要检查
        lot_size = float(detail.lot_size)
        per_volume = handify(self.symbol_ticks_map[symbol]['last_volume'].mean(), lot_size)
        bias = 0.15
        hands = per_volume/lot_size
        part_hands = math.floor(hands*bias)
        random_hands = random.randint(-part_hands, part_hands)
        random_volume = random_hands * lot_size
        market_volume_random = per_volume + random_volume
        per_volume_random = handify(market_volume_random, lot_size)
        self.symbol_ticks_map[symbol].at[len(self.symbol_ticks_map[symbol])-1, 'per_volume_random'] = per_volume_random

        new_tick = self.symbol_ticks_map[symbol].iloc[-1]  
        self.main_trade.on_tick(new_tick)

        self.update_realtime(new_tick)


    def ticks(self, symbol):
        ticks = self.symbol_ticks_map.get(symbol)
        if ticks is None:
            return pd.DataFrame(columns=['symbol', 'datetime', 'volume', 'last_price', 'last_volume', 'pre_close'])
        
        return ticks
    
    def order_book(self, symbol):
        return self.symbol_order_book_map.get(symbol)
    
    def update_realtime(self, tick):
        symbol = tick.symbol
        volume = tick.volume
        # 计算分时数据
        next_time = (tick.datetime+timedelta(minutes=1)).replace(second=0, microsecond=0)
        time = next_time.strftime('%H:%M') # quote的是当前时间，而rt_data的时间应该是当前这一分钟的结束，也就是下一分钟整的开始 
        rt_data = self.symbol_rt_data_map.get(symbol)
        if not rt_data:
            self.symbol_rt_data_map[symbol] = rt_data = Munch.fromDict({'_volume': [('init_time', 0), (time, volume)]}) # 0元素是上一分钟，1元素是这一分钟
        else:
            # 如果当前这一分钟已经变化，则要更新这一分钟当前值和前一分钟的最后值；否则只更新当前一分钟值
            if not rt_data._volume[1][0] == time:
                rt_data._volume[0] = rt_data._volume[1]
            rt_data._volume[1] = (time, volume)
        rt_data.volume = float(rt_data._volume[1][1] - rt_data._volume[0][1])
        rt_data.datetime = next_time

    def rt_data(self, symbol):
        return self.symbol_rt_data_map.get(symbol)
