# -*- coding: UTF-8 -*-
import time
import random


# 模拟等待机制的函数。
def time_wait(interval=10, total_time=10 ** 2):
    """
    模拟等待机制的函数。

    该函数用于在程序中模拟等待过程，总共暂停 `total_time` 秒，每次暂停 `interval` 秒。
    在每次暂停期间，打印已过去的总等待时间。如果达到总等待时间，将引发 `RuntimeError` 异常。

    参数:
    - interval (int): 每次暂停的时间间隔，默认为 10 秒。
    - total_time (int): 总的等待时间，默认为 100 秒。

    异常:
    - RuntimeError: 当达到总等待时间时抛出。
    """
    i = 0
    while i * interval < total_time:
        time.sleep(interval)
        i += 1
        print("Waiting time has passed: {} seconds'".format(i * interval))
    raise RuntimeError("time out...")


def generate_random_floats(n, min_val, max_val):
    """
    生成指定范围和数量的浮点随机数列表。

    参数:
    n (int): 随机数的数量。
    min_val (float): 随机数的最小值。
    max_val (float): 随机数的最大值。

    返回:
    list: 包含 n 个浮点随机数的列表。
    """
    return [random.uniform(min_val, max_val) for _ in range(n)]
