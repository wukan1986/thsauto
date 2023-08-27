# %%
# 540 1920 180
# 360 1920 180
# 360 1600/1500 180
import uiautomator2 as u2

from .base import get_balance, get_positions, get_orders, buy, sell, cancel_single, cancel_multiple
from .parse import parse_confirm_order, parse_orders, parse_positions, parse_balance, parse_confirm_cancel


class THS:
    # uiautomator2中的设备
    d = None

    # 以下未处理的私有成员变量可以手工调用实现特别功能
    balance = {}
    orders = []
    positions = []
    confirm = {}
    prompt = {}

    def __init__(self, debug: bool = True) -> None:
        """初始化

        Parameters
        ----------
        debug: bool
            调试模式下不改变柜台状态。即下单和撤单时最后一步会自动点击取消
            初次使用时，请在`debug=True`模拟账号下走一遍流程

        """
        self._debug = debug

    def connect(self, addr: str = "emulator-5554") -> None:
        """连接

        Parameters
        ----------
        addr: str
            可以本地连接，也可以远程。连接方法参考`uiautomator2`项目
        """
        self.d = u2.connect(addr)
        self.d.implicitly_wait(3.0)

    def get_balance(self):
        """查询资产

        Returns
        -------
        dict

        """
        self.balance = get_balance(self.d)
        return parse_balance(self.balance)

    def get_positions(self):
        """查询持仓

        Returns
        -------
        list or pd.DataFrame

        """
        self.positions = get_positions(self.d)
        return parse_positions(self.positions)

    def get_orders(self):
        """查询委托

        Returns
        -------
        list or pd.DataFrame

        """
        self.orders = get_orders(self.d)
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
                      inside_mask=(True, True, True, False, True, False, True, False)):
        """笔委托撤单

        Parameters
        ----------
        order: tuple
            输入委托
        input_mask: tuple
            输入中选择部分用来比较
        inside_mask: tuple
            列表中选择部分用来比较

        Returns
        -------
        tuple(dict, dict)

        Notes
        -----
        底层使用字符串比较的方法查找指定位置。字符串要完全对应。
        例如: `100.0`与`100.00`不同, ` 万  科 A`与`万科A`也不同
        为方便，请与`order_at`配合使用

        """
        self.confirm, self.prompt = cancel_single(self.d, order, input_mask, inside_mask, self._debug)
        return parse_confirm_cancel(self.confirm), self.prompt

    def cancel_multiple(self, opt: str = 'all'):
        """批量撤单

        Parameters
        ----------
        opt: str
            `all` `buy` `sell`

        Returns
        -------
        tuple(dict, dict)

        """
        self.confirm, self.prompt = cancel_multiple(self.d, opt, self._debug)
        return self.confirm, self.prompt

    def buy(self, symbol: str, price: float, qty: int):
        """买入委托

        Parameters
        ----------
        symbol: str
            证券代码、名称、拼音缩写都支持。只要在键盘精灵排第一即可。推荐使用证券代码
        price: float
            委托价
        qty: int
            委托量

        Returns
        -------
        tuple(dict, dict)

        """
        self.confirm, self.prompt = buy(self.d, symbol, price, qty, self._debug)
        return parse_confirm_order(self.confirm), self.prompt

    def sell(self, symbol: str, price: float, qty: int):
        """卖出委托

        Parameters
        ----------
        symbol: str
            证券代码、名称、拼音缩写都支持。只要在键盘精灵排第一即可。推荐使用证券代码
        price: float
            委托价
        qty: int
            委托量

        Returns
        -------
        tuple(dict, dict)

        """
        self.confirm, self.prompt = sell(self.d, symbol, price, qty, self._debug)
        return parse_confirm_order(self.confirm), self.prompt
