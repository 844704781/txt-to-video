
# 大模型生成视频工具
> 根据提示词/图片生成对应的视频,基于runway,pika平台

## 安装方法
1. 安装Python依赖
```shell
pip install -r requirements.txt
```
2. 安装playwright依赖(可选)
```shell
# Linux环境可能需要
sudo playwright install-deps
```
3. 更换提示词,配置账号
```text
【可选】更换config.ini中的tips内容即可，如果不配置，需要在参数中配置
【可选】账号密码 config.ini自行配置，如果不配置，需要在参数中配置
```
4.执行
```shell
python main.py
# 也可以配置config.ini后通过参数执行
python main.py -t "A purple planet"
# 参数解释
-u 账号
-p 密码
-t 提示词
```
