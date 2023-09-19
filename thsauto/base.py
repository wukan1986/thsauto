import time
from typing import Dict, Tuple, List

import uiautomator2 as u2
from loguru import logger

from .xpath import XPath, center


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
    # 全部成交 已成
    if status in ('全部成交', '已成'):
        return True
    # 待申报 未成交
    return False


def init_navigation(x):
    """提前找到导航栏，之后可减少请求"""
    texts = x.xpath('//*[@resource-id="com.hexin.plat.android:id/btn"]/@bounds')
    # %%
    names = ['买入', '卖出', '撤单', '持仓', '查询']

    return {k: center(v) for k, v in zip(names, texts)}


def get_balance(d: u2.Device) -> Dict[str, str]:
    root = d(resourceId="com.hexin.plat.android:id/recyclerview_id")
    root.wait(exists=True, timeout=6.0)
    root.fling.toBeginning()
    root.fling.toBeginning()

    x = XPath(d)
    x.dump_hierarchy()
    path2 = '//*[@resource-id="com.hexin.plat.android:id/main_layout"]/android.widget.LinearLayout[1]/android.widget.LinearLayout[2]/descendant::android.widget.TextView/@text'
    path4 = '//*[@resource-id="com.hexin.plat.android:id/main_layout"]/android.widget.LinearLayout[1]/android.widget.LinearLayout[4]/descendant::android.widget.TextView/@text'
    nums = x.xpath(f'{path2} | {path4}')

    names = ['总资产', '浮动盈亏', '当日参考盈亏', '当日参考盈亏率', '持仓市值', '可用资金', '可取资金']

    return dict(zip(names, nums))


def _positions_in_view(x: XPath) -> Tuple[List[int], List[tuple]]:
    elements = x.xpath('//*[@resource-id="com.hexin.plat.android:id/recyclerview_id"]/android.widget.RelativeLayout')
    count = len(elements)

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
    root = d(resourceId="com.hexin.plat.android:id/recyclerview_id")
    root.wait(exists=True, timeout=6.0)
    root.fling.toBeginning()
    root.fling.toBeginning()

    x = XPath(d)

    lists = []
    x.dump_hierarchy()
    while not x.same_hierarchy():
        list1, list2 = _positions_in_view(x)
        lists.extend(list2)
        root.scroll.forward()
        time.sleep(1.0)
        x.dump_hierarchy()

    # 只留固定格式
    lists = [_ for _ in lists if len(_) == 8]
    # 去重
    lists = sorted(set(lists), key=lists.index)

    return lists


def _orders_in_view(x: XPath) -> Tuple[List[int], List[tuple], str]:
    elements = x.xpath('//*[@resource-id="com.hexin.plat.android:id/chedan_recycler_view"]/android.widget.LinearLayout')
    count = len(elements)

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
    root = d(resourceId="com.hexin.plat.android:id/scrollView")
    root.wait(exists=True, timeout=6.0)
    root.fling.toBeginning()
    root.fling.toBeginning()

    x = XPath(d)

    lists = []
    x.dump_hierarchy()
    while not x.same_hierarchy():
        list1, list2, last_status = _orders_in_view(x)
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


def _wait_cancel_multiple(d: u2.Device) -> bool:
    """检查是弹出批量撤单确认，还是不支持"""
    return d(resourceId="com.hexin.plat.android:id/cancel_btn").wait(exists=True, timeout=2.0)


def _confirm_cancel_multiple(x: XPath) -> Dict[str, str]:
    """批量撤单对话框"""
    texts = x.xpath('//*[@resource-id="com.hexin.plat.android:id/dialog_layout"]/descendant::android.widget.TextView/@text')
    texts = ['标题'] + texts
    return dict(zip(texts[::2], texts[1::2]))


def _dialog_prompt(x: XPath) -> Dict[str, str]:
    """有标题提示对象框"""
    path1 = '//*[@resource-id="com.hexin.plat.android:id/dialog_title"]/@text'
    path2 = '//*[@resource-id="com.hexin.plat.android:id/prompt_content"]/@text'
    texts = x.xpath(f'{path1} | {path2}')

    names = ['标题', '内容']

    return dict(zip(names, texts))


