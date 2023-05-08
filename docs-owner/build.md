
## install

### docker

https://www.freqtrade.io/en/stable/docker_quickstart/

### installation
``` 
git clone https://github.com/freqtrade/freqtrade.git

cd freqtrade

git checkout stable

or

git checkout develop

```

then script installation

`./setup.sh -i`

then

activate your virtual environment

`source ./.env/bin/activate`

more: https://www.freqtrade.io/en/stable/installation/

历史数据下载

```
freqtrade download-data --timerange 20210101-  -t 1h
```

回测
```
freqtrade backtesting -c config005.json --timerange 20230301 --strategy Strategy005
```


```
docker compose up -d
```


启动交易

docker compose up -d 	

停止并移除镜像

docker compose down

打印日志

docker compose logs -f

本地环境运行

freqtrade trade -c configOwner.json --strategy VolatilitySystem

查看镜像

 docker images



