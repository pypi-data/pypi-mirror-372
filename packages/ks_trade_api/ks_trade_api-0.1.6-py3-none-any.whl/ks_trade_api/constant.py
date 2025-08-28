"""
General constant enums used in the trading platform.
"""

from enum import Enum
import pytz
from datetime import time
from ks_utility.constants import Environment


class Direction(Enum):
    """
    Direction of order/trade/position.
    """
    LONG = "LONG"
    SHORT = "SHORT"
    NET = "NET"


class Offset(Enum):
    """
    Offset of order/trade.
    """
    NONE = ""
    OPEN = "OPEN"
    CLOSE = "CLOSE"
    CLOSETODAY = "CLOSETODAY"
    CLOSEYESTERDAY = "CLOSEYESTERDAY"


class Status(Enum):
    """
    Order status.
    """
    SUBMITTING = "SUBMITTING"
    NOTTRADED = "NOTTRADED"
    PARTTRADED = "PARTTRADED"
    ALLTRADED = "ALLTRADED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    UNKNOWN = "UNKNOWN"


class OrderType(Enum):
    """
    Order type.
    """
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    STOP = "STOP"
    FAK = "FAK"
    FOK = "FOK"
    RFQ = "RFQ"


class OptionType(Enum):
    """
    Option type.
    """
    CALL = "CALL"
    PUT = "PUT"

class Currency(Enum):
    """
    Currency.
    """
    USD = "USD"
    HKD = "HKD"
    CNY = "CNY"
    CAD = "CAD"

# 这个用来定义周期单位，跟Interval不同的是后者是附带数量的
class Period(Enum):
    MINUTE = 'MINUTE'
    HOUR = 'HOUR'
    DAILY = 'DAILY'
    WEEK = 'WEEK'
    MONTH = 'MONTH'

# todo!! 这里改动了周期，要看看有多少地方影响到，wrapper的周期配置肯定是受到影响
class Interval(Enum):
    """
    Interval of bar data.
    """
    MINUTE = "MINUTE"
    MINUTE5 = "MINUTE5"
    MINUTE15 = "MINUTE15"
    MINUTE30 = "MINUTE30"
    HOUR = "HOUR"
    DAILY = "DAILY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    TICK = "TICK"

class Adjustment(Enum):
    BACKWARD_ADJUSTMENT = 'BACKWARD_ADJUSTMENT' # 前复权
    FORWARD_ADJUSTMENT = 'FORWARD_ADJUSTMENT' # 后复权
    NONE = 'NONE' # 不复权

#=======================================

# 这里是把常量映射为字符串 'FUTURE' = > Enum('FUTURE)
def enum_map(enum):
    kv = {}
    for item in enum:
        kv[item.name] = item
        kv[item.value] = item
        kv[item] = item
        
    return kv

# {'zhangsan': 'human', 'lisi': 'human'} -> {'human': ['zhangsan', 'lisi']}
def invert_dict_list(mapping):
    from collections import defaultdict
    result = defaultdict(list)
    for k, v in mapping.items():
        result[v].append(k)
    return dict(result)



DATE_FMT = '%Y-%m-%d'
DATETIME_FMT = DATE_FMT + ' %H:%M:%S.%f' + '%z'

class SwitchStatus(Enum):
    """
    移仓换月的状态
    """
    UNRUN = "UNRUN"
    RUNNING = "RUNNING"
    DONE = "DONE"

tz = pytz.timezone('PRC')
SETTLE_START_TIME = time(15,5,0,0, tzinfo=tz)
SETTLE_END_TIME = time(17,30,0,0, tzinfo=tz) #todo


DAY_OPEN_TIME = time(9,0,0, tzinfo=tz)
DAY_CLOSE_TIME = time(15,0,0, tzinfo=tz)

NIGHT_OPEN_TIME = time(21,0,0,0, tzinfo=tz)
NIGHT_CLOSE_TIME = time(2,3,0,0, tzinfo=tz)

class AccountType(Enum):
    """
    Option type.
    """
    NONE = 'N/A'     # 未知类型
    CASH = 'CASH'           # 现金账户
    MARGIN = 'MARGIN'       # 保证金账户

class Product(Enum):
    """
    Product class.
    """
    EQUITY = "EQUITY"
    FUTURES = "FUTURES"
    OPTION = "OPTION"
    INDEX = "INDEX"
    FOREX = "FOREX"
    SPOT = "SPOT"
    ETF = "ETF"
    BOND = "BOND"
    WARRANT = "WARRANT"
    SPREAD = "SPREAD"
    FUND = "FUND"
    COIN = "COIN"
    MACRO = "MACRO"
    

