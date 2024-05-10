# -*- coding: utf-8 -*-
import sys
import time
from playwright.sync_api import sync_playwright
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from connector.runway_connector import RunwayConnector
from connector.pika_connector import PikaConnector
from db.taskdb import create_tables, is_table_created, TaskMapper, Source, sync_table_structure
from entity.task_status import Status
from entity.video_const import transfer
from entity.result_utils import ResultDo
from entity.error_code import ErrorCode
import configparser
import threading
from entity.iconfig_parser import ConfigParser
from video_builder import VideoBuilder
import concurrent.futures
from logger_config import logger

from common.custom_exception import CustomException
from entity.task_make_type import MakeType
import os
import requests
import random
import string
import argparse
import subprocess

runwayConnector = RunwayConnector()
pikaConnector = PikaConnector()
taskMapper = TaskMapper()

# scheduler_logger = logger.getLogger("apscheduler.executors.default")

# scheduler_logger.setLevel(logger.CRITICAL)

config = configparser.ConfigParser()
config.read('./config.ini')

callback_thread_count = 1
video_processor_thread_count = 1

if config['SERVICE'] is not None:
    if (config['SERVICE']['callback_max_thread_count'] is not None
            or len(config['SERVICE']['callback_max_thread_count'] is not None) != 0):
        callback_thread_count = int(config['SERVICE']['callback_max_thread_count']
                                    or len(config['SERVICE']['callback_max_thread_count']) != 0)
    if config['SERVICE']['video_processor_count'] is not None:
        video_processor_thread_count = int(config['SERVICE']['video_processor_count'])

callbackThreadPool = concurrent.futures.ThreadPoolExecutor(max_workers=callback_thread_count)
videoThreadPool = concurrent.futures.ThreadPoolExecutor(max_workers=video_processor_thread_count)

project_root = os.path.dirname(os.path.abspath(__file__))


# 获取请求连接
def get_connector(source):
    if source == Source.PIKA:
        connector = pikaConnector
    elif source == Source.RUN_WAY:
        connector = runwayConnector
    else:
        raise CustomException(ErrorCode.UNSUPPORTED, f'Unsupported source:{source}')
    return connector


# 进度回调
def progress_callback(_task, _percent):
    def callback_func(task, percent):
        percent = int(percent)
        task.progress = percent
        task.status = Status.DOING.value
        #  查找原数据,如果一样则不回调
        #  异步发送
        task = taskMapper.get(task.task_id)
        if task.progress == percent:
            return

        taskMapper.set_progress(percent, task.task_id)
        _callback(get_connector(task.source), task)

    callbackThreadPool.submit(callback_func, _task, _percent)


# 跑任务
def run_task(task):
    logger.debug(f"【{task.source}】Execute task start")
    if task.source == Source.PIKA:
        username = config['PIKA']['username']
        password = config['PIKA']['password']
    elif task.source == Source.RUN_WAY:
        username = config['RUNWAY']['username']
        password = config['RUNWAY']['password']
    else:
        raise CustomException(ErrorCode.UNSUPPORTED, f'Unsupported source {task.source}')

    i_config = ConfigParser(username, password)
    service = transfer(task.source, task.make_type)

    processor = VideoBuilder.create() \
        .set_config(i_config) \
        .set_form(task.prompt, task.image_path) \
        .set_processor(service) \
        .set_task_id(task.task_id) \
        .progress_callback(lambda percent: progress_callback(task, percent)) \
        .build()

    try:
        video_url = processor.run()
    except CustomException as e:
        logger.error(f"【{task.source}】Execute task end,error:{e.message}")
        return ResultDo(e.code, e.message)
    except Exception as e:
        logger.exception(f"【{task.source}】Execute task end,error:", e)
        return ResultDo(ErrorCode.TIME_OUT, 'Video generation timed out.')
    logger.debug(f"【{task.source}】Execute task end")
    return ResultDo(code=ErrorCode.OK, data=video_url)


def checking():
    logger.debug("checking...")
    tasks = taskMapper.get_doing_tasks()
    for task in tasks:
        # 下次重试
        taskMapper.set_status(task.task_id, Status.FAIL)


