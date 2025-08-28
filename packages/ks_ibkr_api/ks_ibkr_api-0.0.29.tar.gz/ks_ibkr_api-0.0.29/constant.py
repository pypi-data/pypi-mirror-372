class TrdEnv():
    """
    交易环境类型定义
    ..  py:class:: TrdEnv
     ..  py:attribute:: REAL
      真实环境
     ..  py:attribute:: SIMULATE
      模拟环境
    """
    REAL = "REAL"
    SIMULATE = "SIMULATE"

class Market():
    """Enum for market """
    
    ALL = 'ALL'
    US = 'SMART'  # 美股
    HK = 'SEHK'  # 港股
    CN = 'CN'  # A股
    SG = 'SG'  # 新加坡

class SecurityType():
    """Enum for sec_type """
    
    ALL = 'ALL'
    STK = 'STK'  # 股票
    OPT = 'OPT'  # 期权
    WAR = 'WAR'  # 窝轮
    IOPT = 'IOPT'  # 权证(牛熊证)
    FUT = 'FUT'  # 期货
    FOP = 'FOP'  # 期货期权
    CASH = 'CASH'  # 外汇

# 实时数据定阅类型
class SubType():
    TICKER = "TICKER"
    QUOTE = "QUOTE"

class OrderType():
    MKT = 'MKT'  # 市价单
    LMT = 'LMT'  # 限价单
    STP = 'STP'  # 止损单
    STP_LMT = 'STP_LMT'  # 止损限价单
    TRAIL = 'TRAIL'  # 跟踪止损单
    AM = 'AM'  # Auction Market ，竞价市价单
    AL = 'AL'  # Auction Limit ，竞价限价单

# 账户类型
class TrdAccType():
    NONE = 'N/A'     # 未知类型
    CASH = 'CASH'           # 现金账户
    MARGIN = 'MARGIN'       # 保证金账户

# 交易方向 (客户端下单只传Buy或Sell即可，SELL_SHORT / BUY_BACK 服务器可能会传回
class TrdSide():
    """
    交易方向类型定义(客户端下单只传Buy或Sell即可，SELL_SHORT / BUY_BACK 服务器可能会传回)
    ..  py:class:: TrdSide
     ..  py:attribute:: NONE
      未知
    ..  py:attribute:: BUY
      买
     ..  py:attribute:: SELL
      卖
     ..  py:attribute:: SELL_SHORT
      卖空
     ..  py:attribute:: BUY_BACK
      买回
    """
    NONE = "N/A"
    BUY = "BUY"
    SELL = "SELL"
    SELL_SHORT = "SELL_SHORT"
    BUY_BACK = "BUY_BACK"

# 期权类型
class OptionType():
    """
    期权类型
    ..  py:class:: OptionType
     ..  py:attribute:: ALL
      全部
     ..  py:attribute:: CALL
      涨
     ..  py:attribute:: PUT
      跌
    """
    ALL = "ALL"
    CALL = "CALL"
    PUT = "PUT"

class IndexOptionType():
    NONE = "N/A"                                                                 #未知
    NORMAL = "NORMAL"                                                            #正常
    SMALL = "SMALL"                                                              #小型

class OrderSide():
    Buy = 'BUY'
    Sell = 'SELL'

MaketMap = {
    '香港': Market.HK,
    '美国': Market.US
}

SecurityTypeMap = {
    '股票': SecurityType.STK,
    '期货': SecurityType.FUT,
    '期权': SecurityType.OPT
}

AccountTypeMap = {
    '现金': TrdAccType.CASH,
    '信用': TrdAccType.MARGIN
}

TradeSideMap = {
    '买': OrderSide.Buy,
    '卖': OrderSide.Sell
}

OptionTypeMap = {
    '看涨': OptionType.CALL,
    '看跌': OptionType.PUT
}