def _dialog_content(x: XPath) -> Dict[str, str]:
    """无标题提示对象框"""
    path2 = '//*[@resource-id="com.hexin.plat.android:id/prompt_content"]/@text'
    texts = x.xpath(f'{path2}')

    names = ['内容']

    return dict(zip(names, texts))


def cancel_multiple(d: u2.Device, opt: str = 'all', debug=True) -> Tuple[Dict[str, str], Dict[str, str]]:
    """批量撤单

    TODO: 可以优化
    """
    nodes = {
        'all': d(resourceId="com.hexin.plat.android:id/quanche_tv"),
        'buy': d(resourceId="com.hexin.plat.android:id/che_buy_tv"),
        'sell': d(resourceId="com.hexin.plat.android:id/che_sell_tv"),
    }
    node = nodes[opt]

    x = XPath(d)
    x.dump_hierarchy()
    elements = x.xpath('//*[@resource-id="com.hexin.plat.android:id/chedan_recycler_view"]/android.widget.LinearLayout')
    count = len(elements)
    if count == 0:
        logger.warning(f'count == 0, {count=}')
        return {}, {}

    # 滚动到指定位置
    root = d(resourceId="com.hexin.plat.android:id/chedan_recycler_view")
    root.scroll.to(text='全撤')
    if not node.wait(exists=True, timeout=2.0):
        raise Exception("找不到 ['全撤', '撤买', '撤卖'] 三个按钮。请单笔委托撤单")
        # logger.warning("找不到 ['全撤', '撤买', '撤卖'] 三个按钮。请单笔委托撤单")
        # return {}, {}

    node.click()
    confirm = {}
    prompt = {}
    # 有两种情况。1. 撤单确认 2. 不支持批量撤单
    if _wait_cancel_multiple(d):
        x.dump_hierarchy()
        # 1. 撤单确认
        confirm = _confirm_cancel_multiple(x)
        logger.info(confirm)
        if debug:
            _dialog2_select(x, 0)
        else:
            _dialog2_select(x, 1)
    else:
        x.dump_hierarchy()
        # 2. 不支持批量撤单
        prompt = _dialog_content(x)
        logger.warning(prompt)
        _dialog2_select(x, 1)

    return confirm, prompt


def _wait_cancel_single(d: u2.Device) -> bool:
    """检查是弹出单笔委托撤单的三选择，还是无反应"""
    return d(resourceId="com.hexin.plat.android:id/option_cancel").wait(exists=True, timeout=2.0)


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

    root = d(resourceId="com.hexin.plat.android:id/scrollView")
    root.wait(exists=True, timeout=6.0)
    root.fling.toBeginning()
    root.fling.toBeginning()

    x = XPath(d)

    found = -1
    while not x.same_hierarchy():
        x.dump_hierarchy()
        list1, list2, last_status = _orders_in_view(x)
        # 这里的位置从1开始
        for idx, order_ in zip(list1, list2):
            tup = tuple([j for i, j in zip(inside_mask, order_) if i])
            if order == tup:
                if order_is_done(order_[-1]):
                    raise Exception(f'状态已完成，不可再撤, {idx=}, {order_=}')
                    # logger.warning(f'状态已完成，不可再撤, {idx=}, {order_=}')
                    # return {}, {}
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
    node.click(timeout=2.0)

    # 两种情况：1. 弹出撤单确认对话框。 2. 灰了点击无反应
    if _wait_cancel_single(d):
        x = XPath(d)
        x.dump_hierarchy()

        # 1. 弹出撤单确认对话框
        confirm = _confirm_cancel_single(x)
        logger.info(confirm)
        if debug:
            # 取消
            _dialog3_cancel_single_select(x, 2)
        else:
            # 撤单。建议之后再查一下委托列表进行状态更新
            _dialog3_cancel_single_select(x, 0)
    else:
        # 2. 灰了点击无反应
        confirm = {}
    # 为与全撤输出统一
    return confirm, {}


btn_transaction = (0, 0)


