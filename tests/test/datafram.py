


import json
import pandas as pd
import talib
import talib.abstract as ta
from scipy import stats
import numpy as np
from scipy.stats import gaussian_kde

import matplotlib.pyplot as plt
from scipy.stats import norm
BTC_PATH_WIN = r'D:\devlop\quant\freqtrade\user_data\data\binance\futures\BTC_USDT_USDT-5m-futures.json'
ETH_PATH_WIN = r'D:\devlop\quant\freqtrade\user_data\data\binance\futures\ETH_USDT_USDT-5m-futures.json'

BTC_PATH_MAC = "/Users/a123/work/quant/freqtrade/user_data/data/binance/futures/BTC_USDT_USDT-5m-futures.json"
ETH_PATH_WIN = "/Users/a123/work/quant/freqtrade/user_data/data/binance/futures/ETH_USDT_USDT-5m-futures.json"

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

def nadaraya_watson_envelope(dataframe, length=500, h=8, mult=3):
        midpoints = dataframe['close'].values
        
        x = np.arange(0, length)
        gauss_weights = np.exp(-(x[:, None] - x)**2/(2*h**2)) # 预先计算高斯核函数的权重数组
        y = np.dot(gauss_weights, midpoints)/np.sum(gauss_weights, axis=1) # 一次性计算y值

        mae = np.mean(np.abs(midpoints - y))*mult # 平均绝对误差

        # 返回最后一个值的上下轨
        upper_band = y[-1] + mae
        lower_band = y[-1] - mae
        # dataframe['upper_band'] = upper_band
        # dataframe['lower_band'] = lower_band
    
        # cross_up = dataframe['close'] > dataframe['upper_band']
        # cross_down = dataframe['close'] < dataframe['lower_band']

        return upper_band, lower_band

__name__ = '__main__'
df = read_data(BTC_PATH_WIN)
df = caclute_rsi(df)
df = atr_stop_loss_finder(df, 'close')
# df['upper_band'] = 0
# df_copy = df.tail(500).copy()
upper_band, lower_band  = nadaraya_watson_envelope(df.tail(500).copy())
# print(df_copy.tail(20))


# 填充数据
# df.iloc[-500:, df.columns.get_loc('upper_band')] = df_copy['upper_band'].values
# df['upper_band'] = df_copy[0]
df.loc[df.index[-1], 'upper_band'] = upper_band
df.loc[df.index[-1], 'lower_band'] = lower_band
df['cross_up'] = df['close'] > df['upper_band']
df['cross_down'] = df['close'] < df['lower_band']
# df.loc[df.index[-1], 'cross_up'] = df['close'] > upper_band
# df.loc[df.index[-1], 'cross_down'] = df['close'] < lower_band

# df['up'] =  df['open'] < df['close']
# dataframe = df.copy();
# dataframe.loc[
#             (
#                ((dataframe['up'].shift(1) == True) & (dataframe['cross_up'].shift(1) == True)) &
#                 ((dataframe['up'] == False) & (dataframe['cross_up'] == True)) & 
#                 (dataframe['rsi'] > 70)
#             ),
#         'enter_short'] = 1

# dataframe.loc[
#             (
#                ((dataframe['up'].shift(1) == False) & (dataframe['cross_down'].shift(1) == True)) &
#                 ((dataframe['up'] == True) & (dataframe['cross_down'] == True)) & 
#                 (dataframe['rsi'] < 30)
#             ),
#         'enter_long'] = 1


# filtered_df = dataframe[dataframe['enter_short'] == 1]
# print(filtered_df)

# df = df[(df['up'].shift(1) == True) & (df['up'] == False)]
# df = df[df['enter_short'] == 1]
print(df.tail(20))

# 当前k线的收盘价大于上轨，且上一根k线的收盘价小于上轨，做空

# 当前k线的收盘价小于下轨，且上一根k线的收盘价大于下轨，做多

