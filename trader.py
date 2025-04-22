
from binance.enums import *
from binance.exceptions import BinanceAPIException

def place_order_customizado(client, symbol, side, preco_entrada, stop_loss, alavancagem):
    try:
        close_all_positions(client, symbol)
        client.futures_cancel_all_open_orders(symbol=symbol)
        client.futures_change_leverage(symbol=symbol, leverage=alavancagem)

        price = float(client.futures_symbol_ticker(symbol=symbol)['price'])
        quantity = calculate_quantity(client, symbol, price, alavancagem)

        if quantity <= 0:
            print("❌ Quantidade inválida.")
            return

        order = client.futures_create_order(
            symbol=symbol,
            side=side,
            type=ORDER_TYPE_MARKET,
            quantity=quantity
        )

        entry_price = float(client.futures_position_information(symbol=symbol)[0]['entryPrice'])
        roi = 1.0

        tp_price = round(entry_price * (1 + roi / alavancagem), 4) if side == SIDE_BUY else round(entry_price * (1 - roi / alavancagem), 4)
        tp_side = SIDE_SELL if side == SIDE_BUY else SIDE_BUY

        client.futures_create_order(
            symbol=symbol,
            side=tp_side,
            type=FUTURE_ORDER_TYPE_TAKE_PROFIT_MARKET,
            stopPrice=str(tp_price),
            closePosition=True,
            timeInForce=TIME_IN_FORCE_GTC
        )

        client.futures_create_order(
            symbol=symbol,
            side=tp_side,
            type=FUTURE_ORDER_TYPE_STOP_MARKET,
            stopPrice=str(stop_loss),
            closePosition=True,
            timeInForce=TIME_IN_FORCE_GTC
        )

        print(f"✅ Ordem {side} executada: {symbol} | SL: {stop_loss} | TP: {tp_price} | QTD: {quantity}")
    except BinanceAPIException as e:
        print(f"❌ Erro Binance: {e}")

def close_all_positions(client, symbol):
    positions = client.futures_position_information(symbol=symbol)
    for position in positions:
        amt = float(position['positionAmt'])
        if amt != 0:
            side = SIDE_SELL if amt > 0 else SIDE_BUY
            client.futures_create_order(
                symbol=symbol,
                side=side,
                type=ORDER_TYPE_MARKET,
                quantity=abs(amt),
                reduceOnly=True
            )

def calculate_quantity(client, symbol, price, leverage):
    balance = get_futures_balance(client)
    if balance <= 0:
        return 0.0

    info = client.futures_exchange_info()
    symbol_info = next(s for s in info['symbols'] if s['symbol'] == symbol)
    lot_size = next(f for f in symbol_info['filters'] if f['filterType'] == 'LOT_SIZE')
    step_size = float(lot_size['stepSize'])

    notional = balance * leverage
    qty = notional / price
    qty = qty // step_size * step_size
    return round(qty, 8)

def get_futures_balance(client):
    balance = client.futures_account_balance()
    for asset in balance:
        if asset['asset'] == 'USDT':
            return float(asset['availableBalance']) * 0.9
    return 0.0
