# todo 1. 对于查询的持仓，空的也要推送空的，否则orderplit无法回调.  这对于http请求很容易实现，但是如果是websocket回调，也许空的不会回调？例如ibk
# 初始化需要query_position把所有服务器持仓同步到本地，然后才能获取到持仓
# 参照longort和deribit的gateway，如果send_order是异步的（或者order_change是维保考场），那么order_change回调可能会早于send_order返回的orderid,需要处理好状态向前覆盖。每个实例要实现order_id_status_map的状态记录

from logging import DEBUG, INFO, WARNING, ERROR
from abc import ABC, abstractmethod
from typing import Union, Tuple, Optional
from ks_utility.logs import LoggerBase
from ks_utility.dingdings import DingDing
from datetime import datetime
from .constant import *
import traceback
import itertools
from .object import ContractData, MyAccountData, ErrorData, MyPositionData, MyTradeData, MyOrderData, MyMarginRateData
from .constant import (
    Currency as KsCurrency,
    Exchange as KsExchange,
    Direction as KsDirection, 
    OrderType as ksOrderType, 
    Direction as KsDirection,
    Offset as KsOffset, 
    TimeInForce as KsTimeInForce,
    TradingHours as KsTradingHours,
    ErrorCode as KsErrorCode,
    Status as KsStatus,
    SubscribeType,
    RetCode,
    RET_OK, 
    RET_ERROR, 
    CHINA_TZ,
    
)
from .utility import extract_vt_symbol
import sys
from decimal import Decimal
import uuid

class BaseTradeApi(LoggerBase):
    @property
    @abstractmethod
    def gateway_name(self):
        """KS_LONGPORT"""
        pass

    def __init__(self, gateway_name:str, dd_secret=None, dd_token=None, **kwargs):
        LoggerBase.__init__(self)
        
        self.log('#' * 60, tag=f'{gateway_name} init')

        self.setting = kwargs.get('setting', {})


        self.gateway_name = gateway_name

        self.dd: Optional[DingDing] = None
        if dd_token:
            self.dd = DingDing(secret=dd_secret, token=dd_token) #  同样的token和sercret的dd，需要单例

    # 默认要订阅订单，成交，持仓回调，保证在网关连接之后就能获取到订单等回执了。测试用例需要用到 todo!存在优化空间，不是每个策略都需要订阅trade
    def connect(self):
        self.subscribe(vt_symbols=[], vt_subtype_list=[SubscribeType.USER_ORDER, SubscribeType.USER_TRADE, SubscribeType.USER_POSITION])

    # 下单
    @abstractmethod
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
            profit_price: Decimal = None,
            loss_price: Decimal = None,
            reference: str = '',
            product: Product = None
    ) -> Tuple[RetCode, Union[str, ErrorData]]:
        self.log({
            'vt_symbol': vt_symbol,
            'price': price,
            'volume': volume,
            'type': type,
            'direction': direction,
            'offset': offset,
            'time_in_force': time_in_force,
            'reference': reference
        }, level=DEBUG)

    # 撤单
    @abstractmethod
    def cancel_order(self, order_id: str) -> Tuple[RetCode, Optional[ErrorData]]:
        self.log({'order_id': order_id}, level=DEBUG)

    # 获取账号信息
    @abstractmethod
    def query_account(self, currencies: list[KsCurrency] = []) -> tuple[RetCode, Union[MyAccountData, ErrorData]]:
        pass
    
    # 获取保证金信息
    def query_margin_rate(self, vt_symbol: str) -> tuple[RetCode, Union[MyMarginRateData, ErrorData]]:
        self.log('query_margin_rate默认返回空')
        symbol, exchange = extract_vt_symbol(vt_symbol)
        return RET_OK, MyMarginRateData(
            gateway_name=self.gateway_name,
            symbol=symbol,
            exchange=exchange,
            long_margin_ratio_by_money=1,
            long_margin_ratio_by_volume=0,
            short_margin_ratio_by_money=1,
            short_margin_ratio_by_volume=0
        )


    # 获取持仓信息
    @abstractmethod
    def query_position(self, vt_symbols=[], directions: list[KsDirection] = []):
        pass
    
    # 获取今日订单
    @abstractmethod
    def query_orders(self, 
        vt_symbol: Optional[str] = None, 
        direction: Optional[KsDirection] = None, 
        offset: Optional[KsOffset] = None,
        status: Optional[list[KsStatus]] = None,
        orderid: Optional[str] = None,
        reference: Optional[str] = None 
    ) -> tuple[RetCode, Union[list[MyOrderData], ErrorData]]:
        pass
    
    # 订阅订单，成交和持仓回调
    def subscribe(self, vt_symbols: list[str], vt_subtype_list: list[SubscribeType], extended_time=True) -> tuple[RetCode, Optional[ErrorData]]:
        pass
    
    def on_order(self, order: MyOrderData) -> None:
        pass

    def on_trade(self, order: MyTradeData) -> None:
        pass
    
    def on_account(self, account: MyAccountData) -> None:
        pass
    
    def on_margin_rate(self, margin_rate: MyMarginRateData) -> None:
        pass

    def on_position(self, position: MyPositionData) -> None:
        pass

    def on_positions(self, positions: list[MyPositionData]) -> None:
        pass

    def on_orders_end(self) -> None:
        pass

    def on_positions_end(self) -> None:
        pass

    def on_accounts_end(self) -> None:
        pass
    
    def on_margin_rate_end(self) -> None:
        pass

    def on_error(self, error: ErrorData) -> None:
        pass

    def send_dd(self, msg: str='', title: str=f'问题预警'):
        if self.dd:
            my_msg =  f'  \n  【{self.gateway_name}网关】  \n'
            my_msg += f'{title}:  {msg}'
            my_title =  f'{self.gateway_name}{title}'
            self.dd.send(my_msg, my_title)

    @abstractmethod
    def ERROR_CODE_MY2KS() -> dict:
        pass

    def get_error(self, *args, **kvargs):
        method = sys._getframe(1).f_code.co_name
        code = None
        msg = None
        try:
            code = self.ERROR_CODE_MY2KS.get(kvargs.get('e').code)
            msg = kvargs.get('e').message
        except:
            msg = str(kvargs.get('e'))
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


        