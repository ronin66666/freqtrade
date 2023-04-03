# --- Do not remove these libs ---
import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame
from datetime import datetime

import talib.abstract as ta
from freqtrade.strategy import IStrategy

class HFTFuturesStrategy(IStrategy):
    """
    High-Frequency Trading Futures Strategy using MACD and RSI on 1-minute timeframe.
    """

    # Enable short trading for this strategy
    can_short = True

    # Minimal ROI designed for the strategy.
    minimal_roi = {
        "0": 0.01,  # 1% profit after 0 minutes
        "10": 0.005,  # 0.5% profit after 10 minutes
        "30": 0.001,  # 0.1% profit after 30 minutes
        "60": 0  # break even after 1 hour
    }

    # minimal_roi = {
    #     "0": 100
    # }

    # Stoploss value.
    stoploss = -1  # 2% stoploss

    # Optimal ticker interval for the strategy
    timeframe = '15m'

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['macd'], dataframe['signal'], dataframe['hist'] = ta.MACD(dataframe, fastperiod=12, slowperiod=26, signalperiod=9)
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['macd'] > dataframe['signal']) &
                (dataframe['rsi'] < 30)
            ),
            'enter_long'] = 1

        dataframe.loc[
            (
                (dataframe['macd'] < dataframe['signal']) &
                (dataframe['rsi'] > 70)
            ),
            'enter_short'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['macd'] < dataframe['signal']) &
                (dataframe['rsi'] > 70)
            ),
            'exit_long'] = 1

        dataframe.loc[
            (
                (dataframe['macd'] > dataframe['signal']) &
                (dataframe['rsi'] < 30)
            ),
            'exit_short'] = 1

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
        return 5.0
