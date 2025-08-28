# todo 1. 对于查询的持仓，空的也要推送空的，否则orderplit无法回调.  这对于http请求很容易实现，但是如果是websocket回调，也许空的不会回调？例如ibk
# todo 2. 持仓查询已经完成了direction过滤，order查询还没有经过参数过滤

import pandas as pd
from datetime import datetime
from typing import Union, Tuple, Optional
import itertools
from ks_trade_api.object import ContractData, MyAccountData, ErrorData, MyPositionData, MyTradeData, MyOrderData, MyOrderRequest, MySubscribeRequest
from ks_trade_api.constant import (
    Product as ksProduct,
    Currency as KsCurrency,
    Exchange as Exchange,
    Direction as KsDirection, 
    OrderType as ksOrderType, 
    Direction as KsDirection,
    SubscribeType as KsSubscribeType,
    Offset as KsOffset, 
    TimeInForce as KsTimeInForce,
    TradingHours as KsTradingHours,
    ErrorCode as KsErrorCode,
    Status as KsStatus,
    RetCode as KsRetCode,
    RET_OK as KS_RET_OK, 
    RET_ASYNC as KS_RET_ASYNC,
    RET_ERROR as KS_RET_ERROR, 
    CHINA_TZ,
    US_EASTERN_TZ
)
from .ib_api import IbApi
from dateutil.parser import parse
from ks_trade_api.base_trade_api import BaseTradeApi
from ks_trade_api.utility import extract_vt_symbol, extract_vt_orderid
import sys
from decimal import Decimal
import uuid
from logging import DEBUG, WARNING, ERROR
from .ib_api import CURRENCY_VT2IB, raw_symbol_ks2my, raw_symbol_my2ks

RATES_INTERVAL: int = 30

class OrderType():
    LMT = 'LMT'
    MKT = 'MKT'

class TrdSide():
    BUY = 'BUY'
    SELL = 'SELL'


SUBTYPE_KS2MY = {
    KsSubscribeType.USER_ORDER: KsSubscribeType.USER_ORDER,
    KsSubscribeType.USER_TRADE: KsSubscribeType.USER_TRADE,
    KsSubscribeType.USER_POSITION: KsSubscribeType.USER_POSITION,
}

MARKET_KS2MY = {
    Exchange.SEHK: 'HK',
    Exchange.SMART: 'US'
}

MARKET_MY2KS = { v:k for k,v in MARKET_KS2MY.items() }

def symbol_ks2my(vt_symbol: str):
    if not vt_symbol:
        return ''
    symbol, ks_exchange = extract_vt_symbol(vt_symbol)
    return f'{MARKET_KS2MY.get(ks_exchange)}.{symbol}'

ORDERTYPE_MY2KS = {
    OrderType.LMT: ksOrderType.LIMIT,
    OrderType.MKT: ksOrderType.MARKET
}

ORDERTYPE_KS2MY = {v:k for k,v in ORDERTYPE_MY2KS.items()}


SIDE_KS2MY = {
    f'{KsDirection.LONG.value},{KsOffset.OPEN.value}': TrdSide.BUY,
    f'{KsDirection.SHORT.value},{KsOffset.CLOSE.value}': TrdSide.SELL,
    f'{KsDirection.SHORT.value},{KsOffset.CLOSETODAY.value}': TrdSide.SELL,
    f'{KsDirection.SHORT.value},{KsOffset.CLOSEYESTERDAY.value}': TrdSide.SELL,

    f'{KsDirection.SHORT.value},{KsOffset.OPEN.value}': TrdSide.SELL,
    f'{KsDirection.LONG.value},{KsOffset.CLOSE.value}': TrdSide.BUY,
    f'{KsDirection.LONG.value},{KsOffset.CLOSETODAY.value}': TrdSide.BUY,
    f'{KsDirection.LONG.value},{KsOffset.CLOSEYESTERDAY.value}': TrdSide.BUY,
}

def side_ks2my(direction: KsDirection, offset: KsOffset):
    key = f'{direction.value},{offset.value}'
    return SIDE_KS2MY.get(key)

def sides_ks2my(directions: list[KsDirection], offsets: list[KsOffset]):
    sides_map = {}
    combinations = itertools.product(directions, offsets)
    for direction, offset in combinations:
        sides_map[side_ks2my(direction, offset)] = 1
    sides = list(sides_map.keys())
    return sides

def side_my2ks(side: TrdSide):
    # 为啥原来会是对的？
    if side == TrdSide.BUY:
        direction = KsDirection.LONG
        offset = KsOffset.OPEN
    else:
        direction = KsDirection.SHORT
        offset = KsOffset.CLOSE
    return direction, offset



