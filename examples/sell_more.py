from thsauto import THS

t = THS(debug=True, skip_popup=False)
t.connect(addr="emulator-5554")

i = 600800  # 600000 # 000001
j = 100
k = 200

# 遍历卖出，方便查看性能
for r in range(10):
    i += 1
    j += 1
    k += 1
    print('=' * 20, i, j, k)
    try:
        confirm, prompt = t.sell(j, k, code=f'{i:06d}', debug=True)
        print(confirm, prompt)
    except AssertionError as e:
        print(e)
