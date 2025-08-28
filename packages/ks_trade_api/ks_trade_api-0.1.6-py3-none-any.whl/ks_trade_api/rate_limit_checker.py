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
import sys
from decimal import Decimal
import uuid
from ks_utility.datetimes import get_ts_int, get_dt_int
from ks_trade_api.object import ErrorData, ErrorCode
import traceback
from threading import Timer
import queue
import itertools

RATES_INTERVAL = 30 # 30秒内30次请求，所以一旦超频，就睡眠30秒
TRIGGER_NUMS = 15

# 事前管理: 统计调用次数，保证不会违规
class RateLimitCheckerBefore(LoggerBase):
    def __init__(self, rate_interval: int = RATES_INTERVAL, trigger_nums: int = TRIGGER_NUMS, gateway_name: str = ''):
        LoggerBase.__init__(self)
        
        self.gateway_name: str = gateway_name
        self.rate_interval: int = rate_interval
        self.trigger_nums: int = trigger_nums
        self.acc_nums = 0 # 周期内触发的累计次数
        self.ts_int = get_ts_int(interval=self.rate_interval)
    
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            new_ts_int = get_ts_int(interval=self.rate_interval)
            if new_ts_int > self.ts_int:
                self.ts_int = new_ts_int
                self.acc_nums = 0

            if self.acc_nums >= self.trigger_nums:
                next_dt = datetime.fromtimestamp(self.ts_int + self.rate_interval)
                error = ErrorData(
                    code=ErrorCode.RATE_LIMITS_EXCEEDED,
                    msg = f'{func.__name__}请求失败。每{self.rate_interval}秒允许请求{self.trigger_nums}次。将于{next_dt}恢复请求',
                    method=func.__name__,
                    args=args,
                    kvargs=kwargs,
                    traceback='',
                    gateway_name=self.gateway_name
                )
                
                self.log(error)
                return RET_ERROR, error
            self.acc_nums += 1

            # print(datetime.fromtimestamp(self.ts_int), self.acc_nums)
            
            ret, data = func(*args, **kwargs)
            self.last_error_time = None

            return ret, data
        return wrapper

# 事后管理：发生超频错误之后，强制休息
class RateLimitCheckerAfter(LoggerBase):
    def __init__(self, rate_interval = RATES_INTERVAL):
        LoggerBase.__init__(self)
        
        self.rate_interval: int = rate_interval
        self.last_error_time: Optional[datetime] = None
        self.last_error_data: Optional[ErrorData] = None
    
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            diff_seconds = -1
            if self.last_error_time:
                now = datetime.now()
                interval_seconds = (now - self.last_error_time).seconds
                diff_seconds = self.rate_interval - interval_seconds
            if diff_seconds >= 0:
                self.log({'function_name': func.__name__, 'now': now, 'self.last_error_time': self.last_error_time}, tag=f'触发API超频，请求截断。{diff_seconds}秒后恢复访问')
                return RET_ERROR, self.last_error_data
            
            ret, data = func(*args, **kwargs)
            self.last_error_time = None

            if ret == RET_ERROR:
                if data.code == KsErrorCode.RATE_LIMITS_EXCEEDED:
                    self.last_error_time = datetime.now()
                    self.last_error_data = data
                    args[0].send_dd(f'{data.msg}', title=f'超频请求提示')

            return ret, data
        return wrapper
    
# 每interval秒请求1次，所以把一秒内的请求合并再一起请求。 todo 目前仅支持query_positions调用
class RateLimitBatchSender(LoggerBase):
    def __init__(self, interval: int = 1, gateway_name: str = ''):
        LoggerBase.__init__(self)
        
        self.gateway_name: str = gateway_name
        self.interval: int = interval
        self.args = ()
        self.kwargs = {}

        self.inited = False
        self.queque = queue.Queue()
    
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            
            self.func = func
            self.args = args
            self.kwargs = kwargs

            vt_symbols = kwargs.get('vt_symbols', [])
            self.queque.put(vt_symbols)
            if not self.inited:
                self.inited = True
                Timer(self.interval, self.batch_send).start()

            
            return RET_ASYNC, None
        return wrapper
    
    def batch_send(self):
        if not self.queque.empty():
            # 获取所有数据
            vt_symbols = []
            while not self.queque.empty():  # 队列非空时获取数据
                vt_symbols.append(self.queque.get())
            if [] in vt_symbols:
                vt_symbols = []
            else:
                vt_symbols = list(set(itertools.chain(*vt_symbols)))

            self.kwargs['vt_symbols'] = vt_symbols
            ret, positions = self.func(*self.args, **self.kwargs)
            if ret == RET_OK:
                trade_api = self.args[0]
                for position in positions:
                    trade_api.on_position(position)
                trade_api.on_positions_end()
                
        Timer(self.interval, self.batch_send).start()