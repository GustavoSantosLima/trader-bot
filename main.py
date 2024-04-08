# Importações necessárias
import sys
from keys import api, secret
from binance.um_futures import UMFutures # type: ignore
import ta # type: ignore
import pandas as pd # type: ignore
from time import sleep
from binance.error import ClientError # type: ignore
from datetime import datetime

# Inicialização do cliente
client = UMFutures(key=api, secret=secret)

tp = 0.006 # take profit (se você colocar 0.010, então você terá 1,0% de lucro)
sl = 0.004 # stop loss (se você colocar 0.005, então você terá 0,5% de perda) 
volume = 50 # volume para uma ordem (volume / leverage = preço da ordem)
leverage = 10  # alavancagem
margin_mode = 'ISOLATED' # tipo é 'ISOLATED' ou 'CROSS'
qty = 3 # Quantidade de posições abertas simultaneamente
TIME_PERIOD = '5m' # período de tempo para velas
LIMIT_EXIT = 15 # limite de saldo para sair do programa

# obtendo seu saldo de futuros em USDT
def get_balance_usdt():
    try:
        response = client.balance(recvWindow=6000)
        for elem in response:
            if elem['asset'] == 'USDT':
                return float(elem['balance'])
    except ClientError as error:
        print(f"Erro encontrado. status: {error.status_code}, código de erro: {error.error_code}, mensagem de erro: {error.error_message}")

# Obtendo todos os símbolos disponíveis nos Futuros ('BTCUSDT', 'ETHUSDT', ....)
def get_tickers_usdt():
    tickers = []
    resp = client.ticker_price()
    for elem in resp:
        if 'USDT' in elem['symbol'] and '_' not in elem['symbol']:
            tickers.append(elem['symbol'])
    return tickers

# Obtendo velas para o símbolo necessário, é um dataframe com 'Time', 'Open', 'High', 'Low', 'Close', 'Volume'
def klines(symbol):
    try:
        resp = pd.DataFrame(client.klines(symbol, TIME_PERIOD))
        resp = resp.iloc[:,:6]
        resp.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
        resp = resp.set_index('Time')
        resp.index = pd.to_datetime(resp.index, unit = 'ms')
        resp = resp.astype(float)
        return resp
    except ClientError as error:
        print(f"Erro encontrado. status: {error.status_code}, código de erro: {error.error_code}, mensagem de erro: {error.error_message}")

# Definir alavancagem para o símbolo necessário. Você precisa disso porque diferentes símbolos podem ter alavancagem diferente
def set_leverage(symbol, level):
    try:
        response = client.change_leverage(
            symbol=symbol, leverage=level, recvWindow=6000
        )
        print(response)
    except ClientError as error:
        print(f"Erro encontrado. status: {error.status_code}, código de erro: {error.error_code}, mensagem de erro: {error.error_message}")

