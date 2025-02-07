#!/usr/bin/env python3
"""
Main Freqtrade bot script.
Read the documentation to know what cli arguments you need.
"""
import logging
import sys
from typing import Any, List, Optional

from freqtrade.util.gc_setup import gc_set_threshold


# check min. python version
if sys.version_info < (3, 8):  # pragma: no cover
    sys.exit("Freqtrade requires Python version >= 3.8")

from freqtrade import __version__
from freqtrade.commands import Arguments
from freqtrade.exceptions import FreqtradeException, OperationalException
from freqtrade.loggers import setup_logging_pre


logger = logging.getLogger('freqtrade')


def main(sysargv: Optional[List[str]] = None) -> None:
    """
    This function will initiate the bot and start the trading loop.
    :return: None
    """

    return_code: Any = 1
    try:
        setup_logging_pre()
        arguments = Arguments(sysargv)  # 进入命令行解析
        args = arguments.get_parsed_arg()  # 获取解析后的参数， 会解析相关命令

        # Call subcommand.
        if 'func' in args:
            logger.info(f'freqtrade {__version__}')
            gc_set_threshold() # 设置gc阈值
            return_code = args['func'](args) # 执行方法，交易相关的方法在freqtrade/commands/trade_commands.py中
        else:
            # No subcommand was issued.
            raise OperationalException(
                "Usage of Freqtrade requires a subcommand to be specified.\n"
                "To have the bot executing trades in live/dry-run modes, "
                "depending on the value of the `dry_run` setting in the config, run Freqtrade "
                "as `freqtrade trade [options...]`.\n"
                "To see the full list of options available, please use "
                "`freqtrade --help` or `freqtrade <command> --help`."
            )

    except SystemExit as e:  # pragma: no cover
        return_code = e
    except KeyboardInterrupt:
        logger.info('SIGINT received, aborting ...')
        return_code = 0
    except FreqtradeException as e:
        logger.error(str(e))
        return_code = 2
    except Exception:
        logger.exception('Fatal exception!')
    finally:
        sys.exit(return_code)


if __name__ == '__main__':  # pragma: no cover
    main()