class Exchange(Enum):
    """
    Exchange.
    """
    # Chinese
    CFFEX = "CFFEX"         # China Financial Futures Exchange
    SHFE = "SHFE"           # Shanghai Futures Exchange
    CZCE = "CZCE"           # Zhengzhou Commodity Exchange
    DCE = "DCE"             # Dalian Commodity Exchange
    INE = "INE"             # Shanghai International Energy Exchange
    GFEX = "GFEX"           # Guangzhou Futures Exchange
    SSE = "SSE"             # Shanghai Stock Exchange
    SZSE = "SZSE"           # Shenzhen Stock Exchange
    BSE = "BSE"             # Beijing Stock Exchange
    SGE = "SGE"             # Shanghai Gold Exchange
    WXE = "WXE"             # Wuxi Steel Exchange
    CFETS = "CFETS"         # CFETS Bond Market Maker Trading System
    XBOND = "XBOND"         # CFETS X-Bond Anonymous Trading System

    # alias
    CNSE = "CNSE"           # alias for SSE + SZSE 中国股票交易所
    CNFE = 'CNFE'           # alias for CFFEX + SHFE + CZCE + DCE 中国期货交易所
    USFE = 'USFE'           # 美国期货交易所
    GBFE = 'GBFE'           # 英国期货交易所
    JPFE = 'JPFE'           # 日本期货交易所
    SGFE = 'SGFE'           # 新加坡期货交易所
    MYFE = 'MYFE'           # 马来西亚期货交易所
    INDEX = 'INDEX'         # 指数

    # Global
    SMART = "SMART"         # Smart Router for US stocks
    NYSE = "NYSE"           # New York Stock Exchnage
    NASDAQ = "NASDAQ"       # Nasdaq Exchange
    NDE = 'NDE'             # 纳斯达克衍生品交易所
    ARCA = "ARCA"           # ARCA Exchange
    EDGEA = "EDGEA"         # Direct Edge Exchange
    ISLAND = "ISLAND"       # Nasdaq Island ECN
    BATS = "BATS"           # Bats Global Markets
    IEX = "IEX"             # The Investors Exchange
    AMEX = "AMEX"           # American Stock Exchange
    TSE = "TSE"             # Toronto Stock Exchange
    NYMEX = "NYMEX"         # New York Mercantile Exchange
    COMEX = "COMEX"         # COMEX of CME
    GLOBEX = "GLOBEX"       # Globex of CME
    IDEALPRO = "IDEALPRO"   # Forex ECN of Interactive Brokers
    CME = "CME"             # Chicago Mercantile Exchange
    ICE = "ICE"             # Intercontinental Exchange
    SEHK = "SEHK"           # Stock Exchange of Hong Kong
    HKFE = "HKFE"           # Hong Kong Futures Exchange
    SGX = "SGX"             # Singapore Global Exchange
    CBOT = "CBOT"            # Chicago Board of Trade
    CBOE = "CBOE"           # Chicago Board Options Exchange
    CFE = "CFE"             # CBOE Futures Exchange
    DME = "DME"             # Dubai Mercantile Exchange
    EUX = "EUX"             # Eurex Exchange 欧洲期货交易所
    PSE = "PSE"
    APEX = "APEX"           # Asia Pacific Exchange
    LME = "LME"             # London Metal Exchange
    BMD = "BMD"             # Bursa Malaysia Derivatives
    TFEX = 'TFEX'           # Thailand Futures Exchange 泰国的官方金融衍生品交易所
    TOCOM = "TOCOM"         # Tokyo Commodity Exchange
    OSE = "OSE"             # Osaka Exchange 期货与衍生品交易所
    EUNX = "EUNX"           # Euronext Exchange
    KRX = "KRX"             # Korean Exchange
    OTC = "OTC"             # OTC Product (Forex/CFD/Pink Sheet Equity)
    IBKRATS = "IBKRATS"     # Paper Trading Exchange of IB
    
    NYB = 'NYB'             # ICE美国(NYBOT纽约期货交易所)
    IPE = 'IPE'             # ICE欧洲(International Petroleum Exchange伦敦国际石油交易所)
    
    DF = 'DF'               # 德交所
    
    # 指数后缀
    GI = 'GI' # Global Index​（全球指数）
    FI = 'FI' # ​Country/Regional Index​（国家/区域指数）
    XI = 'XI' # ​China-Specific Index​（中国特指指数）
    MI = 'MI' #
    HI = 'HI' # 香港指数
    
    OF = 'OF' # 开放式基金

    TDX = 'TDX' # 通达信自定义板块
    EM = 'EM'  # 东方财富
    WIND = 'WIND' # Wind万德
    CSI = 'CSI' # 中证指数

    # Special Function
    LOCAL = "LOCAL"         # For local generated data
    KS = 'KS'               # 内部使用

    # Coins Exchanges
    BINANCE = 'BINANCE'
    DERIBIT = 'DERIBIT'
    
    # unknow
    UNKNOW = 'UNKNOW'

