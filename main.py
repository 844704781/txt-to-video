import configparser
import argparse
from entity.iconfig_parser import ConfigParser
from video_builder import VideoBuilder
from entity.video_const import VideoConst


# 主函数
def main():
    config = configparser.ConfigParser()
    config.read('./config.ini')

    parser = argparse.ArgumentParser(description='命令行参数示例')
    # 添加参数选项
    parser.add_argument('-u', '--username', type=str, help='用户名')
    parser.add_argument('-p', '--password', type=str, help='密码')
    parser.add_argument('-t', '--tips', type=str, help='提示词')
    # 解析命令行参数
    args = parser.parse_args()
    username = args.username
    password = args.password
    tips = args.tips
    if username is None:
        username = config['Settings']['username']
    if password is None:
        password = config['Settings']['password']

    if tips is None:
        tips = config['Settings']['tips']

    i_config = ConfigParser(username, password)
    processor = VideoBuilder.create().set_config(i_config).set_tips(tips) \
        .set_processor(VideoConst.RUN_WAY).build()
    download_link = processor.run()

    print("视频链接:", download_link)


if __name__ == "__main__":
    main()
