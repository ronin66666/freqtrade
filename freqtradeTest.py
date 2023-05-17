from freqtrade import main

from freqtrade.strategy.strategy_helper import stoploss_from_open
# freqtrade backtesting --timerange 20230506- -c config_fast_btc.json --strategy FastTradeStrategy

CONFIG_PATH = '/Users/a123/work/quant/freqtrade/config_fast_btc.json'
CONFIG_PATH = 'D:\devlop\quant\\freqtrade\config_fast.json'

backtesting = ["backtesting", "--timerange", "20230505-20230507", "-c", CONFIG_PATH, "--strategy", "FastTradeStrategy"]
tryRun = ["trade", "-c", CONFIG_PATH,  "--strategy", "FastTradeStrategy"]
download = ["download-data", "-c", CONFIG_PATH, "--timerange", "20230101-", "-t", "5m"]


def testStoploss(current_profit, is_short=False, leverage=25):

    stoploss_value = -1
    
    if current_profit > 0.3 :
        stoploss_value = stoploss_from_open(0.2, current_profit, is_short=is_short, leverage=leverage)

    return stoploss_value

if __name__ == '__main__':


    main.main(tryRun)

    # testStoploss()

    # shor_array = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.9, 1.0, 1.1, 1.2, 1.3, 2.0, 2.5, 3.0]
    # for i in shor_array:
    #     print(testStoploss(i, is_short=True))

    # long_array = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.9, 1.0, 1.1, 1.2, 1.3, 2.0, 2.5, 3.0]
    # for i in long_array:
    #     print(testStoploss(i, is_short=False))


    