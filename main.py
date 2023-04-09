"""
    Title: Buy and Hold (NYSE)
    Description: This is a long only strategy which rebalances the 
        portfolio weights every month at month start.
    Style tags: Systematic
    Asset class: Equities, Futures, ETFs, Currencies and Commodities
    Dataset: US Equities
"""
import numpy as np
import pandas as pd
import talib as talib
import math

from blueshift.api import(  symbol,
                            order_target_percent,
                            schedule_function,
                            date_rules,
                            time_rules,
                            set_commission,
                            set_slippage
                       )
from blueshift.finance import commission, slippage


#function to run at the beginning of the algo
def initialize(context):

    # tracks total percent of illiquid portfolio
    context.percent_allocated = 0

    # defines maximum percent of portfolio that may be illiquid at any given time
    context.max_total_allocation = .6

    # maximum percent we are willing to lose on any given trade
    context.stop_loss = .05

    # universe selection
    context.securities = [symbol('AMZN'), symbol('AAPL'),
                          symbol('WMT'), symbol('MU'),
                          symbol('BAC'), symbol('KO'),
                          symbol('BA'), symbol('AXP')]

    # define strategy parameters
    context.params = {'indicator_lookback':365,
                      'indicator_freq':'1D',
                      'buy_signal_threshold':0.2,
                      'sell_signal_threshold':-0.2,
                      'trade_freq': 1440,
                      'portfolio_invested':.15,
                      'dm_lookback':14}

    # variable to control trading frequency
    context.bar_count = 0

    # variables to track signals and target portfolio
    context.signals = dict((security,0) for security in context.securities)
    context.target_position = dict((security,0) for security in context.securities)

    # set trading cost and slippage to zero
    set_commission(commission.PerShare(cost=0.0, min_trade_cost=0.0))
    set_slippage(slippage.FixedSlippage(0.00))


# this function runs every minute bar; it calls the run_strategy function
def handle_data(context, data):
    context.bar_count += 1

    # if we are greater than trading frequency threshold...
    if context.bar_count < context.params['trade_freq']:
        return

    # time to trade, call the strategy function
    context.bar_count = 0
    run_strategy(context, data)


# this function is called above and calls the following functions
def run_strategy(context, data):
    generate_signals(context, data)
    generate_target_position(context, data)
    rebalance(context, data)


def rebalance(context,data):
    for security in context.securities:
        order_target_percent(security, context.target_position[security])
    

def calculate_percent_allocated(context, data):
    percent_allocated = 0
    for security in context.securities:
        #print(context.target_position[security])
        context.percent_allocated += context.target_position[security]

    return percent_allocated


# this function will return the security with the lowest percent value and create a sell order
def get_min_security(context, data):

    # these hold temporary variables until the true values are placed
    min_allocation = 1
    min_security = context.securities[0]

    # loop logic to find lowest percent allocation of portfolio
    if context.percent_allocated > context.max_total_allocation:
        for security in context.securities:
            if context.target_position[security] < min_allocation:
                min_allocation = context.target_position[security]
                min_security = context.securities[security]

    return min_security

# undelete quotes
def generate_target_position(context,data):

    context.percent_allocated = calculate_percent_allocated(context,data)

    if context.percent_allocated <= context.max_total_allocation:
        for security in context.securities:
            if context.signals[security] >= context.params['buy_signal_threshold']:
                # apply weight based on our indicators
                if context.signals[security] == .8:
                    context.target_position[security] = .15
                
                elif context.signals[security] == .6:
                    context.target_position[security] = .10
                
                elif context.signals[security] == .4:
                    context.target_position[security] = .05

                elif context.signals[security] == .3:
                    context.target_position[security] = .025

                elif context.signals[security] == .2:
                    context.target_position[security] = .15

            
            elif context.signals[security] <= context.params['sell_signal_threshold']:
                # we sell only as much as we put into the security
                context.target_position[security] *= -1
    
            else:
                context.target_position[security] = 0
    else:            
        # if an order is placed when we are at maximum portfolio allocation capacity

        while context.percent_allocated > context.max_total_allocation:
            min_security = get_min_security(context, data)
            context.target_position[min_security] = -context.target_position[security]
            context.percent_allocated = calculate_percent_allocated(context,data)
    

