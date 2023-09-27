"""
本代码演示在聚宽中如何向云服务器上报单

云服务端
1. 在Windows云服务器上安装雷电模拟器、Python等必备环境
2. 执行`thsauto run --host=0.0.0.0 --port=5000`
3. 云服务器厂商的管理控制台上开启对应的`5000`端口
4. 记录服务器的`IP`备用

聚宽端
1. 复制`thsauto/cli.py`文件到`研究环境`可以在Notebook中直接调用
2. 将`thsauto/cli.py`文件中的**代码**复制到策略开头，也可直接调用

测试
1. `cli.py`中只是用`requests`发起的`HTTP`请求，代码非常简单，可自行阅读修改
2. 可先在聚宽Notebook中测试，将交易代码调试通后再复制到聚宽策略中
"""
import thsauto.cli as t

t._URL = "http://127.0.0.1:5000"
# 替换成云服务器的地址和端口号
t._URL = "http://123.123.123.123:5000"

print(t.connect(addr="emulator-5554"))

print(t.get_balance())

print(t.get_positions())

print(t.sell(100, code='000001'))

print(t.get_orders())

print(t.cancel(0))
