# %%
# 用VSCode打开后，可直接用`Shift+Enter`分块执行
# 也可以复制到Notebook中执行
# %%
from thsauto import THS

# 初次使用请在`debug=True`模式下多测试几次
# 再次测试在模拟炒股下再开启`debug=False`
# 然后再在其它账号下`debug=True`模式下测试
# 最后是其它账号下`debug=False`下交易
t = THS(debug=True, skip_popup=False)
t.connect(addr="emulator-5554")
# t.connect(addr="38edccd4")
# t.connect(addr="192.168.31.20:40851")

# %%
# 可事后再改成可以下单，也可以在下单函数中指定
# t.debug = False
# %%
t.refresh()
# %%
# 资产
balance = t.get_balance()
balance
# %%
# 持仓
positions = t.get_positions()
positions
# %%
# 委托
orders = t.get_orders(break_after_done=True)
orders
# %%
# 委托。未处理的原始数据
t.orders
# %%
# 支持股票代码
confirm, prompt = t.buy(-100, 5, code='600000')
confirm, prompt
# %%
# 支持股票名称。只要在键盘精灵中排第一即可
confirm, prompt = t.sell('300', '11', symbol='万科A', debug=True)
confirm, prompt

# %%
# 支持拼音缩写。只要在键盘精灵中排第一即可
confirm, prompt = t.sell(200, float('nan'), symbol='gzmt', skip_popup=True)
confirm, prompt

# %%
# 撤第一条
confirm, prompt = t.cancel_single(t.order_at(0))
confirm, prompt

# %%
# 撤卖
confirm, prompt = t.cancel_multiple('buy')
confirm, prompt
# %%
# 全撤
confirm, prompt = t.cancel_multiple('all', debug=False)
confirm, prompt

# %%
confirm, prompt = t.cancel_multiple('sell')
confirm, prompt

# %%
