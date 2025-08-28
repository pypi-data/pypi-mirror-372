# todo 1. 对于查询的持仓，空的也要推送空的，否则orderplit无法回调.  这对于http请求很容易实现，但是如果是websocket回调，也许空的不会回调？例如ibk
# 初始化需要query_position把所有服务器持仓同步到本地，然后才能获取到持仓
# 参照longort和deribit的gateway，如果send_order是异步的（或者order_change是维保考场），那么order_change回调可能会早于send_order返回的orderid,需要处理好状态向前覆盖

from logging import DEBUG, INFO, WARNING, ERROR
from abc import ABC, abstractmethod
from datetime import datetime
from pandas import DataFrame
from typing import Union, Tuple, Optional, List
#SysConfig.set_all_thread_daemon(True)
from ks_utility.logs import LoggerBase
from ks_utility.dingdings import DingDing
from .constant import *
import traceback
from .object import (
    ContractData, MyAccountData, ErrorData, MyPositionData, MyTradeData, MyOrderData, MyBookData, 
    MyTickData, MyRawTickData, QuoteData, BarData
)
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
    Interval as KsInterval,
    SubscribeType,
    Adjustment as KsAdjustment,
    Product as KsProduct,
    RET_OK, 
    RET_ERROR, 
    CHINA_TZ,
    
)
from .utility import extract_vt_symbol
import sys
from decimal import Decimal

class BaseMarketApi(LoggerBase):
    @property
    @abstractmethod
    def gateway_name(self):
        """KS_LONGPORT"""
        pass

    def __init__(self, gateway_name: str, dd_secret=None, dd_token=None, setting: dict = {}):
        LoggerBase.__init__(self)

        self.gateway_name = gateway_name
        self.dd: Optional[DingDing] = None
        if dd_token:
            self.dd = DingDing(secret=dd_secret, token=dd_token) # todo 同样的token和sercret的dd，需要单例
            
        self.setting = setting
        self.is_test = setting.get('test', False)

    def connect(self):
        pass

    # 订阅tick，book等回调 
    def subscribe(self, vt_symbols: list[str], vt_subtype_list: list[SubscribeType], extended_time=True) -> tuple[RetCode, Optional[ErrorData]]:
        pass

    def on_book(self, book: MyBookData) -> None:
        pass

    def on_tick(self, tick: MyRawTickData) -> None:
        pass

    def on_bar_rt(self, bar: BarData) -> None:
        pass

    def on_error(self, error: ErrorData) -> None:
        pass

    def on_contract(self, tick: ContractData) -> None:
        pass

    def query_contract(self, vt_symbol: str) -> tuple[RetCode, ContractData]:
        pass

    # 获取账号信息
    @abstractmethod
    def query_book(self, vt_symbol: str) -> tuple[RetCode,  MyBookData]:
        pass

    def query_quotes(self, vt_symbols: list[str], df: bool = True) -> Union[RetCode, list[QuoteData]]:
        pass

    def query_ticks(self, vt_symbol: str) -> Union[RetCode, list[MyRawTickData]]:
        pass

    def query_history(
            self,
            vt_symbol: str,
            start: datetime,
            end: datetime,
            interval: KsInterval,
            adjustment: KsAdjustment,
            extended_time: bool = False,
            df: bool = True
    ) ->  tuple[RetCode, Union[list[BarData], DataFrame]]:
        """
        Query bar history data.
        """
        pass

    def query_history_n(
            self,
            vt_symbol: str,
            n: int,
            interval: KsInterval,
            adjustment: KsAdjustment,
            df: bool = True
        ) -> tuple[RetCode, Union[list[BarData], DataFrame]]:
        """
        Query bar history data.
        """
        pass

    def query_contracts(
            self,
            vt_symbols: Optional[List[str]] = None,
            exchanges: Optional[list[KsExchange]] = None,
            products: Optional[List[KsProduct]] = None,
            df: bool = True
        ) -> tuple[RetCode, Union[list[ContractData], DataFrame]]:
        pass
    
    def query_trading_days(self, exchange: KsExchange, start: str, end=str) -> DataFrame:
        pass

    def send_dd(self, msg: str='', title: str=f'问题预警'):
        if self.dd:
            my_msg =  f'  \n  【{self.gateway_name}网关】  \n'
            my_msg += f'{title}:  {msg}'
            my_title =  f'{self.gateway_name}{title}'
            self.dd.send(my_msg, my_title)

    def get_error(self, *args, **kvargs):
        method = sys._getframe(1).f_code.co_name
        code = None
        msg = None
        try:
            code = self.ERROR_CODE_MY2KS.get(kvargs.get('e').code)
            msg = kvargs.get('e').message or kvargs.get('e').msg
        except:
            msg = kvargs.get('e')
        error = ErrorData(
            code=code,
            msg = msg,
            method=method,
            args=args,
            kvargs=kvargs,
            traceback=traceback.format_exc(),
            gateway_name=self.gateway_name
        )
        self.log(error, tag=f'api_error.{method}', level=ERROR)
        return error

    # 关闭上下文连接
    def close(self) -> None:
        pass
        # self.quote_ctx.close()
        # self.trd_ctx.close()


        