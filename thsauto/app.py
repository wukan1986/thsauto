import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from thsauto import THS

t = THS(debug=False, skip_popup=False)

app = FastAPI()


@app.exception_handler(Exception)
async def exception_handler(request, exc):
    e = {exc.__class__.__name__: str(exc)}
    return JSONResponse(e, status_code=500)


@app.get("/connect")
async def connect(addr: str = "emulator-5554"):
    return t.connect(addr)


@app.get("/get_balance")
async def get_balance():
    return t.get_balance()


@app.get("/get_positions")
async def get_positions():
    return t.get_positions().to_dict('split')


@app.get("/get_orders")
async def get_orders(break_after_done: bool = False):
    return t.get_orders(break_after_done=break_after_done).to_dict('split')


@app.get("/order_at/{idx}")
async def order_at(idx: int = 0):
    return t.order_at(idx)


@app.get("/buy")
def buy(qty: int = 0, price: float = float('nan'), code: str = ''):
    return t.buy(qty, price, code=code)


@app.get("/sell")
def sell(qty: int = 0, price: float = float('nan'), code: str = ''):
    return t.sell(qty, price, code=code)


@app.get("/cancels/{opt}")
def cancels(opt: str = 'all'):
    return t.cancel_multiple(opt)


@app.get("/cancel/{idx}")
def cancel(idx: int = 0):
    return t.cancel_single(t.order_at(idx))


if __name__ == "__main__":
    uvicorn.run(app, host='127.0.0.1', port=5000)
