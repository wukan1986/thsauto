import time
from typing import Dict, Tuple, List

import uiautomator2 as u2
from loguru import logger

from .xpath import XPath


def order_is_done(status: str) -> bool:
    """委托状态是否为最终状态。目前此功能用于提前结束委托列表的滑动遍历

    TODO: 需要观察还有哪些状态。是否会出现不同券商的同状态叫法不同？

    // 147_状态说明
    #define ZTSM_NotSent			0	// 0-未申报
    #define ZTSM_1					1	//
    #define ZTSM_New				2	// 2-已申报未成交,未成交,已报
    #define ZTSM_Illegal			3	// 3-非法委托
    #define ZTSM_4					4	//
    #define ZTSM_PartiallyFilled	5	// 5-部分成交
    #define ZTSM_AllFilled			6	// 6-全部成交,已成,全部成交
    #define ZTSM_PartiallyCancelled	7	// 7-部成部撤，部撤
    #define ZTSM_AllCancelled		8	// 8-全部撤单,已撤,全部撤单
    #define ZTSM_CancelRejected		9	// 9-撤单未成					只会出现撤单记录中
    #define ZTSM_WaitingForReport	10	// 10-等待人工申报

    // 已成,部成,废单,已撤,部撤

    """
    # 全部撤单 内部撤单
    if status.find('撤') >= 0:
        return True
    # 全部成交
    if status in ('全部成交', '已成'):
        return True
    # 待申报 未成交
    return False


def get_balance(d: u2.Device) -> Dict[str, str]:
    d(resourceId="com.hexin.plat.android:id/btn", text="持仓").click()

    root = d(resourceId="com.hexin.plat.android:id/main_layout")
    root.fling.toBeginning()
    root.fling.toBeginning()

    x = XPath(d)
    x.dump_hierarchy()
    path2 = '//*[@resource-id="com.hexin.plat.android:id/main_layout"]/android.widget.LinearLayout[1]/android.widget.LinearLayout[2]/descendant::android.widget.TextView/@text'
    path4 = '//*[@resource-id="com.hexin.plat.android:id/main_layout"]/android.widget.LinearLayout[1]/android.widget.LinearLayout[4]/descendant::android.widget.TextView/@text'
    nums = x.xpath(f'{path2} | {path4}')

    names = ['总资产', '浮动盈亏', '当日参考盈亏', '当日参考盈亏率', '持仓市值', '可用资金', '可取资金']
    _dict = dict(zip(names, nums))

    return _dict


def _positions_in_view(d: u2.Device, x: XPath) -> Tuple[List[int], List[tuple]]:
    root = d(resourceId="com.hexin.plat.android:id/recyclerview_id")
    count = root.info.get('childCount')

    list1 = []
    list2 = []
    for i in range(1, count + 1):
        _path = f'//*[@resource-id="com.hexin.plat.android:id/recyclerview_id"]/android.widget.RelativeLayout[{i}]/descendant::android.widget.TextView/@text'
        tup = tuple(x.xpath(_path))
        logger.info("{} {}", i, tup)
        list1.append(i)
        list2.append(tup)

    return list1, list2


def get_positions(d: u2.Device) -> List[tuple]:
    d(resourceId="com.hexin.plat.android:id/btn", text="持仓").click()

    root = d(resourceId="com.hexin.plat.android:id/recyclerview_id")
    root.fling.toBeginning()

    x = XPath(d)

    lists = []
    while not x.same_hierarchy():
        x.dump_hierarchy()
        list1, list2 = _positions_in_view(d, x)
        lists.extend(list2)
        root.scroll.forward()
        time.sleep(1.0)
        x.dump_hierarchy()

    # 只留固定格式
    lists = [_ for _ in lists if len(_) == 8]
    # 去重
    lists = sorted(set(lists), key=lists.index)

    return lists


def _orders_in_view(d: u2.Device, x: XPath) -> Tuple[List[int], List[tuple], str]:
    root = d(resourceId="com.hexin.plat.android:id/chedan_recycler_view")
    count = root.info.get('childCount')

    last_status = ''
    list1 = []
    list2 = []
    for i in range(1, count + 1):
        _path = f'//*[@resource-id="com.hexin.plat.android:id/chedan_recycler_view"]/android.widget.LinearLayout[{i}]/descendant::android.widget.TextView/@text'
        tup = tuple(x.xpath(_path))
        logger.info("{} {}", i, tup)
        # ['全撤', '撤买', '撤卖']
        # ['今日成交单']
        # ['其他']
        list1.append(i)
        list2.append(tup)
        if len(tup) > 0:
            last_status = tup[-1]

    return list1, list2, last_status


