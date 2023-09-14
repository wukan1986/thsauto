"""
TODO: 因为这套方案还有问题，所以先不上线
"""
from robyn import Robyn, jsonify

from thsauto import THS

t = THS(debug=False, skip_popup=False)

app = Robyn(__file__)


@app.exception
def handle_exception(error):
    e = {error.__class__.__name__: str(error)}
    return jsonify(e)


@app.get("/connect")
def connect(request):
    addr = request.queries.get('addr', "emulator-5554")
    return jsonify(t.connect(addr))


@app.get("/get_balance")
def get_balance(request):
    return jsonify(t.get_balance())


@app.get("/get_positions")
def get_positions(request):
    return jsonify(t.get_positions().to_dict('split'))


@app.get("/get_orders")
def get_orders(request):
    break_after_done = bool(request.queries.get('break_after_done', False))

    return jsonify(t.get_orders(break_after_done=break_after_done).to_dict('split'))


@app.get("/order_at/:idx")
def order_at(request):
    idx = int(request.path_params.get('idx', 0))

    return jsonify(t.order_at(idx))


@app.get("/buy")
def buy(request):
    qty = int(request.queries.get('qty', 0))
    price = float(request.queries.get('price', 'nan'))
    code = request.queries.get('code', '')

    return jsonify(t.buy(qty, price, code=code))


@app.get("/sell")
def buy(request):
    qty = int(request.queries.get('qty', 0))
    price = float(request.queries.get('price', 'nan'))
    code = request.queries.get('code', '')

    return jsonify(t.sell(qty, price, code=code))


@app.get("/cancels/:opt")
def cancels(request):
    opt = request.path_params.get('opt', 'all')

    return jsonify(t.cancel_multiple(opt))


@app.get("/cancel/:idx")
def cancel(request):
    idx = int(request.path_params.get('idx', 0))

    return jsonify(t.cancel_single(t.order_at(idx)))


# TODO: 这为何有时生效，有时不生效
app.add_response_header("content-type", "application/json; charset=UTF-8")
app.start(port=5000, url="0.0.0.0")
