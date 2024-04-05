# Estratégia baseada no indicador RSI, estocástico RSI e média móvel exponencial de 200 períodos (EMA).
#def stochastic_signal(symbol):
    #kl = klines(symbol)
    #rsi = ta.momentum.RSIIndicator(kl.Close).rsi()
    #rsi_k = ta.momentum.StochRSIIndicator(kl.Close).stochrsi_k()
    #rsi_d = ta.momentum.StochRSIIndicator(kl.Close).stochrsi_d()
    #ema = ta.trend.ema_indicator(kl.Close, window=200)
    #if rsi.iloc[-1] < 40 and ema.iloc[-1] < kl.Close.iloc[-1] and rsi_k.iloc[-1] < 20 and rsi_k.iloc[-3] < rsi_d.iloc[-3] and rsi_k.iloc[-2] < rsi_d.iloc[-2] and rsi_k.iloc[-1] > rsi_d.iloc[-1]:
        #return 'up'
    #if rsi.iloc[-1] > 60 and ema.iloc[-1] > kl.Close.iloc[-1] and rsi_k.iloc[-1] > 80 and rsi_k.iloc[-3] > rsi_d.iloc[-3] and rsi_k.iloc[-2] > rsi_d.iloc[-2] and rsi_k.iloc[-1] < rsi_d.iloc[-1]:
        #return 'down'
    #else:
        #return 'none'
#
## Estrategia Baseada no indicador RSI (Índice de Força Relativa) e na média móvel exponencial de 200 períodos (EMA).
#def rsi_signal(symbol):
    #kl = klines(symbol)
    #rsi = ta.momentum.RSIIndicator(kl.Close).rsi()
    #ema = ta.trend.ema_indicator(kl.Close, window=200)
    #if rsi.iloc[-2] < 30 and rsi.iloc[-1] > 30:
        #return 'up'
    #if rsi.iloc[-2] > 70 and rsi.iloc[-1] < 70:
        #return 'down'
    #else:
        #return 'none'
#
## Estratégia baseada no indicador MACD e na média móvel exponencial de 200 períodos (EMA).
#def macd_ema(symbol):
    #kl = klines(symbol)
    #macd = ta.trend.macd_diff(kl.Close)
    #ema = ta.trend.ema_indicator(kl.Close, window=200)
    #if macd.iloc[-3] < 0 and macd.iloc[-2] < 0 and macd.iloc[-1] > 0 and ema.iloc[-1] < kl.Close.iloc[-1]:
        #return 'up'
    #if macd.iloc[-3] > 0 and macd.iloc[-2] > 0 and macd.iloc[-1] < 0 and ema.iloc[-1] > kl.Close.iloc[-1]:
        #return 'down'
    #else:
        #return 'none'
#    
## Estratégia baseada na média móvel exponencial de 200 períodos (EMA) e 50 períodos (EMA).
#def ema200_50(symbol):
    #kl = klines(symbol)
    #ema200 = ta.trend.ema_indicator(kl.Close, window=100)
    #ema50 = ta.trend.ema_indicator(kl.Close, window=50)
    #if ema50.iloc[-3] < ema200.iloc[-3] and ema50.iloc[-2] < ema200.iloc[-2] and ema50.iloc[-1] > ema200.iloc[-1]:
        #return 'up'
    #if ema50.iloc[-3] > ema200.iloc[-3] and ema50.iloc[-2] > ema200.iloc[-2] and ema50.iloc[-1] < ema200.iloc[-1]:
        #return 'down'
    #else:
        #return 'none'
#
## Estratégia baseada no indicador RSI (Índice de Força Relativa) e no estocástico RSI.
#def stochastic_rsi_signal(symbol):
    #kl = klines(symbol)
    #rsi = ta.momentum.RSIIndicator(kl.Close).rsi()
    #stoch_rsi_k = ta.momentum.StochRSIIndicator(kl.Close).stochrsi_k()
    #stoch_rsi_d = ta.momentum.StochRSIIndicator(kl.Close).stochrsi_d()
#    
    ## Se o estocástico RSI K e o D estiverem se cruzando e o RSI estiver em uma determinada faixa
    #if (stoch_rsi_k.iloc[-2] < stoch_rsi_d.iloc[-2] and stoch_rsi_k.iloc[-1] > stoch_rsi_d.iloc[-1]) \
        #and (rsi.iloc[-1] < 20 or rsi.iloc[-1] > 80):
        #return 'up'  # Sinal de compra
    #elif (stoch_rsi_k.iloc[-2] > stoch_rsi_d.iloc[-2] and stoch_rsi_k.iloc[-1] < stoch_rsi_d.iloc[-1]) \
        #and (rsi.iloc[-1] < 20 or rsi.iloc[-1] > 80):
        #return 'down'  # Sinal de venda
    #else:
        #return 'none'  # Nenhum sinal claro
#
## Estratégia baseada no indicador MACD e na média móvel exponencial de 12 períodos (EMA) e 26 períodos (EMA).
#def macd_crossover_signal(symbol):
    #kl = klines(symbol)
    #macd = ta.trend.macd_diff(kl.Close)  # Diferença entre as médias móveis exponenciais
    #ema_short = ta.trend.ema_indicator(kl.Close, window=12)  # EMA de 12 períodos (curto prazo)
    #ema_long = ta.trend.ema_indicator(kl.Close, window=26)  # EMA de 26 períodos (longo prazo)
#    
    #if macd.iloc[-2] < 0 and macd.iloc[-1] > 0 and ema_short.iloc[-1] > ema_long.iloc[-1]:
        #return 'up'  # Sinal de compra quando MACD cruza acima de zero e EMA curto prazo acima de EMA longo prazo
    #elif macd.iloc[-2] > 0 and macd.iloc[-1] < 0 and ema_short.iloc[-1] < ema_long.iloc[-1]:
        #return 'down'  # Sinal de venda quando MACD cruza abaixo de zero e EMA curto prazo abaixo de EMA longo prazo
    #else:
        #return 'none'  # Nenhum sinal claro
#
## Estratégia baseada no indicador EMA (Média Móvel Exponencial) de 8 períodos (EMA) e 80 períodos (EMA).
#def ema_crossover_signal(symbol):
    #kl = klines(symbol)
    #ema_short = ta.trend.ema_indicator(kl.Close, window=8)  # EMA de 8 períodos (curto prazo)
    #ema_long = ta.trend.ema_indicator(kl.Close, window=80)  # EMA de 80 períodos (longo prazo)
#    
    #if ema_short.iloc[-1] > ema_long.iloc[-1] and ema_short.iloc[-2] <= ema_long.iloc[-2]:
        #return 'up'  # Sinal de venda quando a EMA curto prazo cruza abaixo da EMA longo prazo
    #elif ema_short.iloc[-1] < ema_long.iloc[-1] and ema_short.iloc[-2] >= ema_long.iloc[-2]:
        #return 'down'  # Sinal de compra quando a EMA curto prazo cruza acima da EMA longo prazo
    #else:
        #return 'none'  # Nenhum sinal claro