def generate_signals(context,data):


    price = data.history(context.securities, ['open','high','low','close'], 
        context.params['indicator_lookback'], context.params['indicator_freq'])
    for security in context.securities:
        px = get_price(price,security)
        context.signals[security] = signal_function(px, context.params)




def get_price(prices, security):
    try:
        px = prices.loc[:,security].values
    except:
        try:
            px = prices.xs(security)
        except:
            raise ValueError('Unknown type of historical price data')

    return(px)



def signal_function(px, params):
    
    # this will hold the signal of all indicators
    signal = 0

    # swing values
    asi, hsp, hip, lsp, lop, trailing_stop_long = swing_index(px)

    # reaction trend signal
    reaction_trend_signal = reactionTrendSystem(px)
    adx_sig = adx(px,params['dm_lookback'])
    sar_sig = sar(px)
    pi,mi = dmi(px,params['dm_lookback'])
    adxr = adxr_func(px, params['dm_lookback'])
    supertrend = Supertrend(px, params['dm_lookback'], 3.0)
    # by changing the time period it changes when the adx runs
    if adxr < 20:
        signal += reaction_trend_signal
        return signal
    if adxr >= 20:
        return 0
    return 0
    ''' 
    if adxr > 25:
        # note: add stop so that no bad orders are created
        if cross(pi,mi):
            signal += .2
            return .2
        elif cross(mi,pi):
            signal -=.2
            return -.2

        #if pi[-1] > mi[-1]:
        #    signal += .2
        #elif pi[-1] < mi[-1]:
        #    signal -=.2
               
    if asi > hsp:
        signal += .2
        return .2
    elif asi < lsp or px['low'][-1] > trailing_stop_long:
        signal -= .2
        return -.2

    if sar_sig > px['high'][-1]:
        signal += .2
        return .2
    elif sar_sig < px['low'][-1]:
        signal -= .2
        return -.2

    if supertrend:
        signal += .2
        return .2
    elif not supertrend:
        signal -= .2
        return -.2'''
        #else:
        #    pass
    #else:
    #    signal += 0
    #    return 0
        #else:
        #    return 0
    
    

def sma(px, lookback):
    sig = ta.SMA(px, timeperiod=lookback)
    return sig[-1]


def ema(px, lookback):
    sig = ta.EMA(px, timeperiod=lookback)
    return sig[-1]


def rsi(px, lookback):
    sig = ta.RSI(px, timeperiod=lookback)
    return sig[-1]


def bollinger_band(px, lookback):
    upper, mid, lower = ta.BBANDS(px, timeperiod=lookback)
    return upper[-1], mid[-1], lower[-1]


def macd(px, lookback):
    macd_val, macdsignal, macdhist = ta.MACD(px)
    return macd_val[-1], macdsignal[-1], macdhist[-1]


def doji(px):
    sig = ta.CDLDOJI(px.open.values, px.high.values, px.low.values, px.close.values)
    return sig[-1]

    
