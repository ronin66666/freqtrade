from freqtrade import main
import argparse
# freqtrade backtesting --timerange 20230506- -c config_fast_btc.json --strategy FastTradeStrategy

CONFIG_PATH = '/Users/a123/work/quant/freqtrade/config_fast_btc.json'

backtesting = ["backtesting", "--timerange", "20230505-20230507", "-c", CONFIG_PATH, "--strategy", "FastTradeStrategy"]
tryRun = ["trade", "-c", CONFIG_PATH,  "--strategy", "FastTradeStrategy"]
download = ["download-data", "-c", CONFIG_PATH, "--timerange", "20230101-", "-t", "5m"]
if __name__ == '__main__':

    main.main(backtesting)