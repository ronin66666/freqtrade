import json
from pandas import DataFrame
import talib
import talib.abstract as ta
from scipy import stats
import numpy as np
from scipy.stats import gaussian_kde

import matplotlib.pyplot as plt
from scipy.stats import norm

import qtpylib

BTC_PATH_WIN = (
    r"D:\devlop\quant\freqtrade\user_data\data\binance\futures\BTC_USDT_USDT-5m-futures.json"
)
ETH_PATH_WIN = (
    r"D:\devlop\quant\freqtrade\user_data\data\binance\futures\ETH_USDT_USDT-5m-futures.json"
)

BTC_PATH_MAC = (
    "/Users/a123/work/quant/freqtrade/user_data/data/binance/futures/BTC_USDT_USDT-5m-futures.json"
)
ETH_PATH_WIN = (
    "/Users/a123/work/quant/freqtrade/user_data/data/binance/futures/ETH_USDT_USDT-5m-futures.json"
)


# 读取json文件
def read_data(file_name):
    with open(file_name, "r") as f:
        data = json.load(f)

    # df = pd.read_json(file_name)
    datafram = DataFrame(data, columns=["date", "open", "high", "low", "close", "volume"])
    return datafram


# 计算rsi
def caclute_rsi(dataframe, timeperiod=5):
    dataframe["rsi"] = ta.RSI(dataframe, timeperiod=timeperiod)
    return dataframe


def moving_average(atr, length, smoothing="RMA"):
    """
    Function to calculate the moving average 平均真实波动范围
    source: the source to calculate the moving average from (atr)
    """
    rma = ta.RMA(atr, length)  # 不支持，需尝试其他办法
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

    dataframe["atr"] = ta.ATR(dataframe, timeperiod=length)

    # ma = moving_average(dataframe['atr'], length=length, smoothing="smoothing")

    ma = ta.SMA(dataframe["atr"], length)
    dataframe["ma"] = ma
    dataframe["stop_loss_long"] = dataframe["low"] - ma * m  # 多头止损
    dataframe["stop_loss_short"] = dataframe["high"] + ma * m  # 空头止损
    return dataframe


def nadaraya_watson_envelope(dataframe, length=10, h=8, mult=3):
    """
    计算上下轨线
    """
    midpoints = dataframe["close"].values

    x = np.arange(0, length)
    gauss_weights = np.exp(-((x[:, None] - x) ** 2) / (2 * h**2))  # 预先计算高斯核函数的权重数组
    y = np.dot(gauss_weights, midpoints) / np.sum(gauss_weights, axis=1)  # 一次性计算y值
    mae = np.mean(np.abs(midpoints - y)) * mult  # 平均绝对误差
    upper_band = y + mae
    lower_band = y - mae

    return upper_band, lower_band

def populate_indicators(dataframe: DataFrame, metadata: dict) -> DataFrame:
    
        # 1. 计算rsi
        dataframe = caclute_rsi(dataframe)
        # 2. 计算atr stop loss
        dataframe = atr_stop_loss_finder(dataframe, m=2.0)
        
        # 3. 计算nadaraya watson envelope
        dataframe['up'] = dataframe['open'] < dataframe['close']
        dataframe['down'] = dataframe['open'] > dataframe['close']

        # dataframe['upper_band'] = np.nan
        # dataframe['lower_band'] = np.nan

        # upper_band, lower_band = nadaraya_watson_envelope(dataframe.tail(500))
        # qtpylob.indicators.ris.plot_candles(dataframe.tail(500), title="BTC/USDT", showlegend=False)
         qtpylib.indicators.ris(dataframe)
        # dataframe.iloc[-500:, dataframe.columns.get_loc('upper_band')] = upper_band
        # dataframe.iloc[-500:, dataframe.columns.get_loc('lower_band')] = lower_band
        

        # dataframe['lower_band'] = lower_band
        dataframe['cross_up'] = dataframe['close'] > dataframe['upper_band']
        dataframe['cross_down'] = dataframe['close'] < dataframe['lower_band']

        # print(dataframe.tail(10))

        return dataframe

__name__ = "__main__"
dataframe = read_data(BTC_PATH_MAC)
dataframe = caclute_rsi(dataframe)
dataframe = atr_stop_loss_finder(dataframe, "close")

w = 500

dataframe = dataframe.tail(1500).copy()

dataframe["upper_band"] = np.nan
dataframe["lower_band"] = np.nan

upper_band, lower_band = nadaraya_watson_envelope(dataframe.tail(500))

dataframe.iloc[-500:, dataframe.columns.get_loc("upper_band")] = upper_band
dataframe.iloc[-500:, dataframe.columns.get_loc("lower_band")] = lower_band

print(dataframe.head(20))
print(dataframe.tail(20))
