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
_HOST = '127.0.0.1'
_PORT = 5000


def connect(addr: str = "emulator-5554", host=_HOST, port=_PORT):
    """连接"""
    r = requests.get(f'{_PROTOCOL}://{host}:{port}/connect',
                     params={'addr': addr})
    pprint.pprint(r.json())


def get_balance(host=_HOST, port=_PORT):
    """查询资金"""
    r = requests.get(f'{_PROTOCOL}://{host}:{port}/get_balance')
    pprint.pprint(r.json())


def get_positions(host=_HOST, port=_PORT):
    """查询持仓"""
    r = requests.get(f'{_PROTOCOL}://{host}:{port}/get_positions')
    pprint.pprint(r.json())


def get_orders(break_after_done: bool = True, host=_HOST, port=_PORT):
    """查询委托"""
    r = requests.get(f'{_PROTOCOL}://{host}:{port}/get_orders',
                     params={'break_after_done': break_after_done})
    pprint.pprint(r.json())


def order_at(idx: int = 0, host=_HOST, port=_PORT):
    """指定委托信息"""
    r = requests.get(f'{_PROTOCOL}://{host}:{port}/order_at/{idx}')
    pprint.pprint(r.json())


def buy(qty: int, price: float = float('nan'), code: Optional[str] = None, host=_HOST, port=_PORT):
    """买入"""
    r = requests.get(f'{_PROTOCOL}://{host}:{port}/buy',
                     params={'qty': qty, 'price': price, 'code': code})
    pprint.pprint(r.json())


def sell(qty: int, price: float = float('nan'), code: Optional[str] = None, host=_HOST, port=_PORT):
    """卖出"""
    r = requests.get(f'{_PROTOCOL}://{host}:{port}/sell',
                     params={'qty': qty, 'price': price, 'code': code})
    pprint.pprint(r.json())


def cancels(opt: str = 'all', host=_HOST, port=_PORT):
    """批量撤单"""
    r = requests.get(f'{_PROTOCOL}://{host}:{port}/cancels/{opt}')
    pprint.pprint(r.json())


def cancel(idx: int = 0, host=_HOST, port=_PORT):
    """单笔撤单"""
    r = requests.get(f'{_PROTOCOL}://{host}:{port}/cancel/{idx}')
    pprint.pprint(r.json())


def run(host=_HOST, port=_PORT):
    """启动服务"""
    # 启动`Flask`服务
    # os.system(f'flask --app=thsauto.app.flask_ run --host={host} --port={port}')
    # 启动`FastAPI`服务
    os.system(f'uvicorn thsauto.app.fastapi_:app --host={host} --port={port}')


def _main():
    fire.Fire()


if __name__ == '__main__':
    _main()