def calculate_asi(px,opn,high,low,close):
        # initializing variables to be used
        c1 = [0] * len(px)
        c2 = [0] * len(px)
        c3 = [0] * len(px)
        c4 = [0] * len(px)
        c5 = [0] * len(px)
        c6 = [0] * len(px)
        c7 = [0] * len(px)
        n = [0] * len(px)
        r = [0] * len(px)
        si = [0] * len(px)
        asi = [0] * len(px)
        k = [0] * len(px)
        l = 3.00

        # calculations for swing index system
        for i in (range(1,len(px))):
            # cannot be calculated on first day
            
            c1[i] = (abs(high[i] - close[i - 1]))
            c2[i] = (abs(low[i] - close[i - 1]))
            c3[i] = (abs(high[i] - low[i]))
            c4[i] = (abs(close[i - 1] - opn[i - 1]))
            c5[i] = (close[i] - close[i - 1])
            c6[i] = (close[i] - opn[i])
            c7[i] = (close[i - 1] - opn[i - 1])

    
            k[i] = (np.maximum(c1[i], c2[i]))
            
            n[i] = ((c5[i] + (0.5 * c6[i]) + (0.25 * c7[i])))

            if c1[i] == max(c1[i], c2[i], c3[i]):
                r[i] = (c1[i] - (0.5 * c2[i]) + (0.25 * c4[i]))

            elif c2[i] == max(c1[i], c2[i], c3[i]):
                r[i] = (c2[i] - (0.5 * c1[i]) + (0.25 * c4[i]))

            elif c3[i] == max(c1[i], c2[i], c3[i]):
                r[i] = (c3[i] + (0.25 * c4[i]))


            si[i] = (50 * (n[i] / r[i]) * (k[i] / l))

            asi[i] += si[i]
        return asi


# swing index system
def swing_index(px):

    hsp = []
    lsp = []
    hip = []
    lop = []
    close = px['close']
    low = px['low']
    high = px['high']
    opn = px['open']

    
    asi = calculate_asi(px,opn,high,low,close)

    # calculations for finding hsp
    hsp = hsp_asi(px,asi)


    # calculations for finding hip
    hip = hip_asi(px,high,hsp)


    # calculations for finding lsp
    lsp = lsp_asi(px,asi)

    # calculations for finding lop
    lop = lop_asi(px,low,lsp)

    # initialize and declare trailing stop for long trades only

    # calculations for trailing stop when long
    trailing_stop_long = trailing_stop(asi,low,hsp)
    return asi[-1], hsp[-2], hip[-2], lsp[-2], lop[-2], trailing_stop_long[-2]


# finds trailing stop for swing index system
def trailing_stop(asi,low,hsp):
        trailing_stop_long = [0] * len(hsp)
        for i in range(len(hsp)):

            # we want to deal with numbers
            if hsp[i] == None:
                continue

            else:

                # check to see if a new hsp is made

                # most recent change in hsp
                if hsp[i] != hsp[i-1]:
                    
                    for j in range(len(hsp) - i):
                        if abs(hsp[i] - asi[i+j]) > 60:
                            trailing_stop_long[i + j] = low[i]
                            continue

        return trailing_stop_long


# here we initialize the phasing for reaction trend
def initPhasing(phasing,high,low,close,lookback=27):

    # simple algorithm to calculate whether to take the significant low or high price; we calculate the average price
    # over a 27 day range and find the greatest distance between the lows and highs to this average point. out of these,
    # we choose the most significant and compare the most significant low with the most significant high. Which ever is greater
    # is the day we begin phasing on and will decide whether we begin with "B" or "S" as per the Reaction Trend System
    
    xbar = 0 # holds average
    hip = hip_method(high)
    lop = lop_method(low)
    # calculate arithmetic average 
    for i in range(lookback): xbar += (high[i]+low[i]+close[i])/(3*lookback)
    

    # finds most sig price for high and low points
    highSig = 0
    indexHigh = 0
    for i in range(lookback):
        if hip[i] == None or lop[i] == None:
            continue
        temp = abs(xbar-hip[i])

        if highSig < temp: 
            highSig = temp
            indexHigh = i

        lowSig = 0
        indexLow = 0

        temp = abs(xbar-lop[i])

        if lowSig > temp: 
            lowSig = temp
            indexLow = i


    # begins phasing depending on the significant price
    if lowSig > highSig:
        phase(phasing, indexLow, "B")

    elif lowSig <= highSig:
        phase(phasing, indexHigh, "S")


# applies phasing with specific start date and letter
def phase(phasing,start,letter):
    phasing[start] = letter
    
    if letter == "B":
        for j in range(start+1, len(phasing),3):
            phasing[j] = "O"
            
        for j in range(start+2, len(phasing), 3):
            phasing[j] = "S"
        
        for j in range(start+3, len(phasing), 3):
            phasing[j] = "B"

    elif letter == "S":
        for j in range(start+1, len(phasing),3):
            phasing[j] = "B"
            
        for j in range(start+2, len(phasing), 3):
            phasing[j] = "O"
        
        for j in range(start+3, len(phasing), 3):
            phasing[j] = "S"
    

