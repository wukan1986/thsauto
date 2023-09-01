from thsauto import THS

t = THS(debug=True, skip_popup=False)
t.connect(addr="emulator-5554")

code = 600700  # 600000 # 000001
price = float('nan')  # nan表示使用界面自动填充的对手价
qty = 100

# 遍历卖出，方便查看性能
for r in range(10):
    code += 1
    price += 1
    qty += 2
    print('=' * 20, code, price, qty)
    try:
        confirm, prompt = t.sell(qty, price=price, code=f'{code:06d}', debug=True)
        print(confirm, prompt)
    except AssertionError as e:
        print(e)
