# %%
# 用VSCode打开后，可直接用`Shift+Enter`分块执行
# 也可以复制到Notebook中执行
# %%
from thsauto import THS

# 初次使用请在`debug=True`模式下多测试几次
t = THS(debug=True)
t.connect(addr="emulator-5554")
# %%
# 可事后再改成可以下单
# t.debug = False
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
confirm, prompt = t.buy('600000', 5, 100)
confirm, prompt
# %%
# 支持股票名称。只要在键盘精灵中排第一即可
confirm, prompt = t.sell('万科A', 200, 100)
confirm, prompt

# %%
# 支持拼音缩写。只要在键盘精灵中排第一即可
confirm, prompt = t.sell('gzmt', 200, 100)
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
confirm, prompt = t.cancel_multiple('all')
confirm, prompt
# %%

# %%
