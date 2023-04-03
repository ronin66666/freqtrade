# flake8: noqa: F401
# isort: skip_file
# --- Do not remove these libs ---
from datetime import datetime
from typing import Optional

import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame

import talib.abstract as ta
from freqtrade.persistence import Trade
from freqtrade.strategy import (CategoricalParameter, DecimalParameter,
                                IntParameter, IStrategy)
from freqtrade.exchange import date_minus_candles
import freqtrade.vendor.qtpylib.indicators as qtpylib

from technical.util import resample_to_interval, resampled_merge


class VolatilitySystem(IStrategy):
    """
    Volatility System strategy.
    Based on https://www.tradingview.com/script/3hhs0XbR/

    Leverage is optional but the lower the better to limit liquidations
    """
    can_short = True  # 是否支持做空交易

    # Minimum Return on Investment，最小投资回报，其中的键表示时间（以分钟为单位），值表示从交易开始后的相应时间点开始，最小期望的回报率。
    minimal_roi = {
        "0": 100
    }
    
    # Stoploss，止损：用于设定一个固定的止损比例，以便在交易亏损达到特定百分比时自动出场。这有助于限制单笔交易的潜在损失，并降低整体风险。
    # -1 表示无止损
    # stoploss = -0.03，表示当交易亏损达到 3% 策略将触发止损卖出/买入操作
    stoploss = -1

    # 表示用于计算技术指标和生成交易信号的K线（candlestick）时间周期。
    timeframe = '1h'

    # 用于配置策略在图表中显示的指标。它允许您定义主要图表以及子图表上的技术指标，以便在策略回测时，可以通过图表直观地查看策略的执行情况。
    # Volatility system" 的子图 其中包含两个指标：ATR和绝对收盘价变动(abs_close_change), ATR的线条颜色为白色，绝对收盘价变动的线条颜色为红色
    plot_config = {
        # Main plot indicators (Moving averages, ...)
        'main_plot': {
        },
        'subplots': {
            "Volatility system": {
                "atr": {"color": "white"},
                "abs_close_change": {"color": "red"},
            }
        }
    }

    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Adds several indicators to the given DataFrame

        向传入的 DataFrame 中添加指标。这个函数计算所需的技术指标，并将它们附加到 DataFrame 上，
        以便在其他策略函数（如 populate_buy_trend 和 populate_sell_trend)中使用这些指标来确定交易信号。

        """

        # 设定重新采样的时间间隔（resample_int）为 3 小时（60 分钟 * 3）。这意味着在计算技术指标时，将使用 3 小时的数据。
        resample_int = 60 * 3 
        
        # resample_to_interval 原始 DataFrame 重新采样到 3 小时的时间间隔。。
        resampled = resample_to_interval(dataframe, resample_int)


        # Average True Range (ATR)
        # 计算 14 个周期的 Average True Range（ATR）指标，并将其值乘以 2.0。将结果添加到重新采样的 DataFrame 中。
        resampled['atr'] = ta.ATR(resampled, timeperiod=14) * 2.0

        # Absolute close change
        # 计算价格的绝对收盘价变动，将其添加到重新采样的 DataFrame 中。
        resampled['close_change'] = resampled['close'].diff()
        resampled['abs_close_change'] = resampled['close_change'].abs()

        # 将重新采样的 DataFrame 与原始 DataFrame 合并，并填充缺失值。
        dataframe = resampled_merge(dataframe, resampled, fill_na=True)
        dataframe['atr'] = dataframe[f'resample_{resample_int}_atr']
        dataframe['close_change'] = dataframe[f'resample_{resample_int}_close_change']
        dataframe['abs_close_change'] = dataframe[f'resample_{resample_int}_abs_close_change']

        # Average True Range (ATR)
        # dataframe['atr'] = ta.ATR(dataframe, timeperiod=14) * 2.0
        # Absolute close change
        # dataframe['close_change'] = dataframe['close'].diff()
        # dataframe['abs_close_change'] = dataframe['close_change'].abs()

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the buy and sell signals for the given dataframe
        :param dataframe: DataFrame
        :return: DataFrame with buy and sell columns
        """
        # Use qtpylib.crossed_above to get only one signal, otherwise the signal is active
        # for the whole "long" timeframe.
        dataframe.loc[
            # qtpylib.crossed_above(dataframe['close_change'] * 1, dataframe['atr']),
            (dataframe['close_change'] * 1 > dataframe['atr'].shift(1)),
            'enter_long'] = 1
        dataframe.loc[
            # qtpylib.crossed_above(dataframe['close_change'] * -1, dataframe['atr']),
            (dataframe['close_change'] * -1 > dataframe['atr'].shift(1)),
            'enter_short'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        use sell/buy signals as long/short indicators
        """
        dataframe.loc[
            dataframe['enter_long'] == 1,
            'exit_short'] = 1
        dataframe.loc[
            dataframe['enter_short'] == 1,
            'exit_long'] = 1
        return dataframe

    def custom_stake_amount(self, pair: str, current_time: datetime, current_rate: float,
                            proposed_stake: float, min_stake: Optional[float], max_stake: float,
                            leverage: float, entry_tag: Optional[str], side: str,
                            **kwargs) -> float:
        # 50% stake amount on initial entry
        return proposed_stake / 2

    position_adjustment_enable = True

    def adjust_trade_position(self, trade: Trade, current_time: datetime,
                              current_rate: float, current_profit: float,
                              min_stake: Optional[float], max_stake: float,
                              current_entry_rate: float, current_exit_rate: float,
                              current_entry_profit: float, current_exit_profit: float,
                              **kwargs) -> Optional[float]:
        dataframe, _ = self.dp.get_analyzed_dataframe(trade.pair, self.timeframe)
        if len(dataframe) > 2:
            last_candle = dataframe.iloc[-1].squeeze()
            previous_candle = dataframe.iloc[-2].squeeze()
            signal_name = 'enter_long' if not trade.is_short else 'enter_short'
            prior_date = date_minus_candles(self.timeframe, 1, current_time)
            # Only enlarge position on new signal.
            if (
                last_candle[signal_name] == 1
                and previous_candle[signal_name] != 1
                and trade.nr_of_successful_entries < 2
                and trade.orders[-1].order_date_utc < prior_date
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
        return 20.0