EXCHANGE_MAP = enum_map(Exchange)

SUB_EXCHANGE2EXCHANGE = {
    Exchange.SSE: Exchange.CNSE,
    Exchange.SZSE: Exchange.CNSE,
    Exchange.CZCE: Exchange.CNSE,
    Exchange.BSE: Exchange.CNSE,
    
    Exchange.DCE: Exchange.CNFE,
    Exchange.SHFE: Exchange.CNFE,
    Exchange.CZCE: Exchange.CNFE,
    Exchange.GFEX: Exchange.CNFE,
    Exchange.INE: Exchange.CNFE,
    Exchange.CFFEX: Exchange.CNFE,
    
    Exchange.NYB: Exchange.USFE,
    Exchange.NYMEX: Exchange.USFE,
    Exchange.COMEX: Exchange.USFE,
    Exchange.CME: Exchange.USFE,
    Exchange.CBOT: Exchange.USFE,
    
    Exchange.IPE: Exchange.GBFE,
    Exchange.LME: Exchange.GBFE,
    
    Exchange.SGX: Exchange.SGFE,
    
    Exchange.TOCOM: Exchange.JPFE,
    
    Exchange.BMD: Exchange.MYFE,
    
    Exchange.SEHK: Exchange.SEHK,
    
    Exchange.NASDAQ: Exchange.SMART,
    Exchange.NYSE: Exchange.SMART,
    Exchange.AMEX: Exchange.SMART,
    
    Exchange.OTC: Exchange.OTC,
    
    Exchange.GI: Exchange.INDEX,
    Exchange.FI: Exchange.INDEX,
    Exchange.XI: Exchange.INDEX,
    Exchange.MI: Exchange.INDEX,
    
    Exchange.CSI: Exchange.CNSE,
    Exchange.HI: Exchange.SEHK,

    Exchange.TDX: Exchange.CNSE,
    Exchange.EM: Exchange.CNSE,
    Exchange.WIND: Exchange.WIND,
    
    Exchange.OF: Exchange.CNSE, # 中国开放式基金
    
    Exchange.KS: Exchange.KS,
    
    Exchange.UNKNOW: Exchange.UNKNOW
}


EXCHANGES = [
    Exchange.CNSE, Exchange.CNFE, Exchange.USFE, Exchange.GBFE, Exchange.JPFE, 
    Exchange.SGFE, Exchange.MYFE, Exchange.INDEX
]

SUB_EXCHANGES = [x for x in list(Exchange) if x not in EXCHANGES]

EXCHANGE2SUB_EXCHANGES = invert_dict_list(SUB_EXCHANGE2EXCHANGE)


class SubExchange(Enum):
    """
    Exchange.
    """
    # Chinese
    US_NYSE = "US_NYSE"         # China Financial Futures Exchange
    US_NASDAQ = "US_NASDAQ"           # Shanghai Futures Exchange
    US_AMEX = "US_AMEX"           # Zhengzhou Commodity Exchange
    US_PINK = 'US_PINK'

    CN_SH = 'CN_SH'
    CN_SZ = 'CN_SZ'
    CN_BJ = 'CN_BJ'
    CN_STIB = 'CN_STIB' # 科创板？

    HK_MAINBOARD = 'HK_MAINBOARD'
    HK_GEMBOARD = 'HK_GEMBOARD'
    HK_HKEX = 'HK_HKEX'
    
    BINANCE_MAIN = 'BINANCE_MAIN'

    TDX = 'TDX' # 通达信自定义板块
    KS = 'KS'  # 内部使用

    # unknow
    UNKNOW = 'UNKNOW'


# U本位 币本位
class ContractType(Enum):
    U = 'U'
    B = 'B'

