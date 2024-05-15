# -*- coding: utf-8 -*-
import hashlib
import sys
import time
from playwright.sync_api import sync_playwright
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from connector.runway_connector import RunwayConnector
from connector.pika_connector import PikaConnector
from db.taskdb import create_tables as create_task_tables, is_table_created as is_task_table_created, TaskMapper, \
    Source as TaskSource, sync_table_structure as sync_task_table_structure

from db.accountdb import create_tables as create_account_tables, is_table_created as is_account_table_created, \
    Source as AccountSource, AccountMapper, sync_table_structure as sync_account_table_structure
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
from entity.account_status import AccountStatus
import os
import requests
import random
import string
import argparse
import subprocess
import uuid

runwayConnector = RunwayConnector()
pikaConnector = PikaConnector()
taskMapper = TaskMapper()
accountMapper = AccountMapper()
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


def get_worker_id():
    # mac_address = uuid.getnode()
    # return ':'.join(['{:02x}'.format((mac_address >> elements) & 0xff) for elements in range(0, 2 * 6, 2)][::-1])
    return 'worker01'


# 获取请求连接
def get_connector(source):
    if source == TaskSource.PIKA:
        connector = pikaConnector
    elif source == TaskSource.RUN_WAY:
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


def balance_callback(_source, _account, _count: int = None, _message: str = None):
    def callback_func(source, account_no, count: int = None, message: str = None):
        account = accountMapper.get_by_account_no(source, account_no)
        if account is None:
            return

        elif count is not None and count >= 10:
            account_status = AccountStatus.NORMAL.value
            reason = "余额充足"
        elif count is not None and count >= 0:
            account_status = AccountStatus.DISABLED.value
            reason = "余额不足(余额小于10)"
        else:
            account_status = AccountStatus.EXCEPTION.value
            reason = message

        accountMapper.set_balance(account.id, account_status, reason, count)
        payload = {
            "account_no": account.account_no,
            "status": account_status,
            "balance": count,
            "reason": reason
        }
        logger.info("更新账号信息到服务器", payload)
        if source == AccountSource.PIKA:
            pikaConnector.callback_account(payload)

        elif source == AccountSource.RUN_WAY:
            runwayConnector.callback_account(payload)

        if count is not None and count < 10:
            fetch_account(source)
        pass

    # callback_func(_source, _account, _count, _message)
    callbackThreadPool.submit(callback_func, _source, _account, _count, _message)


def check_task_callback(task_id):
    task = taskMapper.get(task_id)
    if task is None:
        return False
    if task.status == Status.SUCCESS.value:
        return False
    return True


def check_task(task):
    if task.make_type == MakeType.TEXT:
        if task.prompt is None or len(task.prompt.strip()) == 0:
            return False
    elif task.make_type == MakeType.IMAGE:
        if task.image_path is None or len(task.image_path.strip()) == 0:
            return False
    else:
        if (task.image_path is None or len(task.image_path.strip()) == 0) and (task.prompt is None or len(
                task.prompt.strip()) == 0):
            return False
    return True


# 跑任务
def run_task(task, account: object = None):
    logger.debug(f"【{task.source}】Execute task start")

    if account is not None:
        logger.debug(f"使用数据库随机账号:{account.account_no}，账号配置中...")
        i_config = ConfigParser(account.account_no, account.password)
    else:
        if task.source == TaskSource.PIKA:
            username = config['PIKA']['username']
            password = config['PIKA']['password']
        elif task.source == TaskSource.RUN_WAY:
            username = config['RUNWAY']['username']
            password = config['RUNWAY']['password']
        else:
            raise CustomException(ErrorCode.UNSUPPORTED, f'Unsupported source {task.source}')
        logger.debug(f"数据库中无账号，使用测试账号:{username}，配置中...")
        i_config = ConfigParser(username, password)
    service = transfer(task.source, task.make_type)

    processor = VideoBuilder.create() \
        .set_config(i_config) \
        .set_form(task.prompt, task.image_path) \
        .set_processor(service) \
        .set_task_id(task.task_id) \
        .progress_callback(lambda percent:
                           progress_callback(task, percent)) \
        .set_balance_callback(
        lambda _account, _count, _message: balance_callback(task.source, _account, _count, _message)
    ).set_check_task_callback(check_task_callback).build()

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
    def generate_hash_filename(content):
        """根据文件内容的哈希值生成文件名"""
        hash_value = hashlib.sha256(content).hexdigest()
        return hash_value.lower()

    images_dir = os.path.join(project_root, 'images')
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
    images_dir = os.path.relpath(images_dir, project_root)
    # 发送 GET 请求获取图片
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # 从 URL 中获取图片格式
            content_type = response.headers.get('content-type')
            image_extension = content_type.split('/')[-1]

            # 根据文件内容的哈希值生成文件名
            hash_filename = generate_hash_filename(response.content)
            filename = os.path.join(images_dir, f"{hash_filename}.{image_extension}")

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


