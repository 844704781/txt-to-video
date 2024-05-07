import configparser
import argparse
from entity.iconfig_parser import ConfigParser
from video_builder import VideoBuilder
from entity.video_const import VideoConst


def main():
    config = configparser.ConfigParser()
    config.read('./config.ini')

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-s', '--service', type=str, help='service["RUN_WAY_TXT","RUN_WAY_IMG","PIKA"]')
    parser.add_argument('-u', '--username', type=str, help='username')
    parser.add_argument('-p', '--password', type=str, help='password')
    parser.add_argument('-c', '--content', type=str, help='content:Prompt word/image local path')
    args = parser.parse_args()
    username = args.username
    password = args.password
    content = args.content
    service = args.service

    if service is None:
        service = VideoConst.PIKA_TXT
    if service == VideoConst.PIKA_TXT or service == VideoConst.PIKA_IMG:
        if username is None:
            username = config['PIKA']['username']
        if password is None:
            password = config['PIKA']['password']

    else:
        if username is None:
            username = config['RUNWAY']['username']
        if password is None:
            password = config['RUNWAY']['password']

    if content is None:
        content = config['CONTENT']['content']

    i_config = ConfigParser(username, password)
    processor = VideoBuilder.create().set_config(i_config).set_content(content) \
        .set_processor(service).build()
    download_link = processor.run()


if __name__ == "__main__":
    main()
