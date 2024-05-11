# 大模型生成视频工具

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
username = v2v2
password = zsLe.nz!DU2zKdY

[PIKA]
#本地账号
username = v2.0@qq.com
password = Abc234!!
```

## 命令行操作(常用于测试)

1.设置测试提示词,配置测试账号
config.ini:
```text
[RUNWAY]
#本地账号
username = v2v2
password = zsLe.nz!DU2zKdY

[PIKA]
#本地账号
username = v2.0@qq.com
password = Abc234!!
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
