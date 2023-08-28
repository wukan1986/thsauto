import pandas as pd


def str2float(s):
    return float(s.replace(',', '').replace('--', '0.0').replace('%', ''))


def str2int(s):
    return int(s.replace(',', '').replace('--', '0'))


def parse_confirm_order(dict_):
    _d = {}
    for k, v in dict_.items():
        t = v.replace(' ', '')
        if k == '数量':
            t = int(t.replace(',', ''))
        if k == '价格':
            t = float(t.replace(',', ''))
        _d[k] = t
    return _d


def parse_confirm_cancel(dict_):
    _d = {}
    for k, v in dict_.items():
        t = v.replace(' ', '')
        if k == '数量':
            t = int(t.replace(',', ''))
        if k == '价格':
            t = float(t.replace(',', ''))
        _d[k] = t
    return _d


def parse_orders(list2):
    df = pd.DataFrame.from_records(list2, columns=['名称', '委托时间', '委托价', '成交均价', '委托量', '已成交量', '买卖', '状态'])

    df = df.apply(lambda x: x.str.replace(',', ''))
    df['名称'] = df['名称'].str.replace(' ', '')

    df[['委托价', '成交均价']] = df[['委托价', '成交均价']].astype(float)
    df[['委托量', '已成交量']] = df[['委托量', '已成交量']].astype(int)
    return df


def parse_positions(list2):
    df = pd.DataFrame.from_records(list2, columns=['名称', '市值', '盈亏', '盈亏率', '持仓', '可用', '成本', '现价'])

    df = df.apply(lambda x: x.str.replace(',', ''))
    df['名称'] = df['名称'].str.replace(' ', '')
    df[['市值', '盈亏', '成本', '现价']] = df[['市值', '盈亏', '成本', '现价']].astype(float)
    df[['持仓', '可用']] = df[['持仓', '可用']].astype(int)
    df['盈亏率'] = df['盈亏率'].str.replace('%', '').astype(float) / 100.0
    return df


def parse_balance(_dict: dict):
    _dict = {k: str2float(v) for k, v in _dict.items()}
    _dict['当日参考盈亏率'] /= 100.
    return _dict