# adjust the phasing if we are short
def adjust_phasing_short(phasing,begin_index,high,i):
    end_index = i
    max = high[begin_index]
    max_index = begin_index

    # finds index to begin new phasing
    for index in range(begin_index, (end_index - begin_index)):
        if high[index] > max:
            max = high[index]
            max_index = index
                
    # adjusts phasing
    phase(phasing,max_index,"S")


# adjust the phasing if we are long
def adjust_phasing_long(phasing,begin_index,low,i):

    # swapping technique
    end_index = i
    min = low[begin_index]
    min_index = begin_index

    # adjusts phasing as necessary
    for index in range(begin_index, end_index - begin_index):
        if low[index] < min:
            min = low[index]
            min_index = index

    phase(phasing,min_index,"S")


# reaction trend system
def reactionTrendSystem(df):

    # intializing data frame values
    high = df['high']
    low = df['low']
    close = df['close']

    # intializing variables 
    long_m = False
    begin_index = 0
    trailing_stop = 0
    short = False

    long_anti_trend = False
    short_anti_trend = False

    #intializing lists
    phasing = [None] * len(df)
    buy_sig = [None] * len(df)
    sell_sig = [None] * len(df)
    hbop = [None] * len(df)
    lbop = [None] * len(df)

    # this method declares the phasing list with default values
    initPhasing(phasing,high,low,close)


    # main trading logic
    for i in range(1,len(df)): # loop through df beginning on second day 
        if high[i] == None:
            continue
        if low[i] == None:
            continue

        # initialize important variables
        # note: values good for current day only
        xbar = (high[i-1] + low[i-1] + close[i-1])/3
        buy_sig[i] = (2*xbar) - high[i-1]
        sell_sig[i] = (2*xbar) - low[i-1]
        hbop[i] = (2*xbar) - (2*low[i-1]) + high[i-1]
        lbop[i] = (2*xbar) - (2*high[i-1]) + low[i-1]


        # we are not in trend mode
        # here we initialize orders
        if not long and not short:

            # check for trend signals

            #trend mode long
            if high[i] > hbop[i]:
                begin_index = i

                # trend mode is always reversing
                long_m = True
                long_anti_trend = False
                short_anti_trend = False
                return .3

            # trend mode short
            if low[i] < lbop[i]:
                begin_index = i

                # trend mode is always reversing
                short = True
                long_anti_trend = False
                short_anti_trend = False
                return -.3


            # check for anti-trend signals


            # anti trend mode short
            elif low[i] < sell_sig[i] and phasing[i] == "S":

                # reversing
                short_anti_trend = True
                long_anti_trend = False
                return -.3


            # anti trend mode long
            elif high[i] > buy_sig[i] and phasing[i] == "B":

                # reversing
                long_anti_trend = True
                short_anti_trend = False
                return .3


        # you can think of this as the anti-trend mode of function
        else:

            #Long trend mode
            if long_m:
                # intializes trailing stop
                trailing_stop = np.minimum(low[i-1],low[i-2])

                # if sell signal triggered
                if low[i] < trailing_stop:

                    # no reverses in trend mode
                    long_m = False

                    adjust_phasing_long(phasing,begin_index,high,i)
                    return 0


            # short trend mode
            elif short:

                # intializes trailing stop
                trailing_stop = np.maximum(high[i-1],high[i-2])

                # if sell signal triggered
                if high[i] > trailing_stop:

                    # no reverses in trend mode
                    short = False

                    adjust_phasing_short(phasing,begin_index,low,i)
                    return 0

            # long anti-trend mode
            if long_anti_trend:

                # non-reverse
                if phasing[i] == "O" and low[i] < sell_sig[i]:
                    long_anti_trend = False
                    return 0
                
                # non-reverse
                elif phasing[i] == "S" and low[i] > sell_sig[i]:
                    long_anti_trend = False
                    return 0
            
            # short anti-trend mode    
            elif short_anti_trend:

                # non-reverse
                if phasing[i] == "B" and high[i] < buy_sig[i]:
                    short_anti_trend = False
                    return 0
    return 0
    
