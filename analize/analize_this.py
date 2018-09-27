import pandas as pd
import matplotlib.pyplot as plt

from datetime import datetime
import warnings

from Altcoin.altcoin.getData import getData
from Altcoin.altcoin.coinData import CoinData


def analize_this(interval, start):
    """
    Compare the sma/bma ratio to profit for a coin portfolio
    """
    results = []
    numCoins = len(CoinData.portfolio)
    for sma in range(6, 20):
        start = 2 * sma
        stop = round(3.5 * sma) + 1
        step = (stop - start) // 8
        for bma in range(start, stop, step):
            lma = round(bma * 2.75)
            profit = 0.0
            CoinData.setParams(sma, bma, lma, interval)
            for coin in CoinData.portfolio.values():
                trend, data = coin.trendFollower(start=start)
                profit += trend['Profit'].iloc[-1]

            results.append((sma, bma, lma, profit / numCoins))
    return pd.DataFrame(results, columns=('sma', 'bma', 'lma', 'portfolio profit'))
