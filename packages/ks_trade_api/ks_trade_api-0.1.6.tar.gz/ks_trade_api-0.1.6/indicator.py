import numpy as np
from decimal import Decimal

def boll(arr: list, period=20, times=2):
    # BOLL指标参数

    # 只计算最后一个 BOLL 值
    last_window = arr[-period:]  # 取最后period个数据
    mid = np.mean(last_window)  # 中轨线：均值
    std_dev = np.std(last_window, ddof=0)  # 总体标准差，ddof=0

    upper = mid + times * std_dev  # 上轨线
    lower = mid - times * std_dev  # 下轨线
    return {
        'upper': Decimal(str(upper)),
        'mid': Decimal(str(mid)),
        'lower': Decimal(str(lower))
    }