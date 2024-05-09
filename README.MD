# 大模型生成视频工具

> 根据提示词/图片生成对应的视频,基于runway,pika平台

## 普通部署

1. 安装Python依赖

```shell
pip install -r requirements.txt
```

2. 安装playwright依赖(可选)

```shell
# Linux环境可能需要
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
video_processor_count = 10 # 视频生成线程池大小
```

## 容器化部署

## 测试服务

1.设置测试提示词,配置测试账号

```text
【可选】更换config.ini中的tips内容即可，如果不配置，需要在参数中配置
【可选】账号密码 config.ini自行配置，如果不配置，需要在参数中配置
```

2.执行

```shell
python main.py
# 也可以配置config.ini后通过参数执行
python main.py -t "A purple planet"
# 参数解释
-u 账号
-p 密码
-t 提示词
```
