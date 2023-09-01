from typing import Dict, Tuple, Any, Optional, Union

import pandas as pd
import uiautomator2 as u2

from .base import get_balance, get_positions, get_orders, buy, sell, cancel_single, cancel_multiple, init_navigation
from .parse import parse_confirm_order, parse_orders, parse_positions, parse_balance, parse_confirm_cancel
from .utils import Timer
from .xpath import XPath


class THS:
    # uiautomator2中的设备
    d = None
    x = None
    # 导航栏几个按扭位置
    navigation = {}

    # 以下未处理的私有成员变量可以人工访问实现特别功能
    balance = {}
    orders = []
    positions = []
    confirm = {}
    prompt = {}

    def __init__(self, debug: bool = True, skip_popup: bool = False) -> None:
        """初始化

        Parameters
        ----------
        debug: bool
            调试模式下不改变柜台状态。即下单和撤单时最后一步会自动点击取消
            初次使用时，请在`debug=True`模拟账号下走一遍流程
        skip_popup: bool
            启用后，下单时的弹出框的确认将交由`李跳跳`等工具完成。好处是弹出框关闭快、下单更快
            1. 用户需自行设置好相应的工具软件
            2. 弹出框的内容不再读取返回
            3. 实测`无障碍服务`与`uiautomator2`冲突，等这个问题解决后，这个功能就能正常使用了


        """
        self.debug: bool = debug
        self.skip_popup: bool = skip_popup

    def connect(self, addr: str = "emulator-5554") -> None:
        """连接

        Parameters
        ----------
        addr: str
            可以本地连接，也可以远程。连接方法参考`uiautomator2`项目
        """
        with Timer():
            self.d = u2.connect(addr)
            self.d.implicitly_wait(3.0)
            # 这里会引导环境准备
            return self.d.info

    def home(self):
        """页首。这里记录了几个导航按钮的位置"""
        with Timer():
            assert self.d is not None, '请先执行`connect()`'
            self.x = XPath(self.d)
            self.x.dump_hierarchy()
            self.navigation = init_navigation(self.x)
            if len(self.navigation) != 5:
                self.x = None
                raise Exception("请检查当前是否处于可交易界面!!!")

    def goto(self, tab: str):
        if True:
            if self.x is None:
                self.home()
            self.x.click(*self.navigation[tab])
        else:
            self.d(resourceId="com.hexin.plat.android:id/btn", text=tab).click()

    def get_balance(self) -> Dict[str, float]:
        """查询资产

        Returns
        -------
        dict

        """
        with Timer():
            self.goto('持仓')
            self.balance = get_balance(self.d)
            return parse_balance(self.balance)

    def get_positions(self) -> pd.DataFrame:
        """查询持仓

        Returns
        -------
        pd.DataFrame

        """
        with Timer():
            self.goto('持仓')
            self.positions = get_positions(self.d)
            return parse_positions(self.positions)

    def get_orders(self, break_after_done: bool = True) -> pd.DataFrame:
        """查询委托

        Parameters
        ----------
        break_after_done: bool
            遇到订单已是最终状态时跳出查询，此功能建立在列表已经排序，已经成交和已经撤单的订单排在最后的特点。
            没有此特点的列表不要启用此功能

        Returns
        -------
        pd.DataFrame

        """
        with Timer():
            self.goto('撤单')
            self.orders = get_orders(self.d, break_after_done)
            return parse_orders(self.orders)

    def order_at(self, idx: int) -> tuple:
        """返回委托列表中指定位置的委托

        Parameters
        ----------
        idx:int
            列表位置

        Returns
        -------
        tuple

        """
        assert 0 <= idx < len(self.orders), '请先执行`get_orders`，或不要超过有效范围'
        order = self.orders[idx]
        return order

    def cancel_single(self, order,
                      input_mask=(True, True, True, False, True, False, True, False),
                      inside_mask=(True, True, True, False, True, False, True, False),
                      debug: Optional[bool] = None) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """笔委托撤单

        Parameters
        ----------
        order: tuple
            输入委托
        input_mask: tuple
            输入中选择部分用来比较
        inside_mask: tuple
            列表中选择部分用来比较
        debug: bool or None
            可临时应用新`debug`参数

        Returns
        -------
        confirm: dict
            需要人工确认的信息
        prompt: dict
            无需人工确认的提示信息

        Notes
        -----
        底层使用字符串比较的方法查找指定位置。字符串要完全对应。
        例如: `100.0`与`100.00`不同, ` 万  科 A`与`万科A`也不同
        为方便，请与`order_at`配合使用

        """
        with Timer():
            self.goto('撤单')
            debug = self.debug if debug is None else debug
            self.confirm, self.prompt = cancel_single(self.d, order, input_mask, inside_mask, debug)
            return parse_confirm_cancel(self.confirm), self.prompt

    def cancel_multiple(self, opt: str = 'all',
                        debug: Optional[bool] = None) -> Tuple[Dict[str, str], Dict[str, str]]:
        """批量撤单

        Parameters
        ----------
        opt: str
            `all` `buy` `sell`
        debug: bool or None
            可临时应用新`debug`参数

        Returns
        -------
        confirm: dict
            需要人工确认的信息
        prompt: dict
            无需人工确认的提示信息

        """
        with Timer():
            self.goto('撤单')
            debug = self.debug if debug is None else debug
            self.confirm, self.prompt = cancel_multiple(self.d, opt, debug)
            return self.confirm, self.prompt

    def buy(self, qty: Union[int, str], price: Union[float, str] = float('nan'), *,
            symbol: Optional[str] = None, code: Optional[str] = None,
            debug: Optional[bool] = None, skip_popup: Optional[bool] = None) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """买入委托

        Parameters
        ----------
        qty: int
            委托量
        price: float or str
            委托价。如果使用默认值`float('nan')`将利用界面自动填入的`卖一价`
        symbol: str
            证券代码、名称、拼音缩写都支持。只要在键盘精灵排第一，不做校验
        code: str
            证券代码。会对输入进行校验。推荐使用证券代码
        debug: bool or None
            可临时应用新`debug`参数
        skip_popup: bool or None
            可临时应用新`skip_popup`参数

        Returns
        -------
        confirm: dict
            需要人工确认的信息
        prompt: dict
            无需人工确认的提示信息

        """
        with Timer():
            self.goto('买入')
            debug = self.debug if debug is None else debug
            skip_popup = self.skip_popup if skip_popup is None else skip_popup
            self.confirm, self.prompt = buy(self.d, qty, price, symbol, code, debug, skip_popup)
            return parse_confirm_order(self.confirm), self.prompt

    def sell(self, qty: Union[int, str], price: Union[float, str] = float('nan'), *,
             symbol: Optional[str] = None, code: Optional[str] = None,
             debug: Optional[bool] = None, skip_popup: Optional[bool] = None) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """卖出委托

        Parameters
        ----------
        qty: int or str
            委托量
        price: float or str
            委托价。如果使用默认值`float('nan')`将利用界面自动填入的`买一价`
        symbol: str
            证券代码、名称、拼音缩写都支持。只要在键盘精灵排第一，不做校验
        code: str
            证券代码。会对输入进行校验。推荐使用证券代码
        debug: bool or None
            可临时应用新`debug`参数
        skip_popup: bool or None
            可临时应用新`skip_popup`参数

        Returns
        -------
        confirm: dict
            需要人工确认的信息
        prompt: dict
            无需人工确认的提示信息

        """
        with Timer():
            self.goto('卖出')
            debug = self.debug if debug is None else debug
            skip_popup = self.skip_popup if skip_popup is None else skip_popup
            self.confirm, self.prompt = sell(self.d, qty, price, symbol, code, debug, skip_popup)
            return parse_confirm_order(self.confirm), self.prompt
