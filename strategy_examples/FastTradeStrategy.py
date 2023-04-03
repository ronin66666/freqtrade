import talib.abstract as ta
from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame

class FastTradeStrategy(IStrategy):
    timeframe = '5m'
    minimal_roi = {
        "0": 0.01
    }
    stoploss = -0.01

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['macd'], dataframe['signal'], dataframe['hist'] = ta.MACD(dataframe, fastperiod=12, slowperiod=26, signalperiod=9)
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        return dataframe
    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
             (dataframe['macd'] > dataframe['signal']) &
             (dataframe['rsi'] < 30)
            ),
            'buy'] = 1

        return dataframe

def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    dataframe.loc[
        (
            (dataframe['macd'] < dataframe['signal']) &
            (dataframe['rsi'] > 70)
        ),
        'sell'] = 1

    return dataframe