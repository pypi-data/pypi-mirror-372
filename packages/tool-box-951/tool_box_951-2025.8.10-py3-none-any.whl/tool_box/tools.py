"""
@Author: MA XinXin
@update time: 2025-03-15 16:23
"""

import os
import time
import subprocess
import hashlib

# import shutil
import math
import inspect
import json
import datetime
import signal
from functools import wraps

import psutil
import pytz
import numpy as np
from loguru import logger


def set_norm_logger(out_dir="./log"):
    """设置日志格式
    @param out_dir: 日志输出目录
    """
    caller_frame = inspect.stack()[1]
    file_name = caller_frame.filename
    base_name = os.path.basename(file_name).rsplit(".", maxsplit=1)[0]
    date_now = datetime.datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(out_dir, base_name + "." + date_now)
    mkdir(out_dir)
    logger.info("set logger {}", log_file)
    logger.remove(handler_id=None)
    logger.add(
        log_file,
        # rotation="00:00",
        # retention=datetime.timedelta(days=7),
        backtrace=True,
        diagnose=True,
        enqueue=True,
    )


def daily_logger(out_dir="./log"):
    """设置日志格式
    @param out_dir: 日志输出目录
    """
    caller_frame = inspect.stack()[1]
    file_name = caller_frame.filename
    base_name = os.path.basename(file_name).rsplit(".", maxsplit=1)[0]
    date_now = datetime.datetime.now().strftime("%Y%m%d")
    mkdir(out_dir)
    logger.remove(handler_id=None)
    logger.add(
        "log/" + base_name + ".{time:YYYYMMDD}",
        rotation="00:00",
        retention=datetime.timedelta(days=7),
        backtrace=True,
        diagnose=True,
        enqueue=True,
    )


def format_time(seconds):
    seconds = round(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours}h {minutes}m {seconds}s"