def get_orders(d: u2.Device, break_after_done: bool) -> List[tuple]:
    d(resourceId="com.hexin.plat.android:id/btn", text="撤单").click()

    root = d(resourceId="com.hexin.plat.android:id/scrollView")
    root.fling.toBeginning()

    x = XPath(d)

    lists = []
    while not x.same_hierarchy():
        x.dump_hierarchy()
        list1, list2, last_status = _orders_in_view(d, x)
        lists.extend(list2)

        # 提前返回
        if break_after_done and order_is_done(last_status):
            logger.info(f'已经搜索完可撤区，提前返回。{last_status=}')
            break

        root.scroll.forward()
        time.sleep(1.0)
        x.dump_hierarchy()

    # 只留固定格式
    lists = [_ for _ in lists if len(_) == 8]
    # 去重
    lists = sorted(set(lists), key=lists.index)

    return lists


def _check_cancel_multiple(d: u2.Device) -> bool:
    """检查是弹出批量撤单确认，还是不支持"""
    node = d(resourceId="com.hexin.plat.android:id/cancel_btn")
    node.wait(exists=True, timeout=2.0)
    return node.exists


def _confirm_cancel_multiple(d: u2.Device) -> Dict[str, str]:
    """批量撤单对话框"""
    nodes = {
        '标题': d(resourceId="com.hexin.plat.android:id/dialog_title"),
        '证券账户': d(resourceId="com.hexin.plat.android:id/account_tv"),
        '撤单对象': d(resourceId="com.hexin.plat.android:id/clearance_stock_tv"),
    }
    return {k: v.get_text() for k, v in nodes.items()}


def _dialog_prompt(d: u2.Device) -> Dict[str, str]:
    """有标题提示对象框"""
    nodes = {
        '标题': d(resourceId="com.hexin.plat.android:id/dialog_title"),
        '内容': d(resourceId="com.hexin.plat.android:id/prompt_content"),
    }
    return {k: v.get_text() for k, v in nodes.items()}


def _dialog_content(d: u2.Device) -> Dict[str, str]:
    """无标题提示对象框"""
    nodes = {
        '内容': d(resourceId="com.hexin.plat.android:id/prompt_content"),
    }
    return {k: v.get_text() for k, v in nodes.items()}


def cancel_multiple(d: u2.Device, opt: str = 'all', debug=True) -> Tuple[Dict[str, str], Dict[str, str]]:
    """批量撤单"""
    nodes = {
        'all': d(resourceId="com.hexin.plat.android:id/quanche_tv"),
        'buy': d(resourceId="com.hexin.plat.android:id/che_buy_tv"),
        'sell': d(resourceId="com.hexin.plat.android:id/che_sell_tv"),
    }
    node = nodes[opt]

    d(resourceId="com.hexin.plat.android:id/btn", text="撤单").click()

    root = d(resourceId="com.hexin.plat.android:id/chedan_recycler_view")
    childCount = root.info.get('childCount')
    if childCount == 0:
        logger.warning(f'childCount == 0, {childCount=}')
        return {}, {}

    # 滚动到指定位置
    root.scroll.to(text='全撤')
    assert node.wait(exists=True, timeout=2.0), "找不到 ['全撤', '撤买', '撤卖'] 三个按钮。请单笔委托撤单"
    node.click()
    confirm = {}
    prompt = {}
    # 有两种情况。1. 撤单确认 2. 不支持批量撤单
    if _check_cancel_multiple(d):
        # 1. 撤单确认
        confirm = _confirm_cancel_multiple(d)
        logger.info(confirm)
        if debug:
            _dialog2_select(d, 0)
        else:
            _dialog2_select(d, 1)
    else:
        # 2. 不支持批量撤单
        prompt = _dialog_content(d)
        logger.warning(prompt)
        _dialog2_select(d, 1)

    return confirm, prompt


