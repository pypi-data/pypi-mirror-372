import collections
import time

func_cost = collections.defaultdict(int)
# 定时器
def timer(func, *args):
    # print(func.__name__, 'start')
    begin_time = time.time()
    reuslt = func(*args)
    end_time = time.time()
    func_cost[func.__name__] += (end_time - begin_time)
    # print(func.__name__, 'end.it cost {}s\n'.format(end_time - begin_time))
    return reuslt


def print_timer():
    for func_name, cost in func_cost.items():
        print(func_name, ' cost: {}s'.format(cost))
