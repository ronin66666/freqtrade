import datetime
import numpy as np
import talib.abstract as ta
from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame

class FastTradeStrategy(IStrategy):
    
    # stoploss = -0.01
    can_short = True

    timeframe = '5m'
    minimal_roi = {
        "0": 1.5
    }

    stoploss = -1

    # 计算rsi
    def caclute_rsi(self, dataframe, timeperiod=5):
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=timeperiod)
        return dataframe
    
    def atr_stop_loss_finder(self, dataframe, source="close", length=14, smoothing="RMA", m=0.5):
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
    
    def nadaraya_watson_envelope(self, dataframe, length=500, h=8, mult=3):
        midpoints = dataframe['close'].values
        
        x = np.arange(0, length)
        gauss_weights = np.exp(-(x[:, None] - x)**2/(2*h**2)) # 预先计算高斯核函数的权重数组
        y = np.dot(gauss_weights, midpoints)/np.sum(gauss_weights, axis=1) # 一次性计算y值
        mae = np.mean(np.abs(midpoints - y))*mult # 平均绝对误差
        upper_band = y + mae
        lower_band = y - mae
        # dataframe['upper_band'] = upper_band
        # dataframe['lower_band'] = lower_band
    
        # dataframe['cross_up'] = dataframe['close'] > dataframe['upper_band']
        # dataframe['cross_down'] = dataframe['close'] < dataframe['lower_band']
        return upper_band, lower_band


    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # 1. 计算rsi
        dataframe = self.caclute_rsi(dataframe)
        # 2. 计算atr stop loss
        dataframe = self.atr_stop_loss_finder(dataframe)
        # dataframe = dataframe.tail(500)
        # df = df.tail(500) # 取最近500条数据
        # 3. 计算nadaraya watson envelope
        upper_band, lower_band = self.nadaraya_watson_envelope(dataframe.tail(500))
        dataframe['upper_band'] = upper_band
        dataframe['lower_band'] = lower_band
        dataframe['cross_up'] = dataframe['close'] > dataframe['upper_band']
        dataframe['cross_down'] = dataframe['close'] < dataframe['lower_band']
        dataframe['up'] =  dataframe['open'] < dataframe['close']
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
       
       dataframe.loc[
            (
               (dataframe['cross_up'] == True) &
                # (dataframe['up'] == False) & 
                (dataframe['rsi'] > 70)
            ),
        'enter_short'] = 1
       
       dataframe.loc[
            (
               (dataframe['cross_down'] == True) &
                # (dataframe['up'] == True) & 
                (dataframe['rsi'] < 30)
            ),
        'enter_long'] = 1
       
       return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe['low'] < dataframe['stop_loss_long']),
            'exit_short'] = 1
        dataframe.loc[
            dataframe['high'] > dataframe['stop_loss_short'],
            'exit_long'] = 1
        # dataframe.loc[
        #     dataframe['enter_long'] == 1,
        #     'exit_short'] = 1
        
        # dataframe.loc[
        #     dataframe['enter_short'] == 1,
        #     'exit_long'] = 1
        
        return dataframe
    
    def leverage(self, pair: str, current_time: datetime, current_rate: float,
                 proposed_leverage: float, max_leverage: float, side: str,
                 **kwargs) -> float:
        """
        Customize leverage for each new trade. This method is only called in futures mode.

        :param pair: Pair that's currently analyzed
        :param current_time: datetime object, containing the current datetime
        :param current_rate: Rate, calculated based on pricing settings in exit_pricing.
        :param proposed_leverage: A leverage proposed by the bot.
        :param max_leverage: Max leverage allowed on this pair
        :param entry_tag: Optional entry_tag (buy_tag) if provided with the buy signal.
        :param side: 'long' or 'short' - indicating the direction of the proposed trade
        :return: A leverage amount, which is between 1.0 and max_leverage.
        """
        return 100.0