# O mesmo para o tipo de margem
def set_mode(symbol, margin_mode):
    try:
        response = client.change_margin_type(
            symbol=symbol, marginType=margin_mode, recvWindow=6000
        )
        print(response)
    except ClientError as error:
        print(f"Erro encontrado. status: {error.status_code}, código de erro: {error.error_code}, mensagem de erro: {error.error_message}")

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
def open_order(symbol, side, price_simple_median):
    price = float(client.ticker_price(symbol)['price'])
    qty_precision = get_qty_precision(symbol)
    price_precision = get_price_precision(symbol)
    qty = round(volume/price, qty_precision)
    if side == 'buy':
        try:
            resp1 = client.new_order(symbol=symbol, side='BUY', type='MARKET', quantity=qty)
            print(f"$$$$$$$$$$$$$$$ => CRIANDO OPERAÇÃO DE {side.upper()} PARA {symbol}")
            print(f"$$$$$$$$$$$$$$$ => Operação: COMPRA, Tipo: {resp1['type']}, Ordem: {resp1['orderId']}")
            sleep(2)
            sl_price = round(price - price*sl, price_precision)
            resp2 = client.new_order(symbol=symbol, side='SELL', type='STOP_MARKET', quantity=qty, timeInForce='GTC', stopPrice=sl_price)
            print(f"$$$$$$$$$$$$$$$ => Operação: VENDA, Tipo: {resp2['type']}, Ordem: {resp2['orderId']}")
            sleep(2)
            tp_price = round(price + price * tp, price_precision)
            if price_simple_median > 0 & price_simple_median < tp_price:
                tp_price = round(price_simple_median, price_precision)
            resp3 = client.new_order(symbol=symbol, side='SELL', type='TAKE_PROFIT_MARKET', quantity=qty, timeInForce='GTC', stopPrice=tp_price)
            print(f"$$$$$$$$$$$$$$$ => Operação: VENDA, Tipo: {resp3['type']}, Ordem: {resp3['orderId']}")
        except ClientError as error:
            print(f"Erro encontrado. status: {error.status_code}, código de erro: {error.error_code}, mensagem de erro: {error.error_message}")
    if side == 'sell':
        try:
            resp1 = client.new_order(symbol=symbol, side='SELL', type='MARKET', quantity=qty)
            print(f"$$$$$$$$$$$$$$$ => CRIANDO OPERAÇÃO DE {side.upper()} PARA {symbol}")
            print(f"$$$$$$$$$$$$$$$ => Operação: VENDA, Tipo: {resp1['type']}, Ordem: {resp1['orderId']}")
            sleep(2)
            sl_price = round(price + price*sl, price_precision)
            resp2 = client.new_order(symbol=symbol, side='BUY', type='STOP_MARKET', quantity=qty, timeInForce='GTC', stopPrice=sl_price)
            print(f"$$$$$$$$$$$$$$$ => Operação: COMPRA, Tipo: {resp2['type']}, Ordem: {resp2['orderId']}")
            sleep(2)
            tp_price = round(price - price * tp, price_precision)
            if price_simple_median > 0 & price_simple_median > tp_price:
                tp_price = round(price_simple_median, price_precision)
            resp3 = client.new_order(symbol=symbol, side='BUY', type='TAKE_PROFIT_MARKET', quantity=qty, timeInForce='GTC', stopPrice=tp_price)
            print(f"$$$$$$$$$$$$$$$ => Operação: COMPRA, Tipo: {resp3['type']}, Ordem: {resp3['orderId']}")
        except ClientError as error:
            print(f"Erro encontrado. status: {error.status_code}, código de erro: {error.error_code}, mensagem de erro: {error.error_message}")

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
        print(f"Erro encontrado. status: {error.status_code}, código de erro: {error.error_code}, mensagem de erro: {error.error_message}")

# Todas as ordens abertas (retorna a lista de símbolos):
def check_orders():
    try:
        response = client.get_orders(recvWindow=6000)
        sym = []
        for elem in response:
            sym.append(elem['symbol'])
        return sym
    except ClientError as error:
        print(f"Erro encontrado. status: {error.status_code}, código de erro: {error.error_code}, mensagem de erro: {error.error_message}")

# Fechar ordens abertas para o símbolo necessário. Se uma ordem de stop for executada e outra ainda estiver lá
def close_open_orders(symbol):
    try:
        response = client.cancel_open_orders(symbol=symbol, recvWindow=6000)
        if response['code'] == 200:
            print(f"===============> ORDENS DE STOP PARA {symbol} FORAM FECHADAS COM SUCESSO")
        else:
            print(response)
    except ClientError as error:
        print(f"Erro encontrado. status: {error.status_code}, código de erro: {error.error_code}, mensagem de erro: {error.error_message}")

# Obter a hora atual
def get_hour():
    hora_atual = datetime.now()
    return hora_atual.strftime("%H:%M:%S")

# Fechar ordens de stop para posições fechadas
def close_orders_not_in_position(ord, pos):
    print(f"===============> CHECANDO ORDENS DE STOP PARA POSIÇÕES FECHADAS...")
    for elem in ord:
        if not elem in pos:
            close_open_orders(elem)