# 获取账号
def fetch_account(source):
    logger.debug(f"{source},随机获取账号中...")
    account = accountMapper.get_random_normal_account(source)
    if account is not None:
        logger.debug(f"{source},账号获取成功，当前账号:{account.account_no},余额:{account.balance}")
        return account
    else:
        logger.debug(f"{source},本地已无可用账号，云端获取账号中...")
        worker_id = get_worker_id()
        accounts = None
        if source == TaskSource.RUN_WAY:
            accounts = runwayConnector.fetch_accounts(worker_id)
        elif source == TaskSource.PIKA:
            accounts = pikaConnector.fetch_accounts(worker_id)
        else:
            pass
        logger.debug(f"{source},云端取到账号数量:{len(accounts)},本地保存中...")
        for account in accounts:
            account['source'] = source
            account['balance'] = 0
            account['reason'] = ''
        accountMapper.bulk_insert_tasks(accounts)
        logger.debug(f"{source},随机获取账号中...")
        account = accountMapper.get_random_normal_account(source)
        if account is not None:
            logger.debug(f"{source},账号获取成功，当前账号:{account.account_no},余额:{account.balance}")
        return account


def is_threadpool_idle(threadpool):
    thread_count = threadpool._max_workers
    # 获取线程池中的所有线程
    all_threads = videoThreadPool._threads
    # 获取正在使用的线程数
    active_threads = sum(1 for thread in all_threads if thread.is_alive())
    message = f"总线程数:{thread_count},活跃线程数:{active_threads}"
    if active_threads >= thread_count:
        message = message + ',线程池忙碌中...'
    else:
        message = message + ',有可用线程...'
    logger.debug(message)
    return active_threads < thread_count


def execute_task():
    def execute_task_func(task, _account):
        try:
            # 处理图片,如果图片未下载，则将其下载直本地
            if task.image_path is None or len(task.image_path) == 0 \
                    or not os.path.exists(task.image_path):

                if task.make_type in [MakeType.IMAGE, MakeType.MIX]:
                    image_path = download_image(task.image_url)
                    task.image_path = image_path
                    taskMapper.update_image_path(image_path, task.task_id)
        except CustomException as e:
            taskMapper.set_fail(task.task_id, e.code, e.message)
            return
        except Exception as e:
            logger.exception(e)
            taskMapper.set_fail(task.task_id, ErrorCode.UNKNOWN, str(e))
            return

        if not check_task(task):
            logger.info(f"遇到无效任务,删除中...,task:{task}")
            taskMapper.remove(task.id)
            return

        try:
            # 将任务设置成执行中
            task.status = Status.DOING.value
            taskMapper.set_status(task.task_id, task.status)
            logger.debug(f"将task设置为doing状态,task_id:{task.task_id}")
            _callback(get_connector(task.source), task)

            execute_result = run_task(task, _account)

            if execute_result.code == 0:
                # 成功
                task.status = Status.SUCCESS.value
                task.video_url = execute_result.data
                taskMapper.set_success(task.task_id, video_url=execute_result.data)
                _callback(get_connector(task.source), task)
            elif execute_result.code == ErrorCode.TASK_COMPLETED:
                # 任务已完成，什么都不需要做
                pass
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

    tasks = taskMapper.get_executable_tasks(video_processor_thread_count)
    if len(tasks) == 0:
        logger.info('All tasks have been completed!!!')
    for _task in tasks:
        is_threadpool_idle(videoThreadPool)
        account = fetch_account(_task.source)
        taskMapper.set_status(_task.task_id, Status.DOING.value)
        videoThreadPool.submit(execute_task_func, _task, account)
        time.sleep(10)


def fetch(connector, source):
    count = taskMapper.get_un_success_count()
    if count > 10:
        # 还有没做完的任务，先不取，或许被其它节点取了?
        return
    logger.debug(f"【{source}】Get task")
    tasks = connector.fetch(10)
    for task in tasks:
        task['source'] = source
        # if not check_task(task):
        #     logger.info(f"遇到无效任务,无视中...,task:{task}")
        #     continue
    if len(tasks) == 0:
        return
    taskMapper.bulk_insert_tasks(tasks)
    logger.debug(f"【{source}】Save task success,task count:{len(tasks)}")
    # 执行爬取操作
    execute_task()
    # 将爬取结果上传至对应接口


def fetch_runway():
    try:
        fetch(runwayConnector, TaskSource.RUN_WAY)
    except Exception as e:
        logger.exception(e)


def fetch_pika():
    try:
        fetch(pikaConnector, TaskSource.PIKA)
    except Exception as e:
        logger.exception(e)


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
    callback(runwayConnector, TaskSource.RUN_WAY)


def callback_pika():
    callback(pikaConnector, TaskSource.PIKA)


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
    logger.info(f"当前worker_id:{get_worker_id()}")
    # 在项目第一次启动时创建表
    if not is_task_table_created():
        create_task_tables()
    if not is_account_table_created():
        create_account_tables()

    if not check_chromium_installed():
        logger.info("初次使用,环境准备中")
        install_chromium()
        logger.info("准备完成")

    sync_task_table_structure()
    sync_account_table_structure()
    checking()
    logger.info("初始化成功")

    # 创建后台调度器
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_runway, 'interval', seconds=10, next_run_time=datetime.now())
    scheduler.add_job(fetch_pika, 'interval', seconds=10, next_run_time=datetime.now())

    scheduler.add_job(callback_runway, 'interval', seconds=10)
    scheduler.add_job(execute_task, 'interval', seconds=10, next_run_time=datetime.now())
    scheduler.start()

    event = threading.Event()

    event.wait()


if __name__ == "__main__":
    main()
