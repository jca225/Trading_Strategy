import numpy as np
import SILibrary as rm

def calculate_asi(px,high,close):
        # initializing variables to be used
        c1 = []
        c2 = []
        c3 = []
        c4 = []
        c5 = []
        c6 = []
        c7 = []
        n = []
        r = []
        si = []
        asi = []
        k = []
        l = 3.00

        # calculations for swing index system
        for i in (range(len(px))):
            # cannot be calculated on first day
            if i == 0:
                asi.insert(0, 0)
                continue
            c1.append(abs(high[i] - close[i - 1]))
            c2.append(abs(low[i] - close[i - 1]))
            c3.append(abs(high[i] - low[i]))
            c4.append(abs(close[i - 1] - opn[i - 1]))
            c5.append(close[i] - close[i - 1])
            c6.append(close[i] - opn[i])
            c7.append(close[i - 1] - opn[i - 1])

        for i in range(len(c1)):
            k.append(np.maximum(c1[i], c2[i]))
            n.append((c5[i] + (0.5 * c6[i]) + (0.25 * c7[i])))

            if c1[i] == max(c1[i], c2[i], c3[i]):
                r.append(c1[i] - (0.5 * c2[i]) + (0.25 * c4[i]))

            elif c2[i] == max(c1[i], c2[i], c3[i]):
                r.append(c2[i] - (0.5 * c1[i]) + (0.25 * c4[i]))

            elif c3[i] == max(c1[i], c2[i], c3[i]):
                r.append(c3[i] + (0.25 * c4[i]))
            si.append(50 * (n[i] / r[i]) * (k[i] / l))

            asi.append(sum(si))
        return asi


def swing_index(px):

    hsp = []
    lsp = []
    hip = []
    lop = []
    close = px['close']
    low = px['low']
    high = px['high']

    
    asi = calculate_asi(px,high,close)

    # calculations for finding hsp
    hsp = rm.hsp_asi(px,asi)


    # calculations for finding hip
    hip = rm.hip_asi(px,high,hsp)


    # calculations for finding lsp
    lsp = rm.lsp_asi(px,asi)

    # calculations for finding lop
    lop = rm.lop_asi(px,low,lsp)

    # initialize and declare trailing stop for long trades only
    trailing_stop_long = [None] * len(hsp)
    for i in range(len(hsp)):

        # we want to deal with numbers
        if hsp[i] == None:
            continue

        else:

            # check to see if a new hsp is made
            if hsp[i] != hsp[i-1]:

                
                for j in range(len(hsp) - i):
                    if abs(hsp[i] - asi[i+j]) > 60:
                        trailing_stop_long[i + j] = low[i]
                        continue


    return asi[-1], hsp[-2], hip[-2], lsp[-2], lop[-2], trailing_stop_long[-2]

