from abc import ABC, abstractmethod
import os
import pandas as pd
from typing import Union, Tuple, Optional
#SysConfig.set_all_thread_daemon(True)
from ks_utility.logs import LoggerBase
from datetime import datetime
from .constant import *
from ks_trade_api.object import ContractData, MyAccountData, ErrorData, MyPositionData, MyTradeData, MyOrderData
from .constant import (
    Currency as KsCurrency,
    Exchange as KsExchange,
    Direction as KsDirection, 
    OrderType as ksOrderType, 
    Direction as KsDirection,
    Offset as KsOffset, 
    TimeInForce as KsTimeInForce,
    ErrorCode as KsErrorCode,
    Status as KsStatus,
    RET_OK, 
    RET_ERROR, 
    CHINA_TZ,
    
)
from ks_trade_api.utility import extract_vt_symbol
from ks_utility.numbers import to_decimal
import sys
from decimal import Decimal
import uuid
from ks_utility.datetimes import get_ts_int, get_dt_int
from ks_trade_api.object import ErrorData, ErrorCode
import traceback
from threading import Timer
import queue
import itertools
import math

RATES_INTERVAL = 30 # 30秒内30次请求，所以一旦超频，就睡眠30秒
TRIGGER_NUMS = 15

# 事前管理: 统计调用次数，保证不会违规
class VolumeAutoAdjust(LoggerBase):
    def __init__(self, gateway_name: str = ''):
        LoggerBase.__init__(self)
        
        self.gateway_name: str = gateway_name
        self.max_volume: int = math.inf
        self.max_money: Decimal = math.inf
    
    def __call__(self, func):
        def wrapper(self, *args, **kwargs):
            if not self.setting.get('volume_auto_adjust.max_money') is None:
                money = to_decimal(self.setting.get('volume_auto_adjust.max_money'))
                adjust_volume = money / 
                
            ret, data = func(*args, **kwargs)
            return ret, data
        return wrapper