def _place_order(d: u2.Device, qty: int, price: float, symbol: str, code: str) -> Dict[str, str]:
    """下单动作。输入股票代码、股票名称、缩写都可以。只要在键盘精灵中排第一即可"""
    # 利用了nan的特点
    not_nan = price == price
    # 输入参数类型修正
    stockprice = str(price)
    stockvolume = str(qty)
    stockcode = str(code or symbol)  # 取其中可用的

    # 等特定对象出现
    node = d(resourceId="com.hexin.plat.android:id/auto_stockcode")
    node.wait(exists=True, timeout=6.0)  # 可能有点问题，等待久一点试试

    x = XPath(d)

    # TODO: 为何这个点还没出现，可能是网络卡了？
    auto_stockcode = (0, 0)
    for i in range(3):
        if auto_stockcode == (0, 0):
            x.dump_hierarchy()
            auto_stockcode = x.center('//*[@resource-id="com.hexin.plat.android:id/auto_stockcode"]/@bounds')
            if i > 0:
                time.sleep(0.5)
        else:
            # 从这跳出，表示成功
            break
    # 点击后弹出键盘精灵
    x.click(*auto_stockcode)

    # 等待键盘精灵出现并输入
    node = d(resourceId="com.hexin.plat.android:id/dialogplus_view_container").child(className='android.widget.EditText')
    node.wait(exists=True, timeout=2.0)
    x.set_text(node, stockcode)  # 这里输入后，可能网络慢，还是已有持仓。特别是在前几笔网络还没有刷新时

    # 如何等待更新和关闭
    # 键盘精灵中第一条。断网情况下第一条可能不更新，导致选择错误，但下单也会失败，所以不会有严重后果
    node = d(resourceId="com.hexin.plat.android:id/stockcode_tv")

    # 等到数量稳定了才停才下，表示已经不更新了
    last_count = -1
    curr_count = node.count
    while last_count != curr_count:
        # print(last_count, curr_count)
        time.sleep(0.5)
        last_count = curr_count
        curr_count = node.count

    # 有可能出现curr_count==0的情况。可能是之前已经是当前股票了，所以自动点击了确认
    if curr_count > 0:
        if code is not None:
            # 设置了code，就得对比。会降速
            text = node.get_text()
            node.click(timeout=2.0)
            assert code == text, f'{code=}, {text=}, 检测到输入代码与自动完成代码不对应，请检查'
        else:
            node.click(timeout=2.0)

    # 先数量
    node = d(resourceId="com.hexin.plat.android:id/stockvolume").child(className="android.widget.EditText")
    try:
        node.wait(exists=True, timeout=2.0)
        x.set_text(node, stockvolume)
    except u2.exceptions.UiObjectNotFoundError:
        x.dump_hierarchy()
        # {'标题': '系统信息', '内容': '股票代码不存在'}
        prompt = _dialog_prompt(x)
        logger.info(prompt)
        _dialog2_select(x, 1)
        return prompt

    # 再价格。后写入。等着软件自动写入后再写入
    if not_nan:
        node = d(resourceId="com.hexin.plat.android:id/stockprice").child(className="android.widget.EditText")
        x.set_text(node, stockprice)

    # 在显示分辨率不同时，可能导致点击不到，但第二次又能点击到，所以初始化时这个按钮还没有完全生成，所以需要第二次操作
    global btn_transaction
    for i in range(3):
        if btn_transaction == (0, 0):
            x.dump_hierarchy()
            btn_transaction = x.center('//*[@resource-id="com.hexin.plat.android:id/btn_transaction"]/@bounds')
            if i > 0:
                time.sleep(0.5)
        else:
            # 从这跳出，表示成功
            break
    # 点击下单
    x.click(*btn_transaction)

    return {}


