from ks_trade_api.utility import get_trading_hours
from datetime import time
from ks_trade_api.constant import TradingHours

pre_market_time = time(9,29,59,999)
rth_time = time(15,59,59,999)
after_hours_time = time(19,59,59,999)
over_night_time1 = time(23,59,59,999)
over_night_time2 = time(3,59,59,999)

assert(get_trading_hours(pre_market_time) == TradingHours.PRE_MARKET)
assert(get_trading_hours(rth_time) == TradingHours.RTH)
assert(get_trading_hours(after_hours_time) == TradingHours.AFTER_HOURS)
assert(get_trading_hours(over_night_time1) == TradingHours.OVER_NIGHT)
assert(get_trading_hours(over_night_time2) == TradingHours.OVER_NIGHT)