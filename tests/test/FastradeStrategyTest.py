import datetime
from datetime import datetime
import numpy as np
import talib.abstract as ta
from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
from freqtrade.exchange import date_minus_candles
from typing import Optional, Union
from freqtrade.persistence import Trade
import logging

from freqtrade.strategy.strategy_helper import stoploss_from_open

class FastTradeStrategyTest(IStrategy):
    
    can_short = True
    

    timeframe = '5m'

    # 最小投资回报率
    minimal_roi = { 
        "0": 100
    }

    # trailing_stop
    stoploss = -1

    use_custom_stosoploss = True # 使用自定义止损
    # trailing_stop_pitive_offset = 0.3 # 设置最小利润
    

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
        upper_band = y + mae
        lower_band = y - mae
      
        return upper_band, lower_band


    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # print(dataframe.tail(10))
        
        # print("excute populate_indicators: pair = ", metadata['pair'])

        # 1. 计算rsi
        dataframe = self.caclute_rsi(dataframe)
        # 2. 计算atr stop loss
        dataframe = self.atr_stop_loss_finder(dataframe, m=2.0)
        
        # 3. 计算nadaraya watson envelope
        dataframe['up'] = dataframe['open'] < dataframe['close']
        dataframe['down'] = dataframe['open'] > dataframe['close']

        dataframe['upper_band'] = np.nan
        dataframe['lower_band'] = np.nan

        upper_band, lower_band = self.nadaraya_watson_envelope(dataframe.tail(500))
        
        dataframe.iloc[-500:, dataframe.columns.get_loc('upper_band')] = upper_band
        dataframe.iloc[-500:, dataframe.columns.get_loc('lower_band')] = lower_band

        # dataframe['lower_band'] = lower_band
        dataframe['cross_up'] = dataframe['close'] > dataframe['upper_band']
        dataframe['cross_down'] = dataframe['close'] < dataframe['lower_band']

        # print(dataframe.tail(10))

        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

       # 前一根k线 上涨且上穿上轨线，且rsi > 70， 当前k线为跌且收盘价 > 上轨线，做空
       dataframe.loc[
            (
               (dataframe['cross_up'].shift(1)) & (dataframe['up'].shift(1)) &
                ((dataframe['cross_up']) & (dataframe['down'])) & 
                # (dataframe['down']) &
                (dataframe['rsi'] > 80)
            ),
        ['enter_short', 'enter_tag']] = (1, 'enter_short_signal')

         # 前一根k线 下跌且下穿下轨线，且rsi < 30， 当前k线为涨且收盘价 < 下轨线，做多
       dataframe.loc[
            (
               (dataframe['cross_down'].shift(1)) & (dataframe['down'].shift(1)) &
                ((dataframe['up']) & (dataframe['cross_down'])) &
                # (dataframe['up']) &
                (dataframe['rsi'] < 20)
            ),
        ['enter_long', 'enter_tag']] = (1, 'enter_long_signal')
       
       return dataframe
    
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        dataframe.loc[
            dataframe['enter_long'] == 1,
            ['exit_short', 'exit_tag']] = (1, 'exit_with_long_signal')
        
        dataframe.loc[
            dataframe['enter_short'] == 1,
            ['exit_long', 'exit_tag']] = (1, 'exit_with_short_signal')
        
        return dataframe
    
    def adjust_trade_position(self, trade: Trade, current_time: datetime,
                            current_rate: float, current_profit: float,
                            min_stake: Optional[float], max_stake: float,
                            current_entry_rate: float, current_exit_rate: float,
                            current_entry_profit: float, current_exit_profit: float,
                            **kwargs) -> Optional[float]:
        print("excute adjust_trade_position, pair = ", trade.pair)
        """
        在交易期间动态调整交易的仓位大小，以便在交易期间增加或减少仓位。
        """
        dataframe, _ = self.dp.get_analyzed_dataframe(trade.pair, self.timeframe) # 获取交易对的数据

        if len(dataframe) > 2:
            last_candle = dataframe.iloc[-1].squeeze()  # 获取最后一行数据，并转换为Series
            previous_candle = dataframe.iloc[-2].squeeze() # 获取倒数第二行数据，并转换为Series
            signal_name = 'enter_long' if not trade.is_short else 'enter_short'
            prior_date = date_minus_candles(self.timeframe, 1, current_time) # 获取当前时间的前一根K线时间

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
        
        if pair == 'BTC/USDT:USDT' or pair == 'ETH/USDT:USDT':  
            return 50.0

        return 25.0
    
    def custom_exit(self, pair: str, trade: Trade, current_time: datetime, current_rate: float,
                    current_profit: float, **kwargs) -> Optional[Union[str, bool]]:
        # print("excute custom_exit pair = ", pair)

        """
        自定义出场逻辑
        """
        # 获取之前开仓时的dataframe的k线数据
        # open_exec_date = trade.open_date_utc.strftime('%Y-%m-%d %H:%M:00+00:00')
        # print("open_exec_date = ", open_exec_date)
        analyzed_dataframe, dateTime = self.dp.get_analyzed_dataframe(pair, self.timeframe)

        #找到最近一次开单的k线数据
        signal_name = 'enter_long' if not trade.is_short else 'enter_short'

        signal_candles = analyzed_dataframe[analyzed_dataframe[signal_name] == 1]
        if len(signal_candles) == 0:
            return None
        last_candle = signal_candles.iloc[-1].squeeze()

        if signal_name == 'enter_long' and current_rate < last_candle['stop_loss_long']:
            logging.info("exit_long_stop_loss, pair = %s, current_rate = %s, stop_loss_long = %s", pair, current_rate, last_candle['stop_loss_long'])
            return 'exit_long_stop_loss'
        elif signal_name == 'enter_short' and current_rate > last_candle['stop_loss_short']:
            logging.info("exit_short_stop_loss, pair = %s, current_rate = %s, stop_loss_short = %s", pair, current_rate, last_candle['stop_loss_short'])
            return 'exit_short_stop_loss'
        else:
            return None
    
    
    def custom_stoploss(self, pair: str, trade: Trade, current_time: datetime, current_rate: float, current_profit: float, **kwargs) -> float:
        """
        自定义止损点，返回止损点，这里只能做移动向上止损，如果返回值低于之前设置的止损点，则该返回值会被忽略，
        在首次交易调用此方法之前，它将被设定为初始止损stoploss，并且仍然是必需的。

        对于多头交易（longs），current_profit 的取值范围是 -1 到正无穷；而对于卖空交易（shorts），current_profit 的取值范围是负无穷到 1。
        """
        custom_stoploss = -1.0

        if current_profit > 0.3 and current_profit < 1.0: 
            custom_stoploss = stoploss_from_open(0.5, current_profit, is_short=trade.is_short, leverage=trade.leverage)

        elif current_profit >= 1.0:
            custom_stoploss = stoploss_from_open(0.2, current_profit, is_short=trade.is_short, leverage=trade.leverage)
            
        logging.info("excute custom_stoploss, pair = %s, current_profit = %s, custom_stoploss = %s self.stoploss = %s", pair, current_profit, custom_stoploss, self.stoploss)

        return custom_stoploss
    
    def confirm_trade_exit(self, pair: str, trade: Trade, order_type: str, amount: float,
                           rate: float, time_in_force: str, exit_reason: str,
                           current_time: datetime, **kwargs) -> bool:
        
        if trade.is_open and (exit_reason == 'exit_with_long_signal' or exit_reason == 'exit_with_short_signal'):
            logging.info('confirm_trade_exit false exit_reason = %s', exit_reason)
            return False
        return True