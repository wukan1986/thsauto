# thsauto
同花顺Android版模拟炒股自动化测试封装

## 目标用户
只适合资金量少的散户。自动化测试技术速度慢，稳定性也一般，达不到专业人市的要求。

资金量大的个人或机构，请使用专业软件。如：迅投QMT、恒生PTrade、掘金量化、卡方科技等，或券商自研软件。
它们带扫文件单功能，能实现批量委托，速度更快。注意：软件虽支持，但券商可能不开放扫单权限，请提前向客户经理认真确认。

## 起源
[THSTrader](https://github.com/nladuo/THSTrader) 项目代码优化不够，安装了大量库效率低。所以决定学习后重写。

## 对比
### [easytrader](https://github.com/shidenggui/easytrader)
1. 原理：`pywinauto`进行鼠标键盘模拟
2. 优点：PC版客户端可以设置省略弹出框，所以委托速度还行。下一笔约1~2秒，但赶不上专用软件的扫单功能。
3. 缺点：PC版新客户端复制列表时需要输入验证码，由于鼠标键盘占用，所以得独占电脑
### [THSTrader](https://github.com/nladuo/THSTrader)
1. 原理：使用Google的`UIAutomator`技术进行辅助控制。使用`easyocr`对截图进行文本识别
2. 优点：Android版比PC版支持的券商更多
3. 缺点：截图识别效率太低、速度慢。截图对位置大小有要求，分辨率不能随意改动。依赖`pytorch`等库，还需外网下载识别模型。
### [thsauto](https://github.com/wukan1986/thsauto)
1. 原理：使用Google的`UIAutomator`技术进行辅助控制。使用`XPath`进行文字提取，跳过了文本识别
2. 优点：支持的券商多。支持本地和远程，不占用鼠标键盘，不独占电脑
3. 缺点：Android版客户端没有跳过弹出对话框的设置，所以速度要慢于PC版。下一笔约6~7秒

- 下单耗时(越小越好)：easytrader < thsauto <= THSTrader
- 查询耗时(越小越好)：easytrader < thsauto << THSTrader
- 市场占有率(越大越好)：Android > PC，所以在不能使用easytrader的情况下也许能用thsauto/THSTrader

## `uiautomator2`的局限
1. 查询界面时，不可见部分查询不到，需要滑动实现
2. 无法遍历列表控件，通过滑动变通实现，很难保证不重复、不遗漏
3. 持仓列表不会重复，委托列表由于报单速度慢，重复的可能性小
4. 设置分辨率长屏，同时显示更多行，需要滑动的次数少，能缓解此局限

## 安装
以下安装方法参考于`THSTrader`项目
```commandline
pip install -U thsauto
```
或二次开发
```commandline
git clone --depth=1 https://github.com/wukan1986/thsauto.git
cd thsauto
pip install -e .
```

## 安装雷电9模拟器
下载页：https://ldmnq.com/other/version-history-and-release-notes.html  
安装包名类似于`ldinst_9.0.57.2.exe`（约500MB）而不是`ldplayer9_ld_112_ld.exe`（约3MB）

## 模拟器设置分辨率
1. 软件设置 -> 性能设置 -> 手机版 ->720*1280(dpi 320)
    - 此分变率在`weditor`显示中正好匹配，可用于二次开发。
2. 自定义-> 360*1500(dpi 180)
    - 实盘时，此分变率在本人电脑`2560*1600`下比较合适
    - 宽360小于720，字体也就小，界面中可以显示更多行
    - 高1500小于1600，能显示更多行，又能防止长屏过长时软件界面压缩导致界面模糊
    - dpi 120与dpi 180显示的委托列表行数一样多，目前使用的dpi 180
    
## 安装同花顺APP
下载页：https://m.10jqka.com.cn/ 右上角按钮进行下载。需下载Android版(文件扩展名为`apk`)

## 安装配置ADB(初级用户可不做)
将安装路径 `D:\leidian\LDPlayer9`，添加到`环境变量`后就可以在控制台中使用`adb`命令了

## 测试连接模拟器(可不做)
查看模拟器设备名，一般默认值为`emulator-5554`
```commandline
adb kill-server
adb devices
```
初始化`uiautomator2`。1.3.0之后的版本已经不需要执行此步了，在`u2.connect`时会自动推送相关文件
```commandline
python -m uiautomator2 init
```

## 演示
本自动化测试工具没有`登录`和`切换账号`功能，所以需要用户自己先打开指定界面。
1. 打开同花顺APP
2. 最下导航栏 -> 交易
3. 最上导航栏 -> 模拟
4. 点击中间区域（买入、卖出、撤单、持仓、查询）五个图标按钮中任意一个，即可进入交易界面
5. 注意：在任何步骤执行完毕，都不应当出现弹出对话框未关闭的情况，否则会阻断之后的执行。如果遇到能复现错误，请截图并保留日志

### VSCode运行[demo示例](examples/demo.py)
```python
from thsauto import THS

# 初次使用请在`debug=True`模式下多测试几次
t = THS(debug=True)
t.connect(addr="emulator-5554")

# 资产
t.get_balance()
"""
{'总资产': 200202.81,
 '浮动盈亏': 202.81,
 '当日参考盈亏': 89.01,
 '当日参考盈亏率': 0.0004,
 '持仓市值': 12454.0,
 '可用资金': 172459.9,
 '可取资金': 0.0}
"""

# 持仓
t.get_positions()
"""
	名称	市值	盈亏	盈亏率	持仓	可用	成本	现价
0	美的集团	5526.0	2.23	0.00040	100	100	55.238	55.26
1	招商银行	3156.0	11.00	0.00350	100	100	31.450	31.56
2	万科A	2688.0	196.92	0.07908	200	0	12.455	13.44
3	贵州轮胎	705.0	-5.22	-0.00730	100	100	7.102	7.05
4	中国银行	379.0	-2.12	-0.00560	100	100	3.811	3.79
"""

# 委托
t.get_orders(break_after_done=True)
"""
名称	委托时间	委托价	成交均价	委托量	已成交量	买卖	状态
0	浦发银行	21:16:56	5.00	0.0	100	0	买入	未成交
1	浦发银行	21:14:41	10.50	0.0	100	0	买入	未成交
2	浦发银行	10:07:39	10.50	0.0	100	0	买入	未成交
3	浦发银行	02:15:10	10.50	0.0	100	0	买入	未成交
4	浦发银行	01:50:09	10.50	0.0	100	0	买入	未成交
5	万科A	22:10:22	10.00	0.0	100	0	卖出	未成交
6	万科A	21:48:15	15.00	0.0	100	0	卖出	未成交
7	白云机场	16:58:46	11.76	0.0	200	0	买入	未成交
8	白云机场	16:26:47	11.76	0.0	100	0	买入	未成交
9	白云机场	16:58:37	11.76	0.0	100	0	买入	全部撤单
10	白云机场	16:27:05	11.76	0.0	200	0	买入	全部撤单
"""

# 委托。未处理的原始数据
t.orders
"""
[('浦发银行', '21:16:56', '5.000', '0.000', '100', '0', '买入', '未成交'),
 ('浦发银行', '21:14:41', '10.500', '0.000', '100', '0', '买入', '未成交'),
 ('浦发银行', '10:07:39', '10.500', '0.000', '100', '0', '买入', '未成交'),
 ('浦发银行', '02:15:10', '10.500', '0.000', '100', '0', '买入', '未成交'),
 ('浦发银行', '01:50:09', '10.500', '0.000', '100', '0', '买入', '未成交'),
 ('万  科 A', '22:10:22', '10.000', '0.000', '100', '0', '卖出', '未成交'),
 ('万  科 A', '21:48:15', '15.000', '0.000', '100', '0', '卖出', '未成交'),
 ('白云机场', '16:58:46', '11.760', '0.000', '200', '0', '买入', '未成交'),
 ('白云机场', '16:26:47', '11.760', '0.000', '100', '0', '买入', '未成交'),
 ('白云机场', '16:58:37', '11.760', '0.000', '100', '0', '买入', '全部撤单'),
 ('白云机场', '16:27:05', '11.760', '0.000', '200', '0', '买入', '全部撤单')]
"""

# 支持股票代码
confirm, prompt = t.buy('600000', 5, 100)
confirm, prompt
"""
({'标题': '委托买入确认',
  '账户': 'A516832234',
  '名称': '浦发银行',
  '代码': '600000',
  '数量': 100,
  '价格': 5.0},
 {'标题': '系统信息', '内容': '委托已提交，合同号为：3672942466'})
"""

# 撤第一条
confirm, prompt = t.cancel_single(t.order_at(0))
confirm, prompt
"""
({'标题': '委托撤单确认',
  '操作': '撤买入单',
  '名称': '浦发银行',
  '代码': '600000',
  '数量': 100,
  '价格': 5.0},
 {})
"""
```