import talib

def adx(px, lookback):
    close = px['close']
    low = px['low']
    high = px['high']
    adx = talib.adx(high, low, close, timeperiod=lookback)
    return adx[-2]


def sar(px):
    close = px['close']
    opn = px['open']
    low = px['low']
    high = px['high']
    sar = talib.sar(high, low, acceleration=.02, maximum=.20)
    return sar[-2]


def dmi(px, lookback): 
    pd, md = talib.dmi(px,lookback)
    return pd[-1], md[-1]


def adxr_func(px, lookback):
    close = px['close']
    low = px['low']
    high = px['high']
    signal = talib.adxr(high, low, close, timeperiod=lookback)
    return signal[-2]