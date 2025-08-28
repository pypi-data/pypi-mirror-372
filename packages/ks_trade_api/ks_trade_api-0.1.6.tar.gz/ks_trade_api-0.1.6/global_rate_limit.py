import os
import time
import tempfile
from functools import wraps
from filelock import FileLock

class GlobalRateLimiter:
    def __init__(self, interval_sec: float, id: str = 'ks_trade_api_global_rate_limit'):
        """
        interval_sec: 限流间隔（秒）
        lock_name: 跨进程锁文件名
        ts_name: 记录上次调用时间戳的文件名
        """
        tmp_dir = os.path.expandvars(r"%LOCALAPPDATA%\Temp")  # 自动适配平台，例如 Windows 用 C:\Users\xx\AppData\Local\Temp。不能用tempfile.gettempdir()因为多会话会出现/temp/1和/temp不同
        self.interval = interval_sec
        lock_name = f'{id}.lock'
        ts_name = f'{id}.text'
        self.lock_file = os.path.join(tmp_dir, lock_name)
        self.ts_file = os.path.join(tmp_dir, ts_name)
        self.lock = FileLock(self.lock_file)

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self.lock:  # 跨进程互斥锁
                now = time.time()
                try:
                    if os.path.exists(self.ts_file):
                        with open(self.ts_file, "r") as f:
                            last = float(f.read().strip())
                    else:
                        last = 0.0
                except Exception:
                    last = 0.0

                wait_time = self.interval - (now - last)
                if wait_time > 0:
                    time.sleep(wait_time)

                try:
                    with open(self.ts_file, "w") as f:
                        f.write(str(time.time()))
                except Exception as e:
                    print(f"[RateLimiter] Failed to write ts_file: {e}")

            return func(*args, **kwargs)
        return wrapper
