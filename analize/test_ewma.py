import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import logging

from Altcoin.altcoin.getData import getData
from Altcoin.altcoin.Stop_Loss import init, plotDataset, dollarTotal, plotDollars

log = logging.getLogger(__name__)

sma = [1, 1, 2, 2, 3, 3, 4, 5, 5, 6, 6, 7, 7, 8, 9, 9, 10, 10, 11, 11, 12, 13, 13, 14, 14, 15, 15, 16]
bma = [2, 3, 5, 6, 8, 9, 11, 13, 14, 16, 17, 19, 20, 22, 24, 25, 27, 28, 30, 31, 33, 35, 36, 38, 39, 41, 42, 44]
intervals = ['3h', '6h', '12h', '1D']


# prepare a DataFrame for eack coin
def prepareData(syms, step, start):
    data = {}
    for sym in syms:
        df = getData(sym, step)
        for idx in range(len(bma)):
            df['sewma_{}'.format(sma[idx])] = df['close'].ewm(span=sma[idx]).mean()
            df['bewma_{}'.format(bma[idx])] = df['close'].ewm(span=bma[idx]).mean()

        df = df.loc[start:].copy()
        df['returns'] = df['close'].pct_change(2)
        # df['Dollar Return'] = 1000 * df['close']/df['close'].iloc[0]
        data[sym] = df
    return data


# plot for each combo sma/bma a portfolio
def test_best_ewma(coins, step, start, show=True):
    if show:
        fig, ax = plt.subplots(4, 7, figsize=(14, 8))
    syms = [coin[:3] for coin in coins]
    count = 0
    data = prepareData(syms, step, start)
    profit = {}
    for idx in range(len(bma)):
        dollars = []
        stop_dollars = []
        cols = ('open close high sewma_{} bewma_{} returns'.format(sma[idx], bma[idx])).split()
        for sym in syms:
            df = data[sym][cols]
            price, stop_price = init(df, (cols[3], cols[4]))
            dollars.append(dollarTotal(df, price, 'Total'))
            stop_dollars.append(dollarTotal(df, stop_price, 'Stop_Total'))

        if show:
            row = count // 7
            col = count % 7
            ax[row, col].bar(syms, dollars, label='dollar')
            ax[row, col].bar(syms, stop_dollars, label='stop_dollar', alpha=0.5)
            ax[row, col].set_title('{}/{}'.format(sma[idx], bma[idx]))
            plt.tight_layout()
            count += 1

        dollar_tot = sum([x - 1000 for x in dollars])
        stop_tot = sum([x - 1000 for x in stop_dollars])
        profit[bma[idx]] = [dollar_tot, stop_tot]

    df = pd.DataFrame.from_dict(profit, orient='index')
    df.columns = ('dollar', 'stop_dollar')
    df.index.name = 'BMA'
    return df


# Now we test for each sma.bma over a portfolio and compare how this
# looks over different sampling frequencies
def profit_over_intervals(coins, start, interval=intervals):
    fig, ax = plt.subplots(1, 4, figsize=(16, 4), sharex=True)
    count = 0
    for delta in intervals:
        df = test_best_ewma(coins, delta, start, False)
        max = df.idxmax()
        df.plot(ax=ax[count], title='{0} max-bma: dollar {1[0]} stop {1[1]}'.format(delta, max))
        ax[count].grid(color='b', alpha=0.5, linestyle='--', lw=0.5)
        count += 1

    plt.tight_layout()
    plt.show()