def timeit(func):
    @wraps(func)
    def measure_time(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        logger.info(
            "`{}` executed in {} {:.2f} ms",
            func.__name__,
            format_time(elapsed_time),
            (elapsed_time - int(elapsed_time)) * 1e3,
        )
        return result

    return measure_time


def dec_retry(retry=5, delay=1):
    """
    装饰器函数，用于在失败时重试指定的次数。

    :param retry: 最大重试次数, 默认5次
    :param delay: 初始延迟时间（秒）
    """

    def decorator_retry(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay
            while retries < retry:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.info("Attempt {} {}", retries + 1, e)
                    retries += 1
                    time.sleep(current_delay)

        return wrapper

    return decorator_retry


def guess_ts_unit(ts):
    """
    猜测时间戳单位
    """
    ts_s = 1718873000
    n = round(math.log(ts / ts_s) / math.log(10))
    if n == 0:
        return "s"
    if n == 3:
        return "ms"
    if n == 6:
        return "us"
    if n == 9:
        return "ns"
    return "s"


def one_day_ago(date_format="%Y%m%d"):
    return (datetime.datetime.now() - datetime.timedelta(days=1)).strftime(date_format)


def two_day_ago(date_format="%Y%m%d"):
    return (datetime.datetime.now() - datetime.timedelta(days=2)).strftime(date_format)


def three_day_ago(date_format="%Y%m%d"):
    return (datetime.datetime.now() - datetime.timedelta(days=3)).strftime(date_format)


def four_day_ago(date_format="%Y%m%d"):
    return (datetime.datetime.now() - datetime.timedelta(days=4)).strftime(date_format)


def days_ago(days=5, date_format="%Y%m%d"):
    return (datetime.datetime.now() - datetime.timedelta(days=days)).strftime(
        date_format
    )


def today(date_format="%Y-%m-%d"):
    return datetime.datetime.now().strftime(date_format)


def timestamp_to_beijing_time(timestamp):
    """将时间戳转换为北京时间"""
    utc_dt = datetime.datetime.utcfromtimestamp(timestamp)
    beijing_tz = pytz.timezone("Asia/Shanghai")
    beijing_dt = utc_dt.replace(tzinfo=pytz.UTC).astimezone(beijing_tz)
    formatted_time = beijing_dt.strftime("%Y-%m-%d %H:%M:%S %Z%z")
    return formatted_time


def kill_process_tree(pid):
    sig = signal.SIGKILL
    pid_list = [pid]
    while True:
        if len(pid_list) == 0:
            break
        tmp_pid = pid_list.pop(0)
        if not psutil.pid_exists(tmp_pid):
            continue
        parent = psutil.Process(tmp_pid)
        if parent is not None:
            children = parent.children(recursive=False)
            if children is not None:
                for child in children:
                    pid_list.append(child.pid)
            cmdline = " ".join(parent.cmdline())
            print(f"kill {parent.pid} {cmdline}")
            parent.send_signal(sig)


def rm(path):
    os.system(f"/bin/rm -rf {path}")


def mkdir(path):
    """创建文件夹"""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True, mode=0o755)


def ls(directory, file_only=False, abs_path=False):
    """列出目录
    @param directory: 要列出的目录
    @param file_only: 是否只列出文件
    @param abs_path: 是否返回绝对路径
    """
    file_names = []
    with os.scandir(directory) as entries:
        for entry in entries:
            if file_only and entry.is_dir():
                continue
            if abs_path:
                file_names.append(entry.path)
            else:
                file_names.append(entry.name)
    return sorted(file_names)


def roundn(x, n: int):
    """保留n位有效数字 i.e (1) x=1.2121, n=3, return 1.21 (2) x=0.2121, n=3, return
    0.212."""
    if x == 0:
        return x
    return round(x, -int(math.floor(math.log10(abs(x)))) + (n - 1))


class NumpyEncoder(json.JSONEncoder):
    """Special json encoder for numpy types."""

    def default(self, o):
        if isinstance(
            o,
            (
                np.int_,
                np.intc,
                np.intp,
                np.int8,
                np.int16,
                np.int32,
                np.int64,
                np.uint8,
                np.uint16,
                np.uint32,
                np.uint64,
            ),
        ):
            return int(o)
        if isinstance(o, (np.float_, np.float16, np.float32, np.float64)):
            return float(o)
        if isinstance(o, (np.ndarray,)):
            return o.tolist()
        if isinstance(o, (list, tuple)):
            return json.JSONEncoder.default(self, o)
        if isinstance(o, (int, float, bool)):
            return json.JSONEncoder.default(self, o)

        if isinstance(o, type(mkdir)):
            return o.__name__

        return None


def to_json(config):
    """将字典转化为json字符串"""
    return json.dumps(config, indent=4, cls=NumpyEncoder)


def drop_duplicates(factors):
    if factors is None:
        return []
    if np.size(factors) == 0:
        return factors
    new_factors = []
    for i in factors:
        if i in new_factors:
            continue
        new_factors.append(i)
    return new_factors


def to_man_file(df, out_file, cols=5):
    with open(out_file, "w") as f:
        for i in range(0, df.shape[1], cols):
            i_end = min(i + cols, df.shape[1])
            if i == i_end:
                continue
            s = df.iloc[:, i:i_end].to_string()
            f.write(s + "\n")


def is_file_updated(file_path, dt: int) -> bool:
    """文件在dt时间内是否有更新,
    @dt:时间间隔, 单位为秒
    @return True:有更新 False:没有更新
    """
    # 获取文件的最后修改时间
    modified_time = os.path.getmtime(file_path)

    # 计算当前时间和最后修改时间的时间差
    time_diff = datetime.datetime.now() - datetime.datetime.fromtimestamp(modified_time)

    # 比较时间差和指定的时间间隔
    if time_diff.total_seconds() <= dt:
        return True  # 文件在最近dt时间内有更新
    return False  # 文件在最近dt时间内没有更新


def is_file_not_updated(file_path, dt):
    """文件在dt时间内是否维持不变
    True: 不变
    False：发生了变化
    """
    modified_time = os.path.getmtime(file_path)
    time_diff = datetime.datetime.now() - datetime.datetime.fromtimestamp(modified_time)
    return time_diff.total_seconds() > dt


def file_is_newer_than(file_path1, file_path2):
    """True: file1比file2新, False: file2比file1新"""
    modified_time1 = os.path.getmtime(file_path1)
    modified_time2 = os.path.getmtime(file_path2)
    return modified_time1 > modified_time2


def is_text_file(file_path):
    """判断文件是否为文本文件"""
    result = subprocess.check_output(["file", "-i", file_path], text=True)
    return "text/plain" in result


def get_updated_files(folder_path, window):
    """
    检查文件夹内是否有文件在指定时间内更新

    参数:
        folder_path:      目标文件夹路径
        window: 时间窗口（秒）

    返回:
        bool: 存在更新返回True，否则False
        list: 更新文件路径列表（仅当target_file=None时返回）
    """
    current_time = time.time()
    updated_files = []
    if not os.path.exists(folder_path):
        return updated_files

    # 遍历文件夹（含子目录）
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)

            # 获取文件修改时间<cite data-id='30002'>30002</cite>
            try:
                mod_time = os.path.getmtime(file_path)
                time_diff = current_time - mod_time

                # 判断是否在时间窗口内更新
                if time_diff <= window:
                    updated_files.append(file_path)
            except OSError:  # 处理权限问题等异常
                continue

    return updated_files


def get_files_hash(files):
    hash_obj = hashlib.new("sha256")
    for i in files:
        hash_obj.update(open(i, "rb").read())
    return hash_obj.hexdigest()