# 定义一个自定义错误类
class MyError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message
        # futu没有错误代码。。只能用文字先替代
        if '购买力不足' in message:
            self.code = KsErrorCode.BUY_POWER_EXCEEDED
        elif '频率太高' in message:
            self.code = KsErrorCode.RATE_LIMITS_EXCEEDED

class KsIbkrApi(BaseTradeApi):
    gateway_name: str = "KS_IBKR"

    ERROR_CODE_MY2KS: dict = {
        KsErrorCode.BUY_POWER_EXCEEDED: KsErrorCode.BUY_POWER_EXCEEDED,
        KsErrorCode.RATE_LIMITS_EXCEEDED: KsErrorCode.RATE_LIMITS_EXCEEDED
    }

    def __init__(self, setting: dict):
        self.port = setting.get('port', 7497)
        self.client_id = setting.get('client_id', 666)
        dd_secret = setting.get('dd_secret')
        dd_token = setting.get('dd_token')
        gatway_name: str = setting.get('gateway_name', self.gateway_name)

        self.vt_orderid_acc_id_map: dict = {} # 记录订单的account，因为订单撤销需要账号
        
        super().__init__(gateway_name=gatway_name, dd_secret=dd_secret, dd_token=dd_token, setting=setting)

        self.positions = []
        self.query_position_params = {}
        
        self.init_handlers()



    # 初始化行回调和订单回调
    def init_handlers(self):
        self.ctx = IbApi(self, self.port, client_id = self.client_id)
    
    def on_contract(self, contract):
        pass   

    def on_positions(self, positions: list[MyPositionData]) -> None:
        pass
        

    # 订阅行情
    def subscribe(self, vt_symbols, vt_subtype_list, product: ksProduct = ksProduct.EQUITY, delay: bool = False, snapshot: bool = False, regulatory_snapshot: bool = False, extended_time=True) -> tuple[KsRetCode, Optional[ErrorData]]:
        for vt_symbol in vt_symbols:
            symbol, exchange = extract_vt_symbol(vt_symbol)
            req = MySubscribeRequest(symbol=symbol, exchange=exchange, types=vt_subtype_list, product=product, delay=delay, snapshot=snapshot, regulatory_snapshot=regulatory_snapshot)
            self.ctx.subscribe(req)

    def query_contract(self, vt_symbol: str) -> tuple[KsRetCode, ContractData]:
        try:
            self.ctx.query_contract(vt_symbol)
        except Exception as e:
            error = self.get_error(vt_symbol, e=e)
            self.send_dd(error.msg, f'合约查询错误')
            return KS_RET_ERROR, error
        
        return KS_RET_ASYNC, None
 
    
    # 下单
    # @RateLimitChecker(RATES_INTERVAL)
    def send_order(
            self, 
            vt_symbol: str,
            price: Decimal,
            volume: Decimal,
            type: ksOrderType = ksOrderType.LIMIT,
            direction: KsDirection = KsDirection.LONG,
            offset: KsOffset = KsOffset.OPEN,
            time_in_force: KsTimeInForce = KsTimeInForce.GTC,
            trading_hours: KsTradingHours = KsTradingHours.RTH,
            reference: str = '',
            product: ksProduct = ksProduct.EQUITY
    ) -> Tuple[KsRetCode, Union[str, ErrorData]]:
        symbol, exchange = extract_vt_symbol(vt_symbol)
        order_request: MyOrderRequest = MyOrderRequest(
            symbol=symbol,
            exchange=exchange,
            direction=direction,
            offset=offset,
            type=type,
            price=price,
            volume=volume,
            time_in_force=time_in_force,
            reference=reference,
            product=product
        )
        try:
            vt_orderid =self.ctx.send_order(order_request)

            self.log({
                'vt_symbol': vt_symbol,
                'direction': direction,
                'offset': offset,
                
                'symbol': symbol,
                'price': price,
                'volume': volume,
                'type': type,
                'direction': direction,
                'offset': offset,
                'time_in_force': time_in_force,
                'trading_hours': trading_hours,
                'reference': reference,
                'vt_orderid': vt_orderid
            })
            return KS_RET_OK, vt_orderid
        except Exception as e:
            error = self.get_error(params={
                'symbol': symbol,
                'price': price,
                'volume': volume,
                'type': type,
                'direction': direction,
                'offset': offset,
                'time_in_force': time_in_force,
                'trading_hours': trading_hours,
                'reference': reference
            }, e=e)
            return KS_RET_ERROR, error
        
    # My.add 直接向服务器请求合约数据
    # @RateLimitChecker(RATES_INTERVAL)
    def request_cancel_orders(
            self,
            vt_symbol: Optional[str] = None,
            direction: KsDirection = None,
            offset: KsOffset = None
        ) -> tuple[KsRetCode,  list[MyOrderData]]:
        ret = KS_RET_OK
        orders = []
        
        ret_query, open_orders = self.query_open_orders(vt_symbol=vt_symbol, direction=direction, offset=offset)
        if ret_query == KS_RET_ASYNC:
            # todo 异步尚未处理好
            return ret_query, open_orders
        
        if ret_query == KS_RET_OK:  
            for order in open_orders:
                order: MyOrderData
                ret_cancel, cancel_res = self.cancel_order(order.vt_orderid)
                # todo这里没有处理异步
                if ret_cancel == KS_RET_OK:
                    order.status = KsStatus.CANCELLED
                    orders.append(order)
                else:
                    ret = ret_cancel
                    orders = cancel_res
                    break
        else:
            ret = ret_query
            orders = open_orders
            

        return ret, orders

    # 撤单
    # @RateLimitChecker(RATES_INTERVAL)
    def cancel_order(self, vt_orderid: str) -> Tuple[KsRetCode, Optional[ErrorData]]:
        self.log({'vt_orderid': vt_orderid}, level=DEBUG)
        gateway_name, orderid = extract_vt_orderid(vt_orderid)
        try:
            self.ctx.cancel_order(orderid)
        except Exception as e:
            error = self.get_error(orderid, e=e)
            return KS_RET_ERROR, error

        return KS_RET_OK, vt_orderid

    # 获取账号信息
    def query_account(self, currencies: list[KsCurrency] = []) -> tuple[KsRetCode, Union[MyAccountData, ErrorData]]:
        # IB初始化会更新account，不需要主动查询 有更新自动推送，没有更新三分钟推送
        # self.ctx.reqAccountUpdates()
        return KS_RET_ASYNC, None
        accounts: dict[MyAccountData] = []

        try:
            data = self.ctx.accountSummary()
        except Exception as e:
            error = self.get_error(currency=currency, e=e)
            return KS_RET_ERROR, error
        
        # if len(data):
        #     balance = next((float(x.value) for x in data if x.tag == 'EquityWithLoanValue'), None)
        #     available = next((float(x.value) for x in data if x.tag == 'BuyingPower'), None)
        #     account: MyAccountData = MyAccountData(
        #         accountid='',
        #         balance=balance,
        #         frozen=0,
        #         currency=KsCurrency.HKD,
        #         gateway_name=self.gateway_name,
        #     )
        #     account.available = available
        #     accounts.append(account)

        return KS_RET_ASYNC, None
        

    def request_cancel_orders(
            self,
            vt_symbol: Optional[str] = None,
            direction: KsDirection = None,
            offset: KsOffset = None
        ) -> tuple[KsRetCode,  list[MyOrderData]]:
        ret = KS_RET_OK
        orders = []
        
        ret_query, open_orders = self.query_open_orders(vt_symbol=vt_symbol, direction=direction, offset=offset)
        if ret_query == KS_RET_ASYNC:
            # todo 异步尚未处理好
            return ret_query, open_orders
        
        if ret_query == KS_RET_OK:  
            for order in open_orders:
                order: MyOrderData
                ret_cancel, cancel_res = self.cancel_order(order.vt_orderid)
                # todo这里没有处理异步
                if ret_cancel == KS_RET_OK:
                    order.status = KsStatus.CANCELLED
                    orders.append(order)
                else:
                    ret = ret_cancel
                    orders = cancel_res
                    break
        else:
            ret = ret_query
            orders = open_orders
            

        return ret, orders


    # 获取持仓信息
    # @RateLimitChecker(RATES_INTERVAL)
    def query_position(self, vt_symbols=[], directions: list[KsDirection] = []):
        self.positions = []
        self.query_position_params = {'vt_symbols': vt_symbols, 'directions': directions}
        try:
            self.ctx.client.reqPositions()
        except Exception as e:
            error = self.get_error(vt_symbols, e=e)
            self.send_dd(error.msg, f'持仓查询错误')
            return KS_RET_ERROR, error
        
        return KS_RET_ASYNC, None
        
        positions = []
        if len(data):
            for position_data in data:
                # todo 这里持仓返回的exchange并不是smart，而是具体的，这导致跟我们配置的smart不符合，所以要重设为smart
                contract = position_data.contract
                contract.exchange = ''
                self.ctx.qualifyContracts(contract)
                
                if contract.secType == 'CASH':
                    symbol = contract.pair()
                else:
                    symbol = contract.symbol

                exchange = Exchange(contract.exchange)
                direction = KsDirection.NET
                position = MyPositionData(
                    symbol=symbol,
                    exchange=exchange,
                    direction=direction,
                    price=Decimal(str(position_data.avgCost)),
                    volume=Decimal(str(position_data.position)),
                    available=Decimal(str(position_data.position)),
                    gateway_name=self.gateway_name
                )
                positions.append(position)

        # 去除多查询的持仓
        if vt_symbols:
            positions = [x for x in positions if x.vt_symbol in vt_symbols]

        # 如果当天清仓再开仓，会有两条持仓记录，我们直接把0的记录删除
        positions = [x for x in positions if x.volume]
        

        # 补齐空持仓
        ret_ks_symbols = [x.vt_symbol for x in positions]
        lack_ks_symbols = [x for x in vt_symbols if not x in ret_ks_symbols]
        for lack_ks_symbol in lack_ks_symbols:
            if not lack_ks_symbol:
                continue
            symbol, exchange = extract_vt_symbol(lack_ks_symbol)
            lack_postion = MyPositionData(symbol=symbol, exchange=exchange, direction=KsDirection.NET, gateway_name=self.gateway_name)
            positions.append(lack_postion)

        return KS_RET_OK, positions
    
    def on_position_(self, position: MyPositionData) -> None:
        self.positions.append(position)

    def on_positions_end_(self) -> None:
        # 去除多查询的持仓
        vt_symbols: list[str] = self.query_position_params.get('vt_symbols', [])
        directions: list[KsDirection] = self.query_position_params.get('directions', [])
        if vt_symbols:
            self.positions = [x for x in self.positions if x.vt_symbol in vt_symbols]
        # 补齐空持仓
        ret_ks_symbols = [x.vt_symbol for x in self.positions]
        lack_ks_symbols = [x for x in vt_symbols if not x in ret_ks_symbols]
        for lack_ks_symbol in lack_ks_symbols:
            if not lack_ks_symbol:
                continue
            symbol, exchange = extract_vt_symbol(lack_ks_symbol)
            lack_postion = MyPositionData(symbol=symbol, exchange=exchange, direction=KsDirection.NET, gateway_name=self.gateway_name)
            self.positions.append(lack_postion)
        # 过滤direction
        if directions:
            self.positions = [x for x in self.positions if x.direction in directions]

        for position in self.positions:
            self.on_position(position)

        if self.setting.get('log.position', False):
            self.log(self.positions, tag="持仓回调", level=DEBUG)
    
        self.on_positions_end()

    # 获取今日订单
    def query_orders(self, 
        vt_symbol: Optional[str] = None, 
        direction: Optional[KsDirection] = None, 
        offset: Optional[KsOffset] = None,
        status: Optional[list[KsStatus]] = None,
        orderid: Optional[str] = None,
        reference: Optional[str] = None 
    ) -> tuple[KsRetCode, Union[list[MyOrderData], ErrorData]]:
        try:
            # 获取已完成和未完成订单
            self.ctx.client.reqOpenOrders()
            self.ctx.client.reqCompletedOrders(apiOnly=True) 
        except Exception as e:   
            error = self.get_error(vt_symbol, direction, offset, status, orderid, reference, e=e)
            return KS_RET_ERROR, error
        
        # orders = [self.order_data_my2ks(x) for x in orders]
        # # todo 过滤status
        # # 如果指定了代码则过滤代码
        # if vt_symbol:
        #     orders = [x for x in orders if x.vt_symbol == vt_symbol]
        # if direction:
        #     orders = [x for x in orders if x.direction == direction]
        # if direction:
        #     orders = [x for x in orders if x.offset == offset]
        # if direction:
        #     orders = [x for x in orders if x.status in status]
        # if orderid:
        #     orders = [x for x in orders if x.orderid == orderid]
        # if reference:
        #     orders = [x for x in orders if x.reference == reference]

        return KS_RET_ASYNC, None

        
    # 获取今日订单 # todo get_orders没有实现
    def query_open_orders(self, 
            vt_symbol: Optional[str]=None, 
            direction: Optional[KsDirection] = None, 
            offset: Optional[KsOffset] = None,
            status: Optional[list[KsStatus]] = None,
            orderid: Optional[str] = None,
            reference: Optional[str] = None
    ) -> tuple[KsRetCode, Union[list[MyOrderData], ErrorData]]:
        try:
            # 获取未完成订单
            self.ctx.client.reqOpenOrders()
        except Exception as e:   
            error = self.get_error(vt_symbol, direction, offset, status, orderid, reference, e=e)
            return KS_RET_ERROR, error
        
        # orders = [self.order_data_my2ks(x) for x in orders]
        # # todo 过滤status
        # # 如果指定了代码则过滤代码
        # if vt_symbol:
        #     orders = [x for x in orders if x.vt_symbol == vt_symbol]
        # if direction:
        #     orders = [x for x in orders if x.direction == direction]
        # if direction:
        #     orders = [x for x in orders if x.offset == offset]
        # if direction:
        #     orders = [x for x in orders if x.status in status]
        # if orderid:
        #     orders = [x for x in orders if x.orderid == orderid]
        # if reference:
        #     orders = [x for x in orders if x.reference == reference]

        return KS_RET_ASYNC, None


    def close(self):
        self.log('ibkr connection closed!')
        self.ctx.close()


        