# 下载图片
def download_image(url):
    # TODO test...
    def generate_random_filename(length):
        """生成指定长度的随机文件名"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    images_dir = os.path.join(project_root, 'images')
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)

    # 发送 GET 请求获取图片
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # 从 URL 中获取图片格式
            content_type = response.headers.get('content-type')
            image_extension = content_type.split('/')[-1]

            # 生成随机文件名
            random_filename = generate_random_filename(64)
            filename = os.path.join(images_dir, f"{random_filename}.{image_extension}")

            # 保存图片到本地
            with open(filename, 'wb') as f:
                f.write(response.content)
            logger.debug(f"Image downloaded successfully: {filename}")
            return filename
        else:
            logger.error(f"Failed to download image from {url}: HTTP status code {response.status_code}")
    except Exception as e:
        logger.exception(f"Failed to download image from {url}", e)
        raise CustomException(ErrorCode.TIME_OUT, str(e))


# 执行任务
def execute_task():
    def execute_task_func(task):

        try:
            # 处理图片,如果图片未下载，则将其下载直本地
            if task.image_path is None or len(task.image_path) == 0 \
                    or not os.path.exists(task.image_path):

                if task.make_type in [MakeType.IMAGE, MakeType.MIX]:
                    image_path = download_image(task.make_type, task.image_url)
                    task.image_path = image_path
                    taskMapper.update_image_path(image_path, task.task_id)
        except CustomException as e:
            taskMapper.set_fail(task.task_id, e.code, e.message)
            return
        except Exception as e:
            logger.exception(e)
            taskMapper.set_fail(task.task_id, ErrorCode.UNKNOWN, str(e))
            return

        try:
            # 将任务设置成执行中
            task.status = Status.DOING.value
            taskMapper.set_status(task.task_id, task.status)
            _callback(get_connector(task.source), task)

            execute_result = run_task(task)

            if execute_result.code == 0:
                # 成功
                task.status = Status.SUCCESS.value
                task.video_url = execute_result.data
                taskMapper.set_success(task.task_id, video_url=execute_result.data)
                _callback(get_connector(task.source), task)

            else:
                # 失败
                task.status = Status.FAIL.value
                task.message = execute_result.message
                task.err_code = execute_result.code
                taskMapper.set_fail(task.task_id, execute_result.code, execute_result.message)
                _callback(get_connector(task.source), task)
        except CustomException as e:
            raise e
        except Exception as e:
            logger.exception(e)
            raise e

    tasks = taskMapper.get_executable_tasks(10)
    if len(tasks) == 0:
        logger.info('All tasks have been completed!!!')
    for _task in tasks:
        videoThreadPool.submit(execute_task_func, _task)
        time.sleep(5)


def fetch(connector, source):
    logger.debug(f"【{source}】Get task")
    tasks = connector.fetch(1)
    for task in tasks:
        task['source'] = source
    taskMapper.bulk_insert_tasks(tasks)
    logger.debug(f"【{source}】Save task success")
    # 执行爬取操作
    # 将爬取结果上传至对应接口


def fetch_runway():
    fetch(runwayConnector, Source.RUN_WAY)


def fetch_pika():
    fetch(pikaConnector, Source.PIKA)


def _callback(connector, task):
    logger.debug(f"【{task.source}】Callback task")
    payload = {
        "task_id": task.task_id,
        "progress": task.progress,
        "status": task.status,
        "errcode": task.err_code,
        "errmsg": task.message,
        "video_url": task.video_url
    }
    try:
        connector.callback(payload)
    except CustomException as e:
        logger.warning(f"【{task.source}】Callback task Warning:{e.message}")
        taskMapper.update_server_message(e.message, task.task_id)
        return
    except Exception as e:
        logger.exception(f"【{task.source}】Callback task Fail", e)
        taskMapper.update_server_message(str(e), task.task_id)
        return
    taskMapper.set_synced_by_task_id(task.task_id)
    logger.debug(f"【{task.source}】Callback task Success")


def callback(connector, source):
    count = taskMapper.unsync_count(source)
    while count > 0:
        logger.debug(f"【{source}】UnSync task count :{count}")
        task = taskMapper.find_unsync_task_by_source(source)
        if task is None:
            return
        _callback(connector, task)
        time.sleep(2)


def callback_runway():
    callback(runwayConnector, Source.RUN_WAY)


def callback_pika():
    callback(pikaConnector, Source.PIKA)


def check_chromium_installed():
    with sync_playwright() as p:
        # 获取 Chromium 的可执行文件路径
        chromium_path = p.chromium.executable_path

        if os.path.exists(chromium_path):
            return True
        else:
            return False


def install_chromium():
    subprocess.run(["playwright", "install", "chromium"])


def main():
    logger.info("初始化中...")
    # 在项目第一次启动时创建表
    if not is_table_created():
        create_tables()
    if not check_chromium_installed():
        logger.info("初次使用,环境准备中")
        install_chromium()
        logger.info("准备完成")

    sync_table_structure()
    checking()
    logger.info("初始化成功")

    # 创建后台调度器
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_runway, 'interval', seconds=10 * 60, next_run_time=datetime.now())
    scheduler.add_job(fetch_pika, 'interval', seconds=10 * 60, next_run_time=datetime.now())

    scheduler.add_job(callback_runway, 'interval', seconds=10)
    scheduler.add_job(execute_task, 'interval', seconds=60, next_run_time=datetime.now())
    scheduler.start()

    event = threading.Event()

    event.wait()


if __name__ == "__main__":
    main()
