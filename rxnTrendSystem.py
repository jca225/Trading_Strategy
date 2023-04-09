
import numpy as np
import Roman as rm



# determines index to begin phasing
def initPhasing(phasing,high,low,close,lookback=27):

    # simple algorithm to calculate whether to take the significant low or high price; we calculate the average price
    # over a 27 day range and find the greatest distance between the lows and highs to this average point. out of these,
    # we choose the most significant and compare the most significant low with the most significant high. Which ever is greater
    # is the day we begin phasing on and will decide whether we begin with "B" or "S" as per the Reaction Trend System
    
    xbar = 0 # holds average
    hip = rm.hip_method(high)
    lop = rm.lop_method(low)
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
    

# setting up dummy variables to hold true values
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
    high = df['High']
    low = df['Low']
    close = df['Close']

    # intializing variables 
    long = False
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
                long = True
                long_anti_trend = False
                short_anti_trend = False

            # trend mode short
            if low[i] < lbop[i]:
                begin_index = i

                # trend mode is always reversing
                short = True
                long_anti_trend = False
                short_anti_trend = False


            # check for anti-trend signals


            # anti trend mode short
            elif low[i] < sell_sig[i] and phasing[i] == "S":

                # reversing
                short_anti_trend = True
                long_anti_trend = False


            # anti trend mode long
            elif high[i] > buy_sig[i] and phasing[i] == "B":

                # reversing
                long_anti_trend = True
                short_anti_trend = False


        # you can think of this as the anti-trend mode of function
        else:

            #Long trend mode
            if long:
                # intializes trailing stop
                trailing_stop = np.minimum(low[i-1],low[i-2])

                # if sell signal triggered
                if low[i] < trailing_stop:

                    # no reverses in trend mode
                    long = False

                    adjust_phasing_long(phasing,begin_index,high,i)


            # short trend mode
            elif short:

                # intializes trailing stop
                trailing_stop = np.maximum(high[i-1],high[i-2])

                # if sell signal triggered
                if high[i] > trailing_stop:

                    # no reverses in trend mode
                    short = False

                    adjust_phasing_short(phasing,begin_index,low,i)

            # long anti-trend mode
            if long_anti_trend:

                # non-reverse
                if phasing[i] == "O" and low[i] < sell_sig[i]:
                    long_anti_trend = False
                
                # non-reverse
                if phasing[i] == "S" and low[i] > sell_sig[i]:
                    long_anti_trend = False
            
            # short anti-trend mode    
            elif short_anti_trend:

                # non-reverse
                if phasing[i] == "B" and high[i] < buy_sig[i]:
                    short_anti_trend = False
                

    
        return long, short, long_anti_trend, short_anti_trend

