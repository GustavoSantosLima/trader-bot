# Importações necessárias
from keys import api, secret
from binance.um_futures import UMFutures
import ta
import pandas as pd
from time import sleep
from binance.error import ClientError

# Inicialização do cliente
client = UMFutures(key=api, secret=secret)

# 0.012 significa +1,2%, 0.009 é -0,9%
tp = 0.012
sl = 0.009
volume = 10  # volume para uma ordem (se for 10 e a alavancagem for 10, então você coloca 1 USDT para uma posição)
leverage = 5
type = 'ISOLATED'  # tipo é 'ISOLATED' ou 'CROSS'
qty = 2  # Quantidade de posições abertas simultaneamente

# obtendo seu saldo de futuros em USDT
def get_balance_usdt():
    try:
        response = client.balance(recvWindow=6000)
        for elem in response:
            if elem['asset'] == 'USDT':
                return float(elem['balance'])

    except ClientError as error:
        print(
            "Erro encontrado. status: {}, código de erro: {}, mensagem de erro: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )

# Obtendo todos os símbolos disponíveis nos Futuros ('BTCUSDT', 'ETHUSDT', ....)
def get_tickers_usdt():
    tickers = []
    resp = client.ticker_price()
    for elem in resp:
        if 'USDT' in elem['symbol']:
            tickers.append(elem['symbol'])
    return tickers

# Obtendo velas para o símbolo necessário, é um dataframe com 'Time', 'Open', 'High', 'Low', 'Close', 'Volume'
def klines(symbol):
    try:
        resp = pd.DataFrame(client.klines(symbol, '15m'))
        resp = resp.iloc[:,:6]
        resp.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
        resp = resp.set_index('Time')
        resp.index = pd.to_datetime(resp.index, unit = 'ms')
        resp = resp.astype(float)
        return resp
    except ClientError as error:
        print(
            "Erro encontrado. status: {}, código de erro: {}, mensagem de erro: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )

# Definir alavancagem para o símbolo necessário. Você precisa disso porque diferentes símbolos podem ter alavancagem diferente
def set_leverage(symbol, level):
    try:
        response = client.change_leverage(
            symbol=symbol, leverage=level, recvWindow=6000
        )
        print(response)
    except ClientError as error:
        print(
            "Erro encontrado. status: {}, código de erro: {}, mensagem de erro: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )

# O mesmo para o tipo de margem
def set_mode(symbol, type):
    try:
        response = client.change_margin_type(
            symbol=symbol, marginType=type, recvWindow=6000
        )
        print(response)
    except ClientError as error:
        print(
            "Erro encontrado. status: {}, código de erro: {}, mensagem de erro: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )

# Precisão do preço. BTC tem 1, XRP tem 4
def get_price_precision(symbol):
    resp = client.exchange_info()['symbols']
    for elem in resp:
        if elem['symbol'] == symbol:
            return elem['pricePrecision']

# Precisão do montante. BTC tem 3, XRP tem 1
def get_qty_precision(symbol):
    resp = client.exchange_info()['symbols']
    for elem in resp:
        if elem['symbol'] == symbol:
            return elem['quantityPrecision']

# Abrir nova ordem com o último preço e definir TP e SL:
def open_order(symbol, side):
    price = float(client.ticker_price(symbol)['price'])
    qty_precision = get_qty_precision(symbol)
    price_precision = get_price_precision(symbol)
    qty = round(volume/price, qty_precision)
    if side == 'buy':
        try:
            resp1 = client.new_order(symbol=symbol, side='BUY', type='LIMIT', quantity=qty, timeInForce='GTC', price=price)
            print(symbol, side, "colocando ordem")
            print(resp1)
            sleep(2)
            sl_price = round(price - price*sl, price_precision)
            resp2 = client.new_order(symbol=symbol, side='SELL', type='STOP_MARKET', quantity=qty, timeInForce='GTC', stopPrice=sl_price)
            print(resp2)
            sleep(2)
            tp_price = round(price + price * tp, price_precision)
            resp3 = client.new_order(symbol=symbol, side='SELL', type='TAKE_PROFIT_MARKET', quantity=qty, timeInForce='GTC', stopPrice=tp_price)
            print(resp3)
        except ClientError as error:
            print(
                "Erro encontrado. status: {}, código de erro: {}, mensagem de erro: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )
    if side == 'sell':
        try:
            resp1 = client.new_order(symbol=symbol, side='SELL', type='LIMIT', quantity=qty, timeInForce='GTC', price=price)
            print(symbol, side, "colocando ordem")
            print(resp1)
            sleep(2)
            sl_price = round(price + price*sl, price_precision)
            resp2 = client.new_order(symbol=symbol, side='BUY', type='STOP_MARKET', quantity=qty, timeInForce='GTC', stopPrice=sl_price)
            print(resp2)
            sleep(2)
            tp_price = round(price - price * tp, price_precision)
            resp3 = client.new_order(symbol=symbol, side='BUY', type='TAKE_PROFIT_MARKET', quantity=qty, timeInForce='GTC', stopPrice=tp_price)
            print(resp3)
        except ClientError as error:
            print(
                "Erro encontrado. status: {}, código de erro: {}, mensagem de erro: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )

# Suas posições atuais (retorna a lista de símbolos):
def get_pos():
    try:
        resp = client.get_position_risk()
        pos = []
        for elem in resp:
            if float(elem['positionAmt']) != 0:
                pos.append(elem['symbol'])
        return pos
    except ClientError as error:
        print(
            "Erro encontrado. status: {}, código de erro: {}, mensagem de erro: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )

# Todas as ordens abertas (retorna a lista de símbolos):
def check_orders():
    try:
        response = client.get_orders(recvWindow=6000)
        sym = []
        for elem in response:
            sym.append(elem['symbol'])
        return sym
    except ClientError as error:
        print(
            "Erro encontrado. status: {}, código de erro: {}, mensagem de erro: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )

# Fechar ordens abertas para o símbolo necessário. Se uma ordem de stop for executada e outra ainda estiver lá
def close_open_orders(symbol):
    try:
        response = client.cancel_open_orders(symbol=symbol, recvWindow=6000)
        print(response)
    except ClientError as error:
        print(
            "Erro encontrado. status: {}, código de erro: {}, mensagem de erro: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )

# Estratégia. Pode usar qualquer outra:
def str_signal(symbol):
    kl = klines(symbol)
    rsi = ta.momentum.RSIIndicator(kl.Close).rsi()
    rsi_k = ta.momentum.StochRSIIndicator(kl.Close).stochrsi_k()
    rsi_d = ta.momentum.StochRSIIndicator(kl.Close).stochrsi_d()
    ema = ta.trend.ema_indicator(kl.Close, window=200)
    if rsi.iloc[-1] < 40 and ema.iloc[-1] < kl.Close.iloc[-1] and rsi_k.iloc[-1] < 20 and rsi_k.iloc[-3] < rsi_d.iloc[-3] and rsi_k.iloc[-2] < rsi_d.iloc[-2] and rsi_k.iloc[-1] > rsi_d.iloc[-1]:
        return 'up'
    if rsi.iloc[-1] > 60 and ema.iloc[-1] > kl.Close.iloc[-1] and rsi_k.iloc[-1] > 80 and rsi_k.iloc[-3] > rsi_d.iloc[-3] and rsi_k.iloc[-2] > rsi_d.iloc[-2] and rsi_k.iloc[-1] < rsi_d.iloc[-1]:
        return 'down'
    else:
        return 'none'

# Estrategia Baseada no indicador RSI (Índice de Força Relativa) e na média móvel exponencial de 200 períodos (EMA).
def rsi_signal(symbol):
    kl = klines(symbol)
    rsi = ta.momentum.RSIIndicator(kl.Close).rsi()
    ema = ta.trend.ema_indicator(kl.Close, window=200)
    if rsi.iloc[-2] < 30 and rsi.iloc[-1] > 30:
        return 'up'
    if rsi.iloc[-2] > 70 and rsi.iloc[-1] < 70:
        return 'down'
    else:
        return 'none'

# ----------------- xxx -----------------
def macd_ema(symbol):
    kl = klines(symbol)
    macd = ta.trend.macd_diff(kl.Close)
    ema = ta.trend.ema_indicator(kl.Close, window=200)
    if macd.iloc[-3] < 0 and macd.iloc[-2] < 0 and macd.iloc[-1] > 0 and ema.iloc[-1] < kl.Close.iloc[-1]:
        return 'up'
    if macd.iloc[-3] > 0 and macd.iloc[-2] > 0 and macd.iloc[-1] < 0 and ema.iloc[-1] > kl.Close.iloc[-1]:
        return 'down'
    else:
        return 'none'
    
# ----------------- xxx -----------------
def ema200_50(symbol):
    kl = klines(symbol)
    ema200 = ta.trend.ema_indicator(kl.Close, window=100)
    ema50 = ta.trend.ema_indicator(kl.Close, window=50)
    if ema50.iloc[-3] < ema200.iloc[-3] and ema50.iloc[-2] < ema200.iloc[-2] and ema50.iloc[-1] > ema200.iloc[-1]:
        return 'up'
    if ema50.iloc[-3] > ema200.iloc[-3] and ema50.iloc[-2] > ema200.iloc[-2] and ema50.iloc[-1] < ema200.iloc[-1]:
        return 'down'
    else:
        return 'none'

orders = 0
symbol = ''
# obtendo todos os símbolos da lista de Futuros da Binance:
symbols = get_tickers_usdt()

while True:
    # precisamos obter saldo para verificar se a conexão está boa ou se você tem todas as permissões necessárias
    balance = get_balance_usdt()
    sleep(1)
    if balance == None:
        print('Não é possível conectar-se à API. Verifique o IP, as restrições ou espere algum tempo')
    if balance != None:
        print("Meu saldo é: ", balance, " USDT")
        ## obtendo lista de posição:
        pos = []
        pos = get_pos()
        print(f'Você tem {len(pos)} posições abertas:\n{pos}')
        ## Obtendo lista de ordens
        ord = []
        ord = check_orders()
        ## removendo ordens de stop para posições fechadas
        for elem in ord:
            if not elem in pos:
                close_open_orders(elem)
        if len(pos) < qty:
            for elem in symbols:
                # Estratégias (você pode criar a sua própria com a biblioteca TA):
                # signal = str_signal(elem)
                signal = rsi_signal(elem)
                # signal = macd_ema(elem)
                # sinal 'up' ou 'down', colocamos ordens para símbolos que não estão nas posições abertas e ordens
                # também não precisamos de USDTUSDC porque é 1:1 (não precisamos gastar dinheiro com a comissão)
                if signal == 'up' and elem != 'USDCUSDT' and not elem in pos and not elem in ord and elem != symbol:
                    print('Sinal de COMPRA encontrado para ', elem)
                    set_mode(elem, type)
                    sleep(1)
                    set_leverage(elem, leverage)
                    sleep(1)
                    print('Colocando ordem para ', elem)
                    open_order(elem, 'buy')
                    symbol = elem
                    order = True
                    pos = get_pos()
                    sleep(1)
                    ord = check_orders()
                    sleep(1)
                    sleep(10)
                    # break
                if signal == 'down' and elem != 'USDCUSDT' and not elem in pos and not elem in ord and elem != symbol:
                    print('Sinal de VENDA encontrado para ', elem)
                    set_mode(elem, type)
                    sleep(1)
                    set_leverage(elem, leverage)
                    sleep(1)
                    print('Colocando ordem para ', elem)
                    open_order(elem, 'sell')
                    symbol = elem
                    order = True
                    pos = get_pos()
                    sleep(1)
                    ord = check_orders()
                    sleep(1)
                    sleep(10)
                    # break
    print('Aguardando 3 minutos')
    sleep(180)
