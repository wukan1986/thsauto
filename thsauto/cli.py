"""
本计划使用`Flask-CLI`来实现，但此方案`CLI`与`Web`服务耦合过于紧密

1. 每次执行`CLI`都会重启`Web`服务
2. `uiautomator2`必须提前`connect`,耗时至少10秒以上

所以只能分别实现
"""
import os
import pprint
from typing import Optional

import fire
import requests

_PROTOCOL = 'http'  # https
_HOST = os.environ.get('THSAUTO_HOST', '127.0.0.1')
_PORT = int(os.environ.get('THSAUTO_PORT', '5000'))

_URL = f'{_PROTOCOL}://{_HOST}:{_PORT}'


def connect(addr: str = "emulator-5554"):
    """连接"""
    r = requests.get(f'{_URL}/connect',
                     params={'addr': addr})
    pprint.pprint(r.json())


def get_balance():
    """查询资金"""
    r = requests.get(f'{_URL}/get_balance')
    pprint.pprint(r.json())


def get_positions():
    """查询持仓"""
    r = requests.get(f'{_URL}/get_positions')
    pprint.pprint(r.json())


def get_orders(break_after_done: bool = True):
    """查询委托"""
    r = requests.get(f'{_URL}/get_orders',
                     params={'break_after_done': break_after_done})
    pprint.pprint(r.json())


def order_at(idx: int = 0):
    """指定委托信息"""
    r = requests.get(f'{_URL}/order_at/{idx}')
    pprint.pprint(r.json())


def buy(qty: int, price: float = float('nan'), code: Optional[str] = None):
    """买入"""
    r = requests.get(f'{_URL}/buy',
                     params={'qty': qty, 'price': price, 'code': code})
    pprint.pprint(r.json())


def sell(qty: int, price: float = float('nan'), code: Optional[str] = None):
    """卖出"""
    r = requests.get(f'{_URL}/sell',
                     params={'qty': qty, 'price': price, 'code': code})
    pprint.pprint(r.json())


def cancels(opt: str = 'all'):
    """批量撤单"""
    r = requests.get(f'{_URL}/cancels/{opt}')
    pprint.pprint(r.json())


def cancel(idx: int = 0):
    """单笔撤单"""
    r = requests.get(f'{_URL}/cancel/{idx}')
    pprint.pprint(r.json())


def run(host=_HOST, port=_PORT):
    """启动服务"""
    # 启动`Flask`服务
    # os.system(f'flask --app=thsauto.app_.flask_ run --host={host} --port={port}')

    # 启动`FastAPI`服务
    # 不支持双层包，只能简化成一层
    os.system(f'uvicorn thsauto.app:app --host={host} --port={port}')


def _main():
    fire.Fire()


if __name__ == '__main__':
    _main()
