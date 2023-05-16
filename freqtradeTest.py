from freqtrade import main
import argparse

from freqtrade.strategy.strategy_helper import stoploss_from_open
# freqtrade backtesting --timerange 20230506- -c config_fast_btc.json --strategy FastTradeStrategy

CONFIG_PATH = '/Users/a123/work/quant/freqtrade/config_fast_btc.json'
CONFIG_PATH = 'D:\devlop\quant\\freqtrade\config_fast.json'

backtesting = ["backtesting", "--timerange", "20230505-20230507", "-c", CONFIG_PATH, "--strategy", "FastTradeStrategy"]
tryRun = ["trade", "-c", CONFIG_PATH,  "--strategy", "FastTradeStrategy"]
download = ["download-data", "-c", CONFIG_PATH, "--timerange", "20230101-", "-t", "5m"]

def custom_stoploss(open_relative, current_profit, leverage, is_short):
    return stoploss_from_open(open_relative, current_profit, is_short, leverage) 

def adjust_stoploss(current_price, stoploss, is_short, leverage):
    if is_short:
        return float(current_price * (1 + abs(stoploss / leverage)))
    else:
        return float(current_price * (1 - abs(stoploss / leverage)))

if __name__ == '__main__':

    #main.main(tryRun)
    # current_profit = 0.3
    leverage = 25
    # open_relative = 0.2
    is_short = False
    open = 100
    # current_price =  150

    array = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0 , 1.5, 25]
    for i in array:
        current_profit = i

        if current_profit > 0.3:
            open_relative = current_profit - 0.2
            current_price = open * (1 + current_profit)
            stop_loss = custom_stoploss(open_relative, current_profit, leverage, is_short) * leverage
            print('stop__loss = ', stop_loss)
            print('当前止损位 = ', adjust_stoploss(current_price, stop_loss, is_short, leverage))
        else:
            print(-1)
    print("=====================================git")    

    for i in array:
        current_profit = i
        if current_profit > 0.3:
            is_short = True
            open_relative = current_profit - 0.2
            current_price = open * (1 - current_profit)
            stop_loss = custom_stoploss(open_relative, current_profit, leverage, is_short) * leverage
            print('stop__loss = ', stop_loss)
            print('当前止损位 = ', adjust_stoploss(current_price, stop_loss, is_short, leverage))
        else:
            print(-1)