def hip_method(list1):
        list2 = [None] * len(list1)
        for i in range(len(list1)):
            if i == len(list1) - 1:
                continue
            if (list1[i] > list1[i-1] and list1[i] > list1[i+1]):
                list2[i] = list1[i]
                for j in range(1, (len(list1) - i)):
                    if i+j == len(list1) - 1:
                        continue
                    if (list1[i + j] > list1[i + j - 1] and list1[i + j] > list1[i + j + 1]):
                        #n = 0
                        break
                    else:
                        #n+=1
                        #print(n)
                        list2[i+j] = list1[i]
        return list2


#finds low points in prices
def lop_method(list1):
        list2 = [None] * len(list1)
        for i in range(len(list1)):
            if i == len(list1) - 1:
                continue
            if (list1[i] < list1[i - 1] and list1[i] < list1[i + 1]):
                list2[i] = list1[i]
                for j in range(1, (len(list1) - i)):  # 7,4
                    if i + j == len(list1) - 1:
                        continue
                    if (list1[i + j] < list1[i + j - 1] and list1[i + j] < list1[i + j + 1]):
                        # n = 0
                        break
                    else:
                        # n+=1
                        # print(n)
                        list2[i + j] = list1[i]
        return list2


def adx(px, lookback):
    close = px['close']
    low = px['low']
    high = px['high']
    adx = talib.ADX(high, low, close, timeperiod=lookback)
    return adx[-2]


def sar(px):
    close = px['close']
    opn = px['open']
    low = px['low']
    high = px['high']
    sar = talib.SAR(high, low, acceleration=.02, maximum=.20)
    return sar[-1]


def dmi(px, lookback): 
    pd = talib.PLUS_DI(px['high'], px['low'], px['close'], timeperiod=lookback)
    md = talib.MINUS_DI(px['high'], px['low'], px['close'], timeperiod=lookback)
    return pd, md


def adxr_func(px, lookback):
    close = px['close']
    low = px['low']
    high = px['high']
    signal = talib.ADXR(high, low, close, timeperiod=lookback)
    return signal[-1]


# finds high swing point with respect to ASI (Accumulative Swing  Index)
def hsp_asi(df, list1):
        list2 = [0] * len(list1)

        for i in range(len(list1)):
            if i == len(list1) - 1:
                continue
            if (list1[i] > list1[i-1] and list1[i] > list1[i+1]):
                list2[i] = list1[i]
                for j in range(1, (len(list1) - i)):  #7,4
                    if i+j == len(list1) - 1:
                        continue
                    if (list1[i + j] > list1[i + j - 1] and list1[i + j] > list1[i + j + 1]):
                        #n = 0
                        break
                    else:
                        list2[i+j] = list1[i]
        return list2




 # finds high point with respect to swing index system


def hip_asi(df, list1, hsp):
        list2 = [0] * len(list1)
        for i in range(len(list1)):
            if i == len(list1) - 1:
                continue
            if (list1[i] > list1[i-1] and list1[i] > list1[i+1]):
                list2[i] = list1[i]
                for j in range(1, (len(list1) - i)):  #7,4
                    if i+j == len(list1) - 1:
                        continue
                    if (list1[i + j] > list1[i + j - 1] and list1[i + j] > list1[i + j + 1]):
                        #n = 0
                        break
                    else:
                        #n+=1
                        #print(n)
                        list2[i+j] = list1[i]
            if hsp[i] != hsp[i-1] and list1[i] == list1[i-1]:
                    if list1[i+1] != list1[i]:
                        list2[i] = list1[i+1]

        return list2


