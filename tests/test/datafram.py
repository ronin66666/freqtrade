


import json
import pandas as pd
import talib
import talib.abstract as ta
from scipy import stats
import numpy as np
from scipy.stats import gaussian_kde

import matplotlib.pyplot as plt
from scipy.stats import norm
BTC_PATH = r'D:\devlop\quant\freqtrade\user_data\data\binance\futures\BTC_USDT_USDT-5m-futures.json'
ETH_PATH = r'D:\devlop\quant\freqtrade\user_data\data\binance\futures\ETH_USDT_USDT-5m-futures.json'

# 读取json文件
def read_data(file_name):
    
    with open(file_name, 'r') as f:
        data = json.load(f)
        
    # df = pd.read_json(file_name)
    df = pd.DataFrame(data, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    return df

# 计算rsi

def caclute_rsi(dataframe, timeperiod=5):
    dataframe['rsi'] = ta.RSI(dataframe, timeperiod=timeperiod)
    return dataframe

def moving_average(atr, length, smoothing="RMA"):
    """
    Function to calculate the moving average 平均真实波动范围
    source: the source to calculate the moving average from (atr)
    """
    rma = ta.RMA(atr, length) # 不支持，需尝试其他办法
    sma = ta.SMA(atr, length)
    ema = ta.EMA(atr, length)
    wma = ta.WMA(atr, length)
    if smoothing == "RMA":
        return rma
    elif smoothing == "SMA":
        return sma
    elif smoothing == "EMA":
        return ema
    else:
        return wma


def atr_stop_loss_finder(dataframe, source="close", length=14, smoothing="RMA", m=0.5):
    """
    该指标使用平均真实范围 ATR 来确定设置止损的安全位置，
    以避免因止损过紧而被止损或止损退出交易.默认乘数设置为 1.5。对于更保守的止损，请使用 2,
    对于更严格的止损，请使用 1。A
    """

    # ATR = max(high - low, abs(high - close[1]), abs(low - close[1]))

    dataframe['atr'] = ta.ATR(dataframe, timeperiod=length)

    # ma = moving_average(dataframe['atr'], length=length, smoothing="smoothing")

    ma = ta.SMA(dataframe['atr'], length)
    dataframe['ma'] = ma
    dataframe['stop_loss_long'] = dataframe['low'] - ma * m     # 多头止损
    dataframe['stop_loss_short'] = dataframe['high'] + ma * m   # 空头止损
    return dataframe

def nwe(dataframe, window_size=500, n_kernels=8, std_multiplier=3):
    # calculate midpoints
    midpoints = (dataframe['open'] + dataframe['close']) / 2
    # print(midpoints)

    # calculate kernel width
    kernel_width = window_size // n_kernels
    # print(kernel_width)

    # calculate weights for each midpoint
    weights = []
    for midpoint in midpoints:
        kernel_weights = []
        for i in range(n_kernels):
            x = midpoint - i * kernel_width
            print("x:", x, "midpoint:", midpoint, "i:", i, "kernel_width:", kernel_width)
            kernel_weights.append(stats.norm.pdf(x))
        # print(kernel_weights)
        weights.append(np.mean(kernel_weights))

    # print(weights)
    # calculate weighted moving average
    # wma = pd.Series(midpoints).rolling(window=window_size).apply(lambda x: np.dot(x, weights) / sum(weights), raw=True)

    # # calculate standard deviation
    # std = pd.Series(midpoints).rolling(window=window_size).std()

    # # calculate upper and lower bands
    # dataframe['upper_band'] = wma + std * std_multiplier
    # dataframe['lower_band'] = wma - std * std_multiplier

    return dataframe

def nwe2(df, length=500, bandwidth=8, mult=3):
    midpoints = (df['open'] + df['close']) / 2
    kernel_width = length // 8
    
    upper_band = np.zeros(length)
    lower_band = np.zeros(length)
    
    for i in range(length):
        kernel_values = np.zeros(length)
        weights = np.zeros(length)
        for j in range(length):
            x = midpoints[j] - midpoints[i]
            kernel_values[j] = np.exp(-(x/bandwidth)**2/2) / (bandwidth * np.sqrt(2*np.pi))
            if kernel_values[j] > 0.0001:
                weights[j] = 1
        if np.sum(weights) > 0:
            kde = gaussian_kde(midpoints, weights=weights*kernel_values)
            y = kde(midpoints[i])
            mae = np.mean(np.abs(midpoints - y)) * mult
            upper_band[i] = y + mae
            lower_band[i] = y - mae
    print(upper_band)
    return upper_band, lower_band
    # return upper_band, lower_band

__name__ = '__main__'
df = read_data(BTC_PATH)
df = caclute_rsi(df)
df = atr_stop_loss_finder(df, 'close')

df = df.tail(500)
nwe2(df)

# plt.plot(df.index, df['close'], label='close')
# plt.plot(df.index, upper_band, label='upper band')
# plt.plot(df.index, lower_band, label='lower band')
# plt.legend()
# plt.show()

# print(df.tail(10))


