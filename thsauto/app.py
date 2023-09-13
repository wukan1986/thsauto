from functools import wraps

from flask import Flask, request, jsonify, abort

from thsauto import THS

app = Flask(__name__)
app.json.ensure_ascii = False

# 每次启动时都会导致对象创建重连，所以需要有一个全局的变量
t = THS(debug=False, skip_popup=False)


def catch_exception(f):
    """捕获异常"""

    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            abort(500, description=str(e))

    return decorated


@app.errorhandler(500)
def internal_server_error(e):
    """将错误都转换成json格式"""
    return jsonify(error=str(e)), 500


@app.get("/connect")
@catch_exception
def connect():
    addr = request.args.get('addr', "emulator-5554", str)

    return t.connect(addr)


@app.get("/get_balance")
@catch_exception
def get_balance():
    return t.get_balance()


@app.get("/get_positions")
@catch_exception
def get_positions():
    return t.get_positions().to_dict('split')


@app.get("/get_orders")
@catch_exception
def get_orders():
    break_after_done = request.args.get('break_after_done', False, bool)

    return t.get_orders(break_after_done=break_after_done).to_dict('split')


@app.get("/order_at/<int:idx>")
@catch_exception
def order_at(idx: int):
    return list(t.order_at(idx))


@app.get("/buy")
@catch_exception
def buy():
    qty = request.args.get('qty', 0, int)
    price = request.args.get('price', float('nan'), float)
    code = request.args.get('code', '', str)

    # 不支tuple的json化，所以只能先转成list
    return list(t.buy(qty, price, code=code))


@app.get("/sell")
@catch_exception
def sell():
    qty = request.args.get('qty', 0, int)
    price = request.args.get('price', float('nan'), float)
    code = request.args.get('code', '', str)

    return list(t.sell(qty, price, code=code))


@app.get("/cancels/<opt>")
@catch_exception
def cancels(opt: str):
    return list(t.cancel_multiple(opt))


@app.get("/cancel/<int:idx>")
@catch_exception
def cancel(idx: int):
    return list(t.cancel_single(t.order_at(idx)))


if __name__ == '__main__':
    # host='0.0.0.0', port=5000
    app.run(host=None, port=None, debug=False)
