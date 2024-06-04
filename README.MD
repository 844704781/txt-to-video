# 大模型生成视频工具
## 概述
该项目为闲鱼买家项目，目的是为了给买家的AI平台接入国外的文生视频平台，设计隐私部分代码已移除。这本质上属于套壳项目，由于国外的文生视频平台大多还没开放自己的API，所以这里使用Playwright无头浏览器操作国外文生视频平台接口，2024年5月20日之后不再维护，现开源出来供大家学习交流。
> 根据提示词/图片生成对应的视频,基于runway,pika平台

## docker部署:

```shell
docker build -t runway .
docker run runway 
```

## 普通部署

1. 安装依赖

```shell
pip install -r requirements.txt
```

2. 安装playwright依赖

```shell
# Linux环境需要，其它环境情况运行提示
sudo playwright install-deps
```

3. 配置服务器url，访问密钥

```shell
config.ini中的如下配置
[DIAN_BAOBAO]
partner_id = xxx
private_key = xxx
base_url = https://xxx.com
```

4. 根据服务器配置调整并发数

```shell
config.ini中的如下配置
[SERVICE]
callback_max_thread_count = 1 # 回调接口线程池大小
video_processor_count = 8 # 视频生成线程池大小
```

5. 配置本地账号，如果服务器没下发，保证服务器不下发也能正常运行
config.ini:
```text
[RUNWAY]
#本地账号
username = xxx
password = xxx

[PIKA]
#本地账号
username = xxx
password = xxx
```
## 执行启动程序
```shell
python app.py
```

## 命令行操作(常用于测试)

1.设置测试提示词,配置测试账号
config.ini:
```text
[RUNWAY]
#本地账号
username = 
password = 

[PIKA]
#本地账号
username = 
password = 
```

2.执行
```shell
python main.py
# 也可以配置config.ini后通过参数执行
python main.py -t "A purple planet"
# 参数解释
optional arguments:
  -h, --help            show this help message and exit
  -s SERVICE, --service SERVICE
                        service["RUN_WAY_TXT","RUN_WAY_IMG","RUN_WAY_MIX","PIKA_TXT","PIKA_IMG","PIKA_MIX"]
  -u USERNAME, --username USERNAME
                        username
  -p PASSWORD, --password PASSWORD
                        password
  -c CONTENT, --content CONTENT
                        content:Prompt word or image local path
  -i IMAGE, --image IMAGE
                        content:Prompt word and image local path

```