class TimeInForce(Enum):
    GTC = 'good_til_cancelled' # GTC = '立即成交剩余挂单至手工撤单(GTC)'
    GTD = 'good_til_day' # GTD = '立即成交剩余挂单至收盘(GTD)'
    FOK = 'fill_or_kill' # GTC = '全部成交或者撤单(FOK)'
    IOC = 'immediate_or_cancel' # IOC = '立即成交剩余撤销(IOC)'

class RetCode(Enum):
    OK = 'OK'
    ERROR = 'ERROR'
    ASYNC = 'ASYNC'

RET_OK = RetCode.OK
RET_ERROR = RetCode.ERROR
RET_ASYNC = RetCode.ASYNC

class TradeSide(Enum):
    BUY = 'BUY'
    SELL = 'SELL'
    BOTH = 'BOTH'

class SubscribeType(Enum):
    BOOK = 'BOOK'
    TICK = 'TICK'
    TRADE = 'TRADE'
    USER_TRADE = 'USER_TRADE'
    USER_ORDER = 'USER_ORDER'
    USER_POSITION = 'USER_POSITION'

    K_MINUTE = 'K_MINUTE'
    K_HOUR = 'K_HOUR'
    K_DAILY = 'K_DAILY'
    K_WEEK = 'K_WEEK'
    K_MONTH = 'K_MONTH'

    K_MINUTE5 = 'K_MINUTE5'
    K_MINUTE15 = 'K_MINUTE15'
    K_MINUTE30 = 'K_MINUTE30'

    # 指标
    I_MINUTE = 'I_MINUTE'
    I_DAILY = 'I_DAILY'
    
class MarketColumn(Enum):
    PRICE = 'PRICE'  # 实时价
    OPEN = 'OPEN'
    HIGH = 'HIGH'
    LOW = 'LOW'
    CLOSE = 'CLOSE'
    PRE_CLOSE = 'PRE_CLOSE'
    VOLUME = 'VOLUME'
    TURNOVER = 'TURNOVER'
    TURNOVER_RATE = 'TURNOVER_RATE'
    FLOATING_MARKET_SHARES = 'FLOATING_MARKET_SHARES' # 流通股本
    TOTAL_MARKET_SHARES = 'TOTAL_MARKET_SHARES' # 总股本
    FLOATING_MARKET_CAP = 'FLOATING_MARKET_CAP' # 流通市值
    TOTAL_MARKET_CAP = 'TOTAL_MARKET_CAP' # 总市值

class Indicator(Enum):
    TICK = 'TICK'
    BOOK = 'BOOK'
    
    BAR = 'BAR'
    
    BOLL = 'BOLL'
    MACD = 'MACD'

class IndicatorColumn(Enum):
    TICKLASTPRICE = 'TICKLASTPRICE' # 最新成交价
    
    BOOKBIDPRICE1 = 'BOOKBIDPRICE1' # 盘口买一价
    BOOKASKPRICE1 = 'BOOKASKPRICE1' # 盘口买一价
    
    BARCLOSE = 'BARCLOSE'
    
    BOLLUPPER = 'BOLLUPPER'
    BOLLMIDDLE = 'BOLLMIDDLE'
    BOLLLOWER = 'BOLLLOWER'
    
COLUMN2INDICATOR: dict = {
    IndicatorColumn.TICKLASTPRICE: Indicator.TICK,
    
    IndicatorColumn.BOOKBIDPRICE1: Indicator.BOOK,
    IndicatorColumn.BOOKASKPRICE1: Indicator.BOOK,
    
    IndicatorColumn.BARCLOSE: Indicator.BAR,
    
    IndicatorColumn.BOLLUPPER: Indicator.BOLL,
    IndicatorColumn.BOLLMIDDLE: Indicator.BOLL,
    IndicatorColumn.BOLLLOWER: Indicator.BOLL
}

class Timing(Enum):
    REALTIME = 'REALTIME'
    HISTORY = 'HISTORY'


class Currency(Enum):
    HKD = 'HKD'
    USD = 'USD'
    CNY = 'CNY'

class ErrorCode(Enum):
    RATE_LIMITS_EXCEEDED = 1
    SUBSCRIPTION_ERROR = 2
    BUY_POWER_EXCEEDED = 3 # 超过购买力
    LIQUIDITY_LACKED = 4 # 股票流动性不足

    # 100开始是交易框架的错误代码
    GATEWAY_NOT_FOUND = 100
    NOT_TRADING = 101 # trader被关停


