import datetime
import numpy as np
import talib.abstract as ta
from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
from freqtrade.exchange import date_minus_candles
from typing import Optional
from freqtrade.persistence import Trade

class FastTradeStrategy(IStrategy):
    
    # stoploss = -0.01
    can_short = True

    timeframe = '5m'
    minimal_roi = {
        "0": 1.2
    }


    stoploss = -1

    # 计算rsi
    def caclute_rsi(self, dataframe, timeperiod=5):
        """
        计算rsi超买或超卖区域
        """
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
        """
        计算上下轨线
        """
        midpoints = dataframe['close'].values
        
        x = np.arange(0, length)
        gauss_weights = np.exp(-(x[:, None] - x)**2/(2*h**2)) # 预先计算高斯核函数的权重数组
        y = np.dot(gauss_weights, midpoints)/np.sum(gauss_weights, axis=1) # 一次性计算y值
        mae = np.mean(np.abs(midpoints - y))*mult # 平均绝对误差
        upper_band = y[-1] + mae
        lower_band = y[-1] - mae
 
        return upper_band, lower_band


    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # 1. 计算rsi
        dataframe = self.caclute_rsi(dataframe)
        # 2. 计算atr stop loss
        dataframe = self.atr_stop_loss_finder(dataframe, m=1.0)
        # dataframe = dataframe.tail(500)
        # df = df.tail(500) # 取最近500条数据
        # 3. 计算nadaraya watson envelope
        dataframe['up'] = dataframe['open'] < dataframe['close']
        dataframe['down'] = dataframe['open'] > dataframe['close']

        upper_band, lower_band = self.nadaraya_watson_envelope(dataframe.tail(500))
        dataframe.loc[dataframe.index[-1], 'upper_band'] = upper_band
        dataframe.loc[dataframe.index[-1], 'lower_band'] = lower_band

        # dataframe['lower_band'] = lower_band
        dataframe['cross_up'] = dataframe['close'] > dataframe['upper_band']
        dataframe['cross_down'] = dataframe['close'] < dataframe['lower_band']

        # print(dataframe.tail(20))
        # dataframe['up'] =  dataframe['open'] < dataframe['close']
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
       
       dataframe.loc[
            (
               (dataframe['cross_up'].shift(1)) & (dataframe['up'].shift(1)) &
                ((dataframe['cross_up']) & (dataframe['down'])) & 
                # (dataframe['down']) &
                (dataframe['rsi'] > 70)
            ),
        'enter_short'] = 1

       dataframe.loc[
            (
               (dataframe['cross_down'].shift(1) == True) & (dataframe['down'].shift(1)) &
                ((dataframe['up']) & (dataframe['cross_down'])) &
                # (dataframe['up']) &
                (dataframe['rsi'] < 30)
            ),
        'enter_long'] = 1
       
       return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # 最新蜡烛
        last_candle = dataframe.iloc[-1].squeeze()

        #做多止损， 如果最新收盘价 < 做多止损价， 触发止损
        dataframe.loc[
            (dataframe['enter_long'] == 1) & (last_candle['close'] < dataframe['stop_loss_long']),
            'exit_long'] = 1

        # 做空止损
        dataframe.loc[
            (dataframe['enter_short'] == 1) & (last_candle['close'] > dataframe['stop_loss_short']),
            'exit_short'
        ] = 1

        # dataframe.loc[
        #     dataframe['enter_long'] == 1,
        #     'exit_short'] = 1
        
        # dataframe.loc[
        #     dataframe['enter_short'] == 1,
        #     'exit_long'] = 1
        
        return dataframe
    
    def adjust_trade_position(self, trade: Trade, current_time: datetime,
                            current_rate: float, current_profit: float,
                            min_stake: Optional[float], max_stake: float,
                            current_entry_rate: float, current_exit_rate: float,
                            current_entry_profit: float, current_exit_profit: float,
                            **kwargs) -> Optional[float]:
        """
        在交易期间动态调整交易的仓位大小，以便在交易期间增加或减少仓位。
        """
        dataframe, _ = self.dp.get_analyzed_dataframe(trade.pair, self.timeframe) # 获取交易对的数据

        if len(dataframe) > 2:
            last_candle = dataframe.iloc[-1].squeeze()  # 获取最后一行数据，并转换为Series
            previous_candle = dataframe.iloc[-2].squeeze() # 获取倒数第二行数据，并转换为Series
            signal_name = 'enter_long' if not trade.is_short else 'enter_short'
            prior_date = date_minus_candles(self.timeframe, 1, current_time) # 计算当前时间的前一根K线时间

            # Only enlarge position on new signal.
            # 判断是否需要加仓，如果需要加仓，则返回加仓的仓位大小
            if (
                last_candle[signal_name] == 1 # 最后一根K线的做多或做空信号为1
                and previous_candle[signal_name] != 1 # 倒数第二根K线的做多或做空信号不为1
                and trade.nr_of_successful_entries < 2 # 当前的交易是新交易， 交易的成功入场次数小于2
                and trade.orders[-1].order_date_utc < prior_date # 最后一次交易的时间小于当前时间的前一根K线时间，即最后一次交易的时间在当前K线之前
            ):
                return trade.stake_amount
        return None
    
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