def _check_cancel_single(d: u2.Device) -> bool:
    """检查是弹出单笔委托撤单的三选择，还是无反应"""
    node = d(resourceId="com.hexin.plat.android:id/option_cancel")
    node.wait(exists=True, timeout=2.0)
    return node.exists


def cancel_single(d: u2.Device,
                  order,
                  input_mask=(True, True, True, False, True, False, True, False),
                  inside_mask=(True, True, True, False, True, False, True, False),
                  debug=True) -> Tuple[Dict[str, str], Dict[str, str]]:
    """单笔委托撤单"""
    # 过滤为真部分
    order = tuple([j for i, j in zip(input_mask, order) if i])
    logger.info(f'{order=}')
    if len(order) == 0:
        return {}, {}

    d(resourceId="com.hexin.plat.android:id/btn", text="撤单").click()

    root = d(resourceId="com.hexin.plat.android:id/scrollView")
    root.fling.toBeginning()

    x = XPath(d)

    found = -1
    while not x.same_hierarchy():
        x.dump_hierarchy()
        list1, list2, last_status = _orders_in_view(d, x)
        # 这里的位置从1开始
        for idx, order_ in zip(list1, list2):
            tup = tuple([j for i, j in zip(inside_mask, order_) if i])
            if order == tup:
                if order_is_done(order_[-1]):
                    logger.warning(f'状态已完成，不可再撤, {idx=}, {order_=}')
                    return {}, {}
                found = idx
                break
        # 这里的位置从1开始
        if found > 0:
            break

        # 提前返回
        if order_is_done(last_status):
            logger.info(f'已经搜索完可撤区，提前返回。{last_status=}')
            break

        root.scroll.forward()
        time.sleep(1.0)
        x.dump_hierarchy()

    logger.info(f'{found=}')
    if found < 0:
        return {}, {}

    # 这里的位置从0开始
    node = root.child(index=found - 1, clickable=True)
    node.wait(exists=True, timeout=2.0)
    node.click()
    # 两种情况：1. 弹出撤单确认对话框。 2. 灰了点击无反应
    if _check_cancel_single(d):
        # 1. 弹出撤单确认对话框
        confirm = _confirm_cancel_single(d)
        logger.info(confirm)
        if debug:
            # 取消
            _dialog3_cancel_single_select(d, 2)
        else:
            # 撤单。建议之后再查一下委托列表进行状态更新
            _dialog3_cancel_single_select(d, 0)
    else:
        # 2. 灰了点击无反应
        confirm = {}
    # 为与全撤输出统一
    return confirm, {}


def _place_order(d: u2.Device, symbol: str, price: str, qty: str) -> None:
    """下单动作。输入股票代码、股票名称、缩写都可以。只要在键盘精灵中排第一即可"""
    # 输入参数类型修正
    stockcode = str(symbol)
    stockprice = str(price)
    stockvolume = str(qty)

    auto_stockcode = d(resourceId="com.hexin.plat.android:id/auto_stockcode")
    auto_stockcode.wait(exists=True, timeout=2.0)

    # 输入股票代码
    auto_stockcode.click()
    dialogplus_view_container = d(resourceId="com.hexin.plat.android:id/dialogplus_view_container")
    dialogplus_view_container.wait(exists=True, timeout=2.0)
    node = dialogplus_view_container.child(className='android.widget.EditText')
    node.click()
    node.set_text(stockcode)
    # 键盘精灵中第一条。断网情况下第一条可能不更新，导致选择错误，但下单也会失败，所以不会有严重后果
    stockcode_tv = d(resourceId="com.hexin.plat.android:id/stockcode_tv")
    stockcode_tv.wait(exists=True, timeout=2.0)
    stockcode_tv.click()

    # 输入价格、数量、点击买卖按钮
    node = d(resourceId="com.hexin.plat.android:id/stockprice").child(className="android.widget.EditText")
    node.click()
    node.set_text(stockprice)
    node = d(resourceId="com.hexin.plat.android:id/stockvolume").child(className="android.widget.EditText")
    node.click()
    node.set_text(stockvolume)
    d(resourceId="com.hexin.plat.android:id/btn_transaction").click()


def _place_order_auto(d: u2.Device, symbol: str, price: str, qty: str, debug: bool) -> Tuple[Dict[str, str], Dict[str, str]]:
    """下单后，自动进行之后的各项点击与确认"""
    _place_order(d, symbol, price, qty)

    confirm = {}
    prompt = {}
    # 1. 直接提示不合法
    # 2. 委托确认
    if _check_confirm_order(d):
        confirm = _confirm_order(d)
        # {'标题': '委托卖出确认', '账户': 'A123456', '名称': '华海药业', '代码': '600521', '数量': 1, '价格': 100.0}
        logger.info(confirm)
        # TODO: 是否要加判断，输入是否一样
        if debug:
            _dialog2_select(d, 0)
        else:
            # 确认下单
            _dialog2_select(d, 1)
            # {'标题': '系统信息', '内容': '股票余额不足 ,不允许卖空'}
            # {'标题': '系统信息', '内容': '卖出数量必须是100的整数倍'}
            # {'标题': '系统信息', '内容': '委托已提交，合同号为：3672041198'}
            prompt = _dialog_prompt(d)
            logger.info(prompt)
            _dialog2_select(d, 1)
    else:
        # {'标题': '系统信息', '内容': '委托价格不合法，请重新输入'}
        # {'标题': '系统信息', '内容': '委托数量必须大于0'}
        prompt = _dialog_prompt(d)
        logger.info(prompt)
        _dialog2_select(d, 1)

    # 返回个两个字典。出错时，第一个字典为空
    return confirm, prompt


def _check_confirm_order(d: u2.Device) -> bool:
    """委托确认对话框晦检查"""
    node1 = d(resourceId="com.hexin.plat.android:id/ok_btn")
    node1.wait(exists=True, timeout=2.0)
    node2 = d(resourceId="com.hexin.plat.android:id/cancel_btn")
    return node2.exists


def _confirm_order(d: u2.Device) -> Dict[str, str]:
    """委托确认"""
    nodes = {
        '标题': d(resourceId="com.hexin.plat.android:id/dialog_title"),
        '账户': d(resourceId="com.hexin.plat.android:id/account_value"),
        '名称': d(resourceId="com.hexin.plat.android:id/stock_name_value"),
        '代码': d(resourceId="com.hexin.plat.android:id/stock_code_value"),
        '数量': d(resourceId="com.hexin.plat.android:id/number_value"),
        '价格': d(resourceId="com.hexin.plat.android:id/price_value"),
    }
    return {k: v.get_text() for k, v in nodes.items()}


def _confirm_cancel_single(d: u2.Device) -> Dict[str, str]:
    """撤单确认"""
    nodes = {
        '标题': d(resourceId="com.hexin.plat.android:id/title_view"),
        '操作': d(resourceId="com.hexin.plat.android:id/option_textview"),
        '名称': d(resourceId="com.hexin.plat.android:id/stockname_textview"),
        '代码': d(resourceId="com.hexin.plat.android:id/stockcode_textview"),
        '数量': d(resourceId="com.hexin.plat.android:id/ordernumber_textview"),
        '价格': d(resourceId="com.hexin.plat.android:id/orderprice_textview"),
    }
    return {k: v.get_text() for k, v in nodes.items()}


def _dialog3_cancel_single_select(d: u2.Device, opt: int = 0) -> None:
    nodes = {
        0: d(resourceId="com.hexin.plat.android:id/option_chedan"),
        1: d(resourceId="com.hexin.plat.android:id/option_chedan_and_buy"),
        2: d(resourceId="com.hexin.plat.android:id/option_cancel"),
    }
    nodes[opt].click()


def _dialog2_select(d: u2.Device, opt: int = 1) -> None:
    nodes = {
        0: d(resourceId="com.hexin.plat.android:id/cancel_btn"),
        1: d(resourceId="com.hexin.plat.android:id/ok_btn"),
    }
    nodes[opt].click()


def buy(d: u2.Device, symbol: str, price: float, qty: int, debug: bool) -> Tuple[Dict[str, str], Dict[str, str]]:
    d(resourceId="com.hexin.plat.android:id/btn", text="买入").click()
    return _place_order_auto(d, symbol, price, qty, debug)


def sell(d: u2.Device, symbol: str, price: float, qty: int, debug: bool) -> Tuple[Dict[str, str], Dict[str, str]]:
    d(resourceId="com.hexin.plat.android:id/btn", text="卖出").click()
    return _place_order_auto(d, symbol, price, qty, debug)