OPTIONTYPE_MAP = enum_map(OptionType)
ACCOUNTTYPE_MAP = enum_map(AccountType)
ENVIRONMENT_MAP = enum_map(Environment)
CONTRACTTYPE_MAP = enum_map(ContractType)
DIRECTION_MAP = enum_map(Direction)
OFFSET_MAP = enum_map(Offset)
STATUS_MAP = enum_map(Status)
ORDER_TYPE_MAP = enum_map(OrderType)
PRODUCT_MAP = enum_map(Product)
TIMEINFORCE_MAP = enum_map(TimeInForce)
TRADE_SIDE_MAP = enum_map(TradeSide)

UTC_TZ = pytz.UTC
CHINA_TZ = pytz.timezone('PRC')       # 中国时区
US_EASTERN_TZ = pytz.timezone('US/Eastern')   # 美东时间

class TradingHours(Enum):
    PRE_MARKET = 'PRE_MARKET' # 盘前
    RTH = 'RTH' # 盘中
    AFTER_HOURS = 'AFTER_HOURS' # 盘后
    OVER_NIGHT = 'OVER_NIGHT' # 夜盘

class RthTime(Enum):
    # 美股时间
    US_EQUITY_PRE_MARKET_START = time(4, 0, 0, 0)
    US_EQUITY_PRE_MARKET_END = time(9, 30, 0, 0)
    US_EQUITY_RTH_START = time(9, 30, 0, 0)
    US_EQUITY_RTH_END = time(16, 0, 0, 0)
    US_EQUITY_AFTER_HOURS_START = time(16, 0, 0, 0)
    US_EQUITY_AFTER_HOURS_END = time(20, 0, 0, 0)
    US_EQUITY_OVER_NIGHT_START = time(20, 0, 0, 0)
    US_EQUITY_OVER_NIGHT_END = time(4, 0, 0, 0)

    # 港股时间
    HK_EQUITY_RTH_START = time(9, 30, 0, 0)
    HK_EQUITY_RTH_END = time(16, 0, 0, 0)

    # A股时间
    CN_EQUITY_RTH_START = time(9, 30, 0, 0)
    CN_EQUITY_RTH_END = time(15, 0, 0, 0)

class Right(Enum):
    CALL = 'CALL'
    PUT = 'PUT'

INTERVAL2SUBSCRIBE_TYPE = {
    Interval.TICK: SubscribeType.TRADE,
    
    Interval.MINUTE: SubscribeType.K_MINUTE,
    Interval.HOUR: SubscribeType.K_HOUR,
    Interval.DAILY: SubscribeType.K_DAILY,
    Interval.WEEK: SubscribeType.K_WEEK,
    Interval.MONTH: SubscribeType.K_MONTH,
    

    Interval.MINUTE5: SubscribeType.K_MINUTE5,
    Interval.MINUTE15: SubscribeType.K_MINUTE15,
    Interval.MINUTE30: SubscribeType.K_MINUTE30
}

SUBSCRIBE_TYPE2INTERVAL = {v:k for k,v in INTERVAL2SUBSCRIBE_TYPE.items()}

PERIOD2SECONDS = {
    Period.MINUTE: 60,
    Period.HOUR: 60 * 60,
    Period.DAILY: 60 * 60 * 24,
    Period.WEEK: 60 * 60 * 24 * 5
}

