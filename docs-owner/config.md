# Configure the bot

## The Freqtrade configuration file

默认交易机器人会加载当前工作目录中的`config.json`文件，可以使用`-c`或`--config`命令指定不同配置文件。

创建新的基础配置文件命令：`freqtrade new-config --config config.json`

### Environment variables

可以通过设置环境变量来覆盖配置文件中的选项，比如yourExchangeKey、yourExchangeSecret等，环境变量的规则为

`FREQTRADE__{section}__{key}`的方式

例如：

```bash
FREQTRADE__TELEGRAM__CHAT_ID=<telegramchatid>					
FREQTRADE__TELEGRAM__TOKEN=<telegramToken>
FREQTRADE__EXCHANGE__KEY=<yourExchangeKey>
FREQTRADE__EXCHANGE__SECRET=<yourExchangeSecret>
```

### Multiple configuration files

#### 指定多个配置文件

可以使用多个配置文件来管理和组织您的交易机器人设置。这样，您可以将不同的配置参数分散到多个文件中，使得管理和修改配置更加灵活和方便。

要使用多个配置文件，您只需在启动 Freqtrade 时通过命令行参数传递多个配置文件路径。例如：

```bash
freqtrade trade -c config1.json -c config2.json -c config3.json
```

在这个例子中，我们传递了三个配置文件：`config1.json`、`config2.json` 和 `config3.json`。Freqtrade 会按照指定的顺序加载这些配置文件，并将它们合并为一个完整的配置。如果某个设置在多个文件中都有定义，那么后面指定的文件中的设置会覆盖先前的设置。

此外，您还可以将配置参数从标准输入流（stdin）传递给 Freqtrade。这对于需要在运行时动态生成配置的场景非常有用（在运行时动态生成配置的场景通常是指在启动交易机器人之前动态生成或修改配置，而不是在交易机器人已经运行时进行更改）。要使用此功能，您需要使用特殊的文件名 `-`（短横线）作为配置文件参数：

```bash
echo '{"stake_amount": 100, "stake_currency": "USDT"}' | freqtrade trade -c -
```

在这个例子中，我们通过 `echo` 命令将一个包含 `stake_amount` 和 `stake_currency` 设置的 JSON 字符串传递给 Freqtrade。Freqtrade 会从标准输入流读取这些配置参数并使用它们。

您还可以将多个配置文件与从 stdin 读取的配置一起使用。例如：

```bash
echo '{"stake_amount": 100, "stake_currency": "USDT"}' | freqtrade trade -c config1.json -c config2.json -c -
```

在这个例子中，我们同时使用了两个配置文件（`config1.json` 和 `config2.json`）以及从 stdin 传递的配置参数。注意，从 stdin 读取的配置参数具有最高优先级，它们会覆盖其他配置文件中的相应设置。

#### 通过add_config_files添加多个配置文件

在 Freqtrade 中，您可以使用 `add_config_files` 参数来指定和使用多个配置文件。通过这种方式指定的配置文件会与初始配置文件一起加载并合并。这些文件会相对于初始配置文件进行解析。

要使用 `add_config_files` 参数，您需要在初始配置文件中添加一个名为 `add_config_files` 的键，并将其值设置为一个包含其他配置文件路径的数组。例如，假设您有以下三个配置文件：`config1.json`（初始配置文件）、`config2.json` 和 `config3.json`。要将 `config2.json` 和 `config3.json` 添加到 `config1.json` 中，请在 `config1.json` 中添加如下配置：

```json
{
  "add_config_files": ["config2.json", "config3.json"],
  ...
}

```

现在，当您使用 `config1.json` 启动 Freqtrade 时，`config2.json` 和 `config3.json` 也会被自动加载并与 `config1.json` 合并：

```bash
freqtrade trade -c config1.json
```

请注意，这种方法仅适用于在 Freqtrade 运行时不需要更改的配置。如果您需要在运行时动态更改配置，请使用多个 `--config` 参数或从标准输入流（stdin）读取配置。

### 更改配置

在Freqtrade运行时更改配置通常是不支持的。要应用新的配置更改，您需要采取以下步骤：

1. 停止当前运行的交易机器人。确保您正在使用的命令行界面（CLI）或界面提供了停止命令。使用Docker部署Freqtrade时，您可以使用以下命令停止容器：

```bash
Copy code
docker-compose down
```

1. 修改配置文件。您可以直接编辑配置文件（如 `config.json`），根据需要更改相应的设置。保存更改后，关闭文件。
2. 重新启动交易机器人，应用新的配置。使用Docker时，可以使用以下命令重新启动交易机器人：

```bash
Copy code
docker-compose up -d
```

这将使交易机器人在新的配置下重新启动，新的设置将生效。

请注意，更改配置可能会影响当前运行的交易和策略。在修改配置之前，请务必了解每个设置的影响，并确保已备份当前配置文件以防止丢失重要设置。在修改配置时，建议您首先在回测或干运行模式下测试新设置，以确保新的配置按预期工作。

## Configuration parameters

官方比较全的配置示例

```json
{
    "max_open_trades": 3,										
    "stake_currency": "BTC",
    "stake_amount": 0.05,
    "tradable_balance_ratio": 0.99,
    "fiat_display_currency": "USD",
    "amount_reserve_percent": 0.05,
    "available_capital": 1000,
    "amend_last_stake_amount": false,
    "last_stake_amount_min_ratio": 0.5,
    "dry_run": true,
    "dry_run_wallet": 1000,
    "cancel_open_orders_on_exit": false,
    "timeframe": "5m",
    "trailing_stop": false,
    "trailing_stop_positive": 0.005,
    "trailing_stop_positive_offset": 0.0051,
    "trailing_only_offset_is_reached": false,
    "use_exit_signal": true,
    "exit_profit_only": false,
    "exit_profit_offset": 0.0,
    "ignore_roi_if_entry_signal": false,
    "ignore_buying_expired_candle_after": 300,
    "trading_mode": "spot",
    "margin_mode": "",
    "minimal_roi": {
        "40":  0.0,
        "30":  0.01,
        "20":  0.02,
        "0":  0.04
    },
    "stoploss": -0.10,
    "unfilledtimeout": {
        "entry": 10,
        "exit": 10,
        "exit_timeout_count": 0,
        "unit": "minutes"
    },
    "entry_pricing": {
        "price_side": "same",
        "use_order_book": true,
        "order_book_top": 1,
        "price_last_balance": 0.0,
        "check_depth_of_market": {
            "enabled": false,
            "bids_to_ask_delta": 1
        }
    },
    "exit_pricing":{
        "price_side": "same",
        "use_order_book": true,
        "order_book_top": 1,
        "price_last_balance": 0.0
    },
    "order_types": {
        "entry": "limit",
        "exit": "limit",
        "emergency_exit": "market",
        "force_exit": "market",
        "force_entry": "market",
        "stoploss": "market",
        "stoploss_on_exchange": false,
        "stoploss_price_type": "last",
        "stoploss_on_exchange_interval": 60,
        "stoploss_on_exchange_limit_ratio": 0.99
    },
    "order_time_in_force": {
        "entry": "GTC",
        "exit": "GTC"
    },
    "pairlists": [
        {"method": "StaticPairList"},
        {
            "method": "VolumePairList",
            "number_assets": 20,
            "sort_key": "quoteVolume",
            "refresh_period": 1800
        },
        {"method": "AgeFilter", "min_days_listed": 10},
        {"method": "PrecisionFilter"},
        {"method": "PriceFilter", "low_price_ratio": 0.01, "min_price": 0.00000010},
        {"method": "SpreadFilter", "max_spread_ratio": 0.005},
        {
            "method": "RangeStabilityFilter",
            "lookback_days": 10,
            "min_rate_of_change": 0.01,
            "refresh_period": 1440
        }
    ],
    "exchange": {
        "name": "binance",
        "sandbox": false,
        "key": "your_exchange_key",
        "secret": "your_exchange_secret",
        "password": "",
        "log_responses": false,
        // "unknown_fee_rate": 1,
        "ccxt_config": {},
        "ccxt_async_config": {},
        "pair_whitelist": [
            "ALGO/BTC",
            "ATOM/BTC",
            "BAT/BTC",
            "BCH/BTC",
            "BRD/BTC",
            "EOS/BTC",
            "ETH/BTC",
            "IOTA/BTC",
            "LINK/BTC",
            "LTC/BTC",
            "NEO/BTC",
            "NXS/BTC",
            "XMR/BTC",
            "XRP/BTC",
            "XTZ/BTC"
        ],
        "pair_blacklist": [
            "DOGE/BTC"
        ],
        "outdated_offset": 5,
        "markets_refresh_interval": 60
    },
    "edge": {
        "enabled": false,
        "process_throttle_secs": 3600,
        "calculate_since_number_of_days": 7,
        "allowed_risk": 0.01,
        "stoploss_range_min": -0.01,
        "stoploss_range_max": -0.1,
        "stoploss_range_step": -0.01,
        "minimum_winrate": 0.60,
        "minimum_expectancy": 0.20,
        "min_trade_number": 10,
        "max_trade_duration_minute": 1440,
        "remove_pumps": false
    },
    "telegram": {
        "enabled": false,
        "token": "your_telegram_token",
        "chat_id": "your_telegram_chat_id",
        "notification_settings": {
            "status": "on",
            "warning": "on",
            "startup": "on",
            "entry": "on",
            "entry_fill": "on",
            "exit": {
                "roi": "off",
                "emergency_exit": "off",
                "force_exit": "off",
                "exit_signal": "off",
                "trailing_stop_loss": "off",
                "stop_loss": "off",
                "stoploss_on_exchange": "off",
                "custom_exit": "off"
            },
            "exit_fill": "on",
            "entry_cancel": "on",
            "exit_cancel": "on",
            "protection_trigger": "off",
            "protection_trigger_global": "on",
            "show_candle": "off"
        },
        "reload": true,
        "balance_dust_level": 0.01
    },
    "api_server": {
        "enabled": false,
        "listen_ip_address": "127.0.0.1",
        "listen_port": 8080,
        "verbosity": "error",
        "enable_openapi": false,
        "jwt_secret_key": "somethingrandom",
        "CORS_origins": [],
        "username": "freqtrader",
        "password": "SuperSecurePassword",
        "ws_token": "secret_ws_t0ken."
    },
    "external_message_consumer": {
        "enabled": false,
        "producers": [
          {
            "name": "default",
            "host": "127.0.0.2",
            "port": 8080,
            "ws_token": "secret_ws_t0ken."
          }
        ],
        "wait_timeout": 300,
        "ping_timeout": 10,
        "sleep_time": 10,
        "remove_entry_exit_signals": false,
        "message_size_limit": 8
    },
    "bot_name": "freqtrade",
    "db_url": "sqlite:///tradesv3.sqlite",
    "initial_state": "running",
    "force_entry_enable": false,
    "internals": {
        "process_throttle_secs": 5,
        "heartbeat_interval": 60
    },
    "disable_dataframe_checks": false,
    "strategy": "SampleStrategy",
    "strategy_path": "user_data/strategies/",
    "recursive_strategy_search": false,
    "add_config_files": [],
    "reduce_df_footprint": false,
    "dataformat_ohlcv": "json",
    "dataformat_trades": "jsongz"
}

```

- max_open_trades: **required**

  允许您的机器人进行的未平仓交易数量，-1：表示不限制

- stake_currency：**required** 用于交易的加密货币，通常为usdt

- stake_amount：**required** 每次用于交易的金额，如果设置为unlimited表示交易机器可以使用所有的可用余额进行交易

- tradable_balance_ratio：指定了机器人可以用于交易的账户总余额的比例。这个参数的值应该是一个介于0.1和1.0之间的正浮点数。默认值为0.99，即99%。这意味着，如果您的账户总余额为1000美元，那么机器人将使用990美元（即99%）进行交易，其余的10美元（1%）将作为保留资金。

- available_capital：它指定了机器人可用的初始资本。这个参数对于在同一个交易所账户上运行多个机器人很有用，因为它可以确保每个机器人有一个单独的资本份额来管理和交易。参数的值应该是一个正浮点数。例如，如果您的账户总余额为2000美元，`available_capital` 设置为1000美元，`tradable_balance_ratio` 设置为0.75，那么机器人将使用750美元（75%）进行交易。

- fiat_display_currency：用于显示您的利润的法定货币。

- amend_last_stake_amount：default = false, 是 Freqtrade 配置中一个实验性的选项，当设置为 `true` 时，如果交易所或钱包余额不足以满足机器人的下一笔交易，它将尝试减少最后一次交易的头寸大小。换句话说，它会在最后一次交易时使用尽可能多的可用资金。

- last_stake_amount_min_ratio：Default = 0.5，用于在 `amend_last_stake_amount` 设置为 `true` 时定义剩余可用资金的最小头寸大小。这个选项的主要目的是确保当 `amend_last_stake_amount` 尝试减少最后一个头寸大小以适应剩余资金时，交易的头寸大小不会低于此比率。

  例如，如果 `last_stake_amount_min_ratio` 设置为 `0.5`，那么在最后一个头寸中，交易的头寸大小将不会低于总头寸的50%。这可以帮助避免交易太小的头寸，从而使得交易费用占比过高，影响策略的整体表现。

- amount_reserve_percent：default = 0.05(5%)

  它用于在计算每对交易的最小头寸大小时预留一定的资金。当设置这个选项时，机器人会在计算最小头寸大小时预留 `amount_reserve_percent` +止损值，以避免可能的交易拒绝。

  默认值为 0.05（5%）。这意味着，当计算每对交易的最小头寸大小时，机器人会预留额外的 5% 资金 +止损值。这有助于确保在止损触发时，您的账户中仍有足够的资金来执行交易。

  在使用此选项时，您应根据自己的风险容忍度和交易策略来调整 `amount_reserve_percent` 的值。请注意，过高的预留资金可能会限制您的交易机会，而过低的预留资金可能会导致止损订单被拒绝执行。因此，务必谨慎设置此值以达到您的策略目标。

- timeframe：设置周期，一般不在配置文件中设置，在策略中设置

- dry_run：**required**  default = true , 定义机器人运行是测试环境中还是正式环境中

- dry_run_wallet：试跑模式下的钱包余额，默认1000

- cancel_open_orders_on_exit：Defaults to `false`.