def _place_order_auto(d: u2.Device, qty: int, price: float, symbol: str, code: str, debug: bool, skip_popup: bool) -> Tuple[Dict[str, str], Dict[str, str]]:
    """下单后，自动进行之后的各项点击与确认"""
    confirm = {}
    prompt = _place_order(d, qty, price, symbol, code)
    if len(prompt) > 0:
        return {}, prompt

    if skip_popup:
        # 跳过了自动点击功能，需交由第三方工具进行后面的点击操作，如`李跳跳`
        return confirm, prompt

    x = XPath(d)
    _wait_confirm_order(d)
    x.dump_hierarchy()

    # 1. 直接提示不合法
    # 2. 委托确认
    if x.exists('//*[@resource-id="com.hexin.plat.android:id/cancel_btn"]'):
        confirm = _confirm_order(x)
        # {'标题': '委托卖出确认', '账户': 'A123456', '名称': '华海药业', '代码': '600521', '数量': 1, '价格': 100.0}
        logger.info(confirm)

        if debug:
            _dialog2_select(x, 0)
        else:
            # 确认下单
            _dialog2_select(x, 1)
            # {'标题': '系统信息', '内容': '股票余额不足 ,不允许卖空'}
            # {'标题': '系统信息', '内容': '卖出数量必须是100的整数倍'}
            # {'标题': '系统信息', '内容': '委托已提交，合同号为：3672041198'}

            # 这里只是起到等待按钮的功能,不检查后面的操作
            _wait_confirm_order(d)  # TODO: 这步慢1s，如何提速？
            x.dump_hierarchy()

            prompt = _dialog_prompt(x)
            logger.info(prompt)
            _dialog2_select(x, 1)
    else:
        # {'标题': '系统信息', '内容': '委托价格不合法，请重新输入'}
        # {'标题': '系统信息', '内容': '委托数量必须大于0'}
        prompt = _dialog_prompt(x)
        logger.info(prompt)
        _dialog2_select(x, 1)
    # 返回个两个字典。出错时，第一个字典为空
    return confirm, prompt


def _wait_confirm_order(d: u2.Device) -> bool:
    """委托确认对话框检查。等待后再dump"""
    return d(resourceId="com.hexin.plat.android:id/ok_btn").wait(exists=True, timeout=2.0)


def _confirm_order(x: XPath) -> Dict[str, str]:
    """委托确认"""
    t = x.xpath('//*[@resource-id="com.hexin.plat.android:id/dialog_layout"]/descendant::android.widget.TextView/@text')
    t = ['标题'] + t
    return dict(zip(t[::2], t[1::2]))


def _confirm_cancel_single(x: XPath) -> Dict[str, str]:
    """撤单确认"""
    path1 = '//*[@resource-id="com.hexin.plat.android:id/title_view"]/@text'
    path2 = '//*[@resource-id="com.hexin.plat.android:id/content_layout"]/descendant::android.widget.TextView/@text'
    t = x.xpath(f'{path1} | {path2}')
    t[0] = '标题  ' + t[0]  # 强行在第0位置加标题
    t = t[:-1]  # 去了最后一行的 '您是否确认以上撤单？'
    return {i[:2]: i[4:] for i in t}


def _dialog3_cancel_single_select(x: XPath, opt: int = 0) -> None:
    nodes = {
        0: '//*[@resource-id="com.hexin.plat.android:id/option_chedan"]/@bounds',
        1: '//*[@resource-id="com.hexin.plat.android:id/option_chedan_and_buy"]/@bounds',
        2: '//*[@resource-id="com.hexin.plat.android:id/option_cancel"]/@bounds',
    }
    x.click(*x.center(nodes[opt]))


def _dialog2_select(x: XPath, opt: int = 1) -> None:
    nodes = {
        0: '//*[@resource-id="com.hexin.plat.android:id/cancel_btn"]/@bounds',
        1: '//*[@resource-id="com.hexin.plat.android:id/ok_btn"]/@bounds',
    }
    x.click(*x.center(nodes[opt]))


def buy(d: u2.Device, qty: int, price: float, symbol: str, code: str, debug: bool, skip_popup: bool) -> Tuple[Dict[str, str], Dict[str, str]]:
    return _place_order_auto(d, qty, price, symbol, code, debug, skip_popup)


def sell(d: u2.Device, qty: int, price: float, symbol: str, code: str, debug: bool, skip_popup: bool) -> Tuple[Dict[str, str], Dict[str, str]]:
    return _place_order_auto(d, qty, price, symbol, code, debug, skip_popup)