# finds low swing point with respect to ASI (Accumulative Swing Index)
def lsp_asi(df, list1):
        list2 = [0] * len(list1)
        for i in range(len(list1)):
            if i == len(list1) - 1:
                continue
            if (list1[i] < list1[i-1] and list1[i] < list1[i+1]):
                list2[i] = list1[i]
                for j in range(1, (len(list1) - i)):  #7,4
                    if i+j == len(list1) - 1:
                        continue
                    if (list1[i + j] < list1[i + j - 1] and list1[i + j] < list1[i + j + 1]):
                        #n = 0
                        break
                    else:
                        #n+=1
                        #print(n)
                        list2[i+j] = list1[i]
        return list2


# finds low point with respect to swing index system
def lop_asi(df, list1, lsp):
        list2 = [0] * len(list1)
        for i in range(len(list1)):
            if i == len(list1) - 1:
                continue
            if (list1[i] < list1[i - 1] and list1[i] < list1[i + 1]):
                list2[i] = list1[i]
                for j in range(1, (len(list1) - i)):  # 7,4
                    if i + j == len(list1) - 1:
                        continue
                    if (list1[i + j] < list1[i + j - 1] and list1[i + j] < list1[i + j + 1]):
                        # n = 0
                        break
                    else:
                        # n+=1
                        # print(n)
                        list2[i + j] = list1[i]
            if lsp[i] != lsp[i - 1] and list1[i] == list1[i - 1]:
                if list1[i + 1] != list1[i]:
                    list2[i] = list1[i + 1]
        return list2


# finds whether two data sets have crossed
def cross(over, under):
        if len(over) == len(under):
            for i in range(len(over)):
                if over[i-1] < under[i-1] and over[i] > under[i]:
                    return True
                else:
                    return False
        else:
            return 'Value error: Lengths of list are not identical.'


def Supertrend(df, atr_period, multiplier):
    
    high = df['high']
    low = df['low']
    close = df['close']
    
    # calculate ATR
    price_diffs = [high - low, 
                   high - close.shift(), 
                   close.shift() - low]
    true_range = pd.concat(price_diffs, axis=1)
    true_range = true_range.abs().max(axis=1)
    # default ATR calculation in supertrend indicator
    atr = true_range.ewm(alpha=1/atr_period,min_periods=atr_period).mean() 
    # df['atr'] = df['tr'].rolling(atr_period).mean()
    
    # HL2 is simply the average of high and low prices
    hl2 = (high + low) / 2
    # upperband and lowerband calculation
    # notice that final bands are set to be equal to the respective bands
    final_upperband = upperband = hl2 + (multiplier * atr)
    final_lowerband = lowerband = hl2 - (multiplier * atr)
    
    # initialize Supertrend column to True
    supertrend = [True] * len(df)
    
    for i in range(1, len(df.index)):
        curr, prev = i, i-1
        
        # if current close price crosses above upperband
        if close[curr] > final_upperband[prev]:
            supertrend[curr] = True
        # if current close price crosses below lowerband
        elif close[curr] < final_lowerband[prev]:
            supertrend[curr] = False
        # else, the trend continues
        else:
            supertrend[curr] = supertrend[prev]
            
            # adjustment to the final bands
            if supertrend[curr] == True and final_lowerband[curr] < final_lowerband[prev]:
                final_lowerband[curr] = final_lowerband[prev]
            if supertrend[curr] == False and final_upperband[curr] > final_upperband[prev]:
                final_upperband[curr] = final_upperband[prev]

        # to remove bands according to the trend direction
        if supertrend[curr] == True:
            final_upperband[curr] = np.nan
        else:
            final_lowerband[curr] = np.nan
    
    return supertrend[-1]
    

def analyze(context,performance):
    return print_report(context)


def print_report(context):
    account = context.account
    portfolio = context.portfolio
    positions = portfolio.positions

    for asset in positions:
        position = positions[asset]
        print(f'position for {asset}:{position.quantity}')

    print(f'total portfolio {portfolio.portfolio_value}')
    print(f'exposure:{account.net_exposure}')