# Estratégia baseada no indicador Bollinger Bands (Bandas de Bollinger).
def bollinger_strategy(symbol):
    kl = klines(symbol)
    
    # Calculando as bandas de Bollinger
    period = 20  # Período para a média móvel
    std_dev = 2  # Desvio padrão
    simple_median = 0  # Média móvel simples (SMA)

    # Calcular a média móvel simples (SMA)
    simple_median = kl['Close'].rolling(window=period).mean()

    # Calcular as bandas superior e inferior
    kl['Upper'] = simple_median + (std_dev * kl['Close'].rolling(window=period).std())
    kl['Lower'] = simple_median - (std_dev * kl['Close'].rolling(window=period).std())
    
    # Verificando se o preço está acima da banda superior
    if kl['Close'].iloc[-1] > kl['Upper'].iloc[-1]:
        return ['down', 0]
    # Verificando se o preço está abaixo da banda inferior
    elif kl['Close'].iloc[-1] < kl['Lower'].iloc[-1]:
        return ['up', 0]
    else:
        return ['none', 0]

orders = 0
symbol = ''

# obtendo todos os símbolos da lista de Futuros da Binance:
symbols = get_tickers_usdt()

while True:
    # precisamos obter saldo para verificar se a conexão está boa ou se você tem todas as permissões necessárias
    balance = get_balance_usdt()
    sleep(1)
    if balance == None:
        print("Não é possível conectar-se à API. Verifique o IP, as restrições ou espere algum tempo")
    if balance != None:
        print("####################################################################")
        print(f"---------------> MEU SALDO: {round(balance, 2)} USDT - {get_hour()}")
        print("####################################################################")
        ## Se o saldo for menor que 35 USDT, você não pode mais operar
        if balance < LIMIT_EXIT:
            print("---------------> SALDO LIMITE ATINGIDO. VOCÊ NÃO PODE MAIS OPERAR.")
            sys.exit()
        ## obtendo lista de posição:
        pos = []
        pos = get_pos()
        print(f'---------------> Você tem {len(pos)} posições abertas: {pos}')
        ## Obtendo lista de ordens
        ord = []
        ord = check_orders()
        ## removendo ordens de stop para posições fechadas
        close_orders_not_in_position(ord, pos)
        if len(pos) < qty:
            print("---------------> Verificando TODOS os símbolos disponíveis...")
            for elem in symbols:
                # Estratégias (você pode criar a sua própria com a biblioteca TA):
                signal = bollinger_strategy(elem)
                # sinal 'up' ou 'down', colocamos ordens para símbolos que não estão nas posições abertas e ordens
                # também não precisamos de USDTUSDC porque é 1:1 (não precisamos gastar dinheiro com a comissão)
                if len(pos) < qty:
                    if signal[0] == 'up' and elem != 'USDCUSDT' and not elem in pos and not elem in ord and elem != symbol:
                        print('---------------> Sinal de COMPRA encontrado para ', elem)
                        set_mode(elem, margin_mode)
                        sleep(1)
                        set_leverage(elem, leverage)
                        sleep(1)
                        open_order(elem, 'buy', signal[1])
                        symbol = elem
                        order = True
                        pos = get_pos()
                        sleep(1)
                        ord = check_orders()
                        sleep(10)
                        continue
                    if signal[0] == 'down' and elem != 'USDCUSDT' and not elem in pos and not elem in ord and elem != symbol:
                        print('---------------> Sinal de VENDA encontrado para ', elem)
                        set_mode(elem, margin_mode)
                        sleep(1)
                        set_leverage(elem, leverage)
                        sleep(1)
                        open_order(elem, 'sell', signal[1])
                        symbol = elem
                        order = True
                        pos = get_pos()
                        sleep(1)
                        ord = check_orders()
                        sleep(10)
                        continue
                else:
                    print(f'---------------> Você já tem {len(pos)} de {qty} posições abertas: {pos}')
                    close_orders_not_in_position(ord, pos)
                    break
    print(f"---------------> Aguardando 2 minutos a partir de {get_hour()}")
    sleep(120)