EXCHANGE2TIMEZONE = {
    Exchange.NASDAQ: US_EASTERN_TZ,
    Exchange.AMEX: US_EASTERN_TZ,
    Exchange.NYSE: US_EASTERN_TZ,
    Exchange.SMART: US_EASTERN_TZ,
    
    Exchange.SEHK: CHINA_TZ,
    
    Exchange.CNSE: CHINA_TZ,
    Exchange.SSE: CHINA_TZ,
    Exchange.SZSE: CHINA_TZ,
    Exchange.BSE: CHINA_TZ,
    
    Exchange.CNFE: CHINA_TZ,
    Exchange.DCE: CHINA_TZ,
    Exchange.SHFE: CHINA_TZ,
    Exchange.CZCE: CHINA_TZ,
    Exchange.GFEX: CHINA_TZ,
    Exchange.INE: CHINA_TZ,
    Exchange.CFFEX: CHINA_TZ,
    
    Exchange.USFE: US_EASTERN_TZ, # todo 美国不同交易所有时区差别，这里取了股票交易的通用时区西四区
    Exchange.NYB: pytz.timezone('America/New_York'),
    Exchange.NYMEX: pytz.timezone('America/New_York'),
    Exchange.COMEX: pytz.timezone('America/New_York'),
    Exchange.CME: pytz.timezone('America/Chicago'),
    Exchange.CBOT: pytz.timezone('America/Chicago'),
    
    Exchange.GBFE: pytz.timezone('Europe/London'),
    Exchange.IPE: pytz.timezone('Europe/London'),
    Exchange.LME: pytz.timezone('Europe/London'),
    
    Exchange.JPFE: pytz.timezone('Asia/Tokyo'),
    Exchange.TOCOM: pytz.timezone('Asia/Tokyo'),
    
    Exchange.SGFE: pytz.timezone('Asia/Singapore'),
    Exchange.SGX: pytz.timezone('Asia/Singapore'),
    
    Exchange.MYFE: pytz.timezone('Asia/Kuala_Lumpur'),
    Exchange.BMD: pytz.timezone('Asia/Kuala_Lumpur'),
    
    Exchange.BINANCE: CHINA_TZ,
    Exchange.TDX: CHINA_TZ,
    Exchange.KS: CHINA_TZ,
    Exchange.OTC: CHINA_TZ,
    
    Exchange.GI: UTC_TZ,
    Exchange.INDEX: UTC_TZ,
    
    Exchange.OF: CHINA_TZ,
    Exchange.WIND: UTC_TZ
    
}

class BrokerName(Enum):
    futu = 'futu'
    moomoo = 'moomoo'
    longport = 'longport'
    ibkr = 'ibkr'
    binance = 'binance'

class StrategyName(Enum):
    CTA_STRATEGY = 'CtaStrategy'
    TWAP_STRATEGY = 'TwapStrategy'
    VWAP_STRATEGY = 'VwapStrategy'
    ICEBERG_STRATEGY = 'IcebergStrategy'
    GRID_STRATEGY = 'GridStrategy'
    
    # todo! 这种策略就不应该存在，只有一种策略叫网格策略，以后再改吧
    OPTION_GRID_STRATEGY = 'OptionGridStrategy'
    

class PositionStrategy(Enum):
    BASE_POSITION_STRATEGY = 'BASE_POSITION_STRATEGY'
    GRID_POSITION_STRATEGY = 'GRID_POSITION_STRATEGY'

POSITION_STRATEGY_MAP = enum_map(PositionStrategy)

class ExecuteStrategy(Enum):
    BASE_EXECUTE_STRATEGY = 'BASE_EXECUTE_STRATEGY'
    CONDITION_EXECUTE_STRATEGY = 'CONDITION_EXECUTE_STRATEGY'
    OPTION_CONDITION_EXECUTE_STRATEGY = 'OPTION_CONDITION_EXECUTE_STRATEGY'

EXECUTE_STRATEGY_MAP = enum_map(ExecuteStrategy)

class PushStrategy(Enum):
    BASE_PUSH_STRATEGY = 'BASE_PUSH_STRATEGY'
    OPTION_PUSH_STRATEGY = 'OPTION_PUSH_STRATEGY'

PUSH_STRATEGY_MAP = enum_map(PushStrategy)

class TriggerType(Enum):
    LIMIT = 'LIMIT'
    MARKET = 'MARKET'
    BOLL = 'BOLL'

class StrategyApi(Enum):
    INIT = 'init'
    UPDATE = 'update'
    REMOVE = 'remove'
    STOP = 'stop'
    RESTART = 'restart'

    ON_INIT = 'on_init'
    ON_BOOK = 'on_book'
    ON_ERROR = 'on_error'
    ON_DEAL = 'on_deal'
    ON_STOP = 'on_stop'

    # 触发交易
    ON_TRIGGER = 'on_trigger'
    
class PushType(Enum):
    DINGDING = 'DINGDING'
    SMS = 'SMS'
    WHATSAPP = 'WHATSAPP'
    
EXCHANGE2CURRENCY = {
    Exchange.CNSE: Currency.CNY,
    Exchange.SSE: Currency.CNY,
    Exchange.SZSE: Currency.CNY,
    Exchange.BSE: Currency.CNY,
    
    Exchange.SEHK: Currency.HKD,
    
    Exchange.SMART: Currency.USD,
    Exchange.NASDAQ: Currency.USD,
    Exchange.AMEX: Currency.USD,
    Exchange.NYSE: Currency.USD
}
    