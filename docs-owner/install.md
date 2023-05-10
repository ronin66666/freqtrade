

## docker

https://www.freqtrade.io/en/stable/docker_quickstart/

```shell
mkdir ft_userdata
cd ft_userdata/
curl https://raw.githubusercontent.com/freqtrade/freqtrade/stable/docker-compose.yml -o docker-compose.yml
docker compose pull
```

创建user_data目录
`docker compose run --rm freqtrade create-userdir --userdir user_data` 

创建config.json 模板
`docker compose run --rm freqtrade new-config --config user_data/config.json`
or
创建一个空的config.json
`touch user_data/config.json` 

配置`docker-compose.yml`

```shell
container_name: freqtrade   # 重命名容器名称
ports:
      - "127.0.0.1:8282:8282"
    # Default command used when running `docker compose up`
    command: >
      trade
      --logfile /freqtrade/user_data/logs/freqtrade.log # 日志文件路径，默认就好
      --db-url sqlite:////freqtrade/user_data/tradesv3.sqlite # 数据库路径，默认就好
      --config /freqtrade/user_data/config.json # 配置文件路径
      --strategy FastTradeStrategy  # 策略名称

```

启动容器
`docker compose up -d`

停止运行
`docker compose down`

查看日志
`docker compose logs -f`

下载历史数据
`docker compose run --rm freqtrade download-data --timerange 20210101-  -t 1h`

回测
`docker compose run --rm freqtrade backtesting -c config.json --timerange 20230301 --strategy FastTradeStrategy`

查看镜像
`docker images`

查看正在运行的容器
`docker ps`

删除镜像
`docker rmi -f freqtrade`

## 代码 安装

``` 
git clone https://github.com/freqtrade/freqtrade.git

cd freqtrade

git checkout stable

or

git checkout develop

```

### mac
脚本安装相关依赖

`./setup.sh -i`


激活环境
`source ./.env/bin/activate`

### windows 

```
cd \path\freqtrade
python -m venv .env
.env\Scripts\activate.ps1
# optionally install ta-lib from wheel
# Eventually adjust the below filename to match the downloaded wheel
pip install --find-links build_helpers\ TA-Lib -U
pip install -r requirements.txt
pip install -e .
freqtrade

```

## 其他操作
more: https://www.freqtrade.io/en/stable/installation/

历史数据下载

```
freqtrade download-data --timerange 20210101-  -t 1h
```

回测
```
freqtrade backtesting -c config005.json --timerange 20230301 --strategy Strategy005
```


币安申请子账号
https://www.binance.com/zh-CN/survey/e222293e45de4540b9c452ecf61e1bdd?ns=subacct-appform