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

tp = 0.012 # take profit (se você colocar 0.012, então você terá 1,0% de lucro)
sl = 0.007 # stop loss (se você colocar 0.005, então você terá 0,7% de perda) 
volume = 30 # volume para uma ordem (volume / leverage = preço da ordem)
leverage = 10  # alavancagem
margin_mode = 'ISOLATED' # tipo é 'ISOLATED' ou 'CROSS'
qty = 2 # Quantidade de posições abertas simultaneamente
time_period = '15m' # período de tempo para velas

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
        resp = pd.DataFrame(client.klines(symbol, time_period))
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
def set_mode(symbol, margin_mode):
    try:
        response = client.change_margin_type(
            symbol=symbol, marginType=margin_mode, recvWindow=6000
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
            resp1 = client.new_order(symbol=symbol, side='BUY', type='MARKET', quantity=qty)
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
            resp1 = client.new_order(symbol=symbol, side='SELL', type='MARKET', quantity=qty)
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

# Estratégia baseada no indicador RSI, estocástico RSI e média móvel exponencial de 200 períodos (EMA).
def stochastic_signal(symbol):
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

# Estratégia baseada no indicador MACD e na média móvel exponencial de 200 períodos (EMA).
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
    
# Estratégia baseada na média móvel exponencial de 200 períodos (EMA) e 50 períodos (EMA).
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

# Estratégia baseada no indicador RSI (Índice de Força Relativa) e no estocástico RSI.
def stochastic_rsi_signal(symbol):
    kl = klines(symbol)
    rsi = ta.momentum.RSIIndicator(kl.Close).rsi()
    stoch_rsi_k = ta.momentum.StochRSIIndicator(kl.Close).stochrsi_k()
    stoch_rsi_d = ta.momentum.StochRSIIndicator(kl.Close).stochrsi_d()
    
    # Se o estocástico RSI K e o D estiverem se cruzando e o RSI estiver em uma determinada faixa
    if (stoch_rsi_k.iloc[-2] < stoch_rsi_d.iloc[-2] and stoch_rsi_k.iloc[-1] > stoch_rsi_d.iloc[-1]) \
        and (rsi.iloc[-1] < 20 or rsi.iloc[-1] > 80):
        return 'up'  # Sinal de compra
    elif (stoch_rsi_k.iloc[-2] > stoch_rsi_d.iloc[-2] and stoch_rsi_k.iloc[-1] < stoch_rsi_d.iloc[-1]) \
        and (rsi.iloc[-1] < 20 or rsi.iloc[-1] > 80):
        return 'down'  # Sinal de venda
    else:
        return 'none'  # Nenhum sinal claro

# Estratégia baseada no indicador MACD e na média móvel exponencial de 12 períodos (EMA) e 26 períodos (EMA).
def macd_crossover_signal(symbol):
    kl = klines(symbol)
    macd = ta.trend.macd_diff(kl.Close)  # Diferença entre as médias móveis exponenciais
    ema_short = ta.trend.ema_indicator(kl.Close, window=12)  # EMA de 12 períodos (curto prazo)
    ema_long = ta.trend.ema_indicator(kl.Close, window=26)  # EMA de 26 períodos (longo prazo)
    
    if macd.iloc[-2] < 0 and macd.iloc[-1] > 0 and ema_short.iloc[-1] > ema_long.iloc[-1]:
        return 'up'  # Sinal de compra quando MACD cruza acima de zero e EMA curto prazo acima de EMA longo prazo
    elif macd.iloc[-2] > 0 and macd.iloc[-1] < 0 and ema_short.iloc[-1] < ema_long.iloc[-1]:
        return 'down'  # Sinal de venda quando MACD cruza abaixo de zero e EMA curto prazo abaixo de EMA longo prazo
    else:
        return 'none'  # Nenhum sinal claro

# Estratégia baseada no indicador EMA (Média Móvel Exponencial) de 8 períodos (EMA) e 80 períodos (EMA).
def ema_crossover_signal(symbol):
    kl = klines(symbol)
    ema_short = ta.trend.ema_indicator(kl.Close, window=8)  # EMA de 8 períodos (curto prazo)
    ema_long = ta.trend.ema_indicator(kl.Close, window=80)  # EMA de 80 períodos (longo prazo)
    
    if ema_short.iloc[-1] > ema_long.iloc[-1] and ema_short.iloc[-2] <= ema_long.iloc[-2]:
        return 'up'  # Sinal de venda quando a EMA curto prazo cruza abaixo da EMA longo prazo
    elif ema_short.iloc[-1] < ema_long.iloc[-1] and ema_short.iloc[-2] >= ema_long.iloc[-2]:
        return 'down'  # Sinal de compra quando a EMA curto prazo cruza acima da EMA longo prazo
    else:
        return 'none'  # Nenhum sinal claro

# Estratégia baseada no indicador Bollinger Bands (Bandas de Bollinger).
def bollinger_strategy(symbol):
    kl = klines(symbol)
    
    # Calculando as bandas de Bollinger
    period = 20  # Período para a média móvel
    std_dev = 2  # Desvio padrão

    # Calcular a média móvel simples (SMA)
    kl['SMA'] = kl['Close'].rolling(window=period).mean()

    # Calcular as bandas superior e inferior
    kl['Upper'] = kl['SMA'] + (std_dev * kl['Close'].rolling(window=period).std())
    kl['Lower'] = kl['SMA'] - (std_dev * kl['Close'].rolling(window=period).std())
    
    # Verificando se o preço está acima da banda superior
    if kl['Close'].iloc[-1] > kl['Upper'].iloc[-1]:
        return 'down'
    # Verificando se o preço está abaixo da banda inferior
    elif kl['Close'].iloc[-1] < kl['Lower'].iloc[-1]:
        return 'up'
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
        print("Não é possível conectar-se à API. Verifique o IP, as restrições ou espere algum tempo")
    if balance != None:
        print(f">>>>>>>>>>>>>> Meu saldo é: {balance} USDT")
        ## obtendo lista de posição:
        pos = []
        pos = get_pos()
        print(f'>>>>>>>>>>>>>> Você tem {len(pos)} posições abertas: {pos}')
        ## Obtendo lista de ordens
        ord = []
        ord = check_orders()
        ## removendo ordens de stop para posições fechadas
        for elem in ord:
            if not elem in pos:
                close_open_orders(elem)
        if len(pos) < qty:
            print(">>>>>>>>>>>>>> Verificando TODOS os símbolos disponíveis...")
            for elem in symbols:
                # Estratégias (você pode criar a sua própria com a biblioteca TA):
                # signal = stochastic_signal(elem)
                # signal = rsi_signal(elem)
                # signal = macd_ema(elem)
                # signal = macd_crossover_signal(elem)
                # signal = stochastic_rsi_signal(elem)
                # signal = ema_crossover_signal(elem)
                signal = bollinger_strategy(elem)
                # sinal 'up' ou 'down', colocamos ordens para símbolos que não estão nas posições abertas e ordens
                # também não precisamos de USDTUSDC porque é 1:1 (não precisamos gastar dinheiro com a comissão)
                if len(pos) < qty:
                    if signal == 'up' and elem != 'USDCUSDT' and not elem in pos and not elem in ord and elem != symbol:
                        print('>>>>>>>>>>>>>> Sinal de COMPRA encontrado para ', elem)
                        set_mode(elem, margin_mode)
                        sleep(1)
                        set_leverage(elem, leverage)
                        sleep(1)
                        print('>>>>>>>>>>>>>> Colocando ordem para ', elem)
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
                        print('>>>>>>>>>>>>>> Sinal de VENDA encontrado para ', elem)
                        set_mode(elem, margin_mode)
                        sleep(1)
                        set_leverage(elem, leverage)
                        sleep(1)
                        print('>>>>>>>>>>>>>> Colocando ordem para ', elem)
                        open_order(elem, 'sell')
                        symbol = elem
                        order = True
                        pos = get_pos()
                        sleep(1)
                        ord = check_orders()
                        sleep(1)
                        sleep(10)
                        # break
                else:
                    print(">>>>>>>>>>>>>> LIMITE DE POSIÇÕES ATINGIDO")
                    sys.exit()
    hora_atual = datetime.now()
    hora_atual_formatada = hora_atual.strftime("%H:%M:%S")
    print(f">>>>>>>>>>>>>> Aguardando 2 minutos a partir de {hora_atual_formatada}")
    sleep(120)
