from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from connector.runway_connector import RunwayConnector
from connector.pika_connector import PikaConnector
from db.taskdb import create_tables, is_table_created, TaskMapper, Source
from entity.task_status import Status
from entity.task_make_type import MakeType
from entity.video_const import VideoConst, transfer
from entity.result_utils import ResultDo
from entity.error_code import ErrorCode
import configparser
import threading
import logging
from entity.iconfig_parser import ConfigParser
from video_builder import VideoBuilder

runwayConnector = RunwayConnector()
pikaConnector = PikaConnector()
taskMapper = TaskMapper()

scheduler_logger = logging.getLogger("apscheduler.executors.default")

scheduler_logger.setLevel(logging.CRITICAL)
'''
获取参数
'''

config = configparser.ConfigParser()
config.read('./config.ini')


def run_task(task):
    print(f"【{task.source}】Execute task start")
    if task.source == Source.PIKA:
        username = config['PIKA']['username']
        password = config['PIKA']['password']
    elif task.source == Source.RUN_WAY:
        username = config['RUNWAY']['username']
        password = config['RUNWAY']['password']
    else:
        raise Exception(ResultDo(ErrorCode.UNSUPPORTED, f'Unsupported source {task.source}'))

    i_config = ConfigParser(username, password)
    service = transfer(task.source, task.make_type)

    processor = VideoBuilder.create().set_config(i_config).set_form(task.prompt, task.image_url) \
        .set_processor(service).build()

    try:
        video_url = processor.run()
    except Exception as e:
        print(f"【{task.source}】Execute task end,error")
        return ResultDo(ErrorCode.ERR_BROWSER, message=str(e))

    print(f"【{task.source}】Execute task end")
    return ResultDo(code=ErrorCode.OK, data=video_url)


# 执行任务
def execute_task():
    tasks = taskMapper.get_executable_tasks(1)
    task = tasks[0]
    execute_result = run_task(task)

    if execute_result.code == 0:
        taskMapper.set_success(task.task_id, video_url=execute_result.data)
    else:
        taskMapper.set_status(task.task_id, Status.FAIL)


def fetch(connector, source):
    print(f"【{source}】Get task")
    tasks = connector.fetch(1)
    for task in tasks:
        task['source'] = source
    taskMapper.bulk_insert_tasks(tasks)
    print(f"【{source}】Save task success")
    # 执行爬取操作
    # 将爬取结果上传至对应接口


def fetch_runway():
    fetch(runwayConnector, Source.RUN_WAY)


def fetch_pika():
    fetch(pikaConnector, Source.PIKA)


def callback(connector, source):
    count = taskMapper.count(source)
    while count > 0:
        print(f"【{source}】UnSync task count :{count}")
        task = taskMapper.find_unsync_task_by_source(source)
        if task is None:
            return
        print(f"【{source}】Callback task")
        errcode = 0
        errmsg = None
        payload = {
            "task_id": task.task_id,
            "progress": task.progress,
            "status": task.status,
            "errcode": errcode,
            "errmsg": errmsg,
            "video_url": task.video_url
        }
        try:
            connector.callback(payload)
        except Exception as e:
            print(f"【{source}】Callback task Fail,message:", e.args[0].message)
            return
        taskMapper.set_synced_by_task_id(task.get('task_id'))
        print(f"【{source}】Callback task Success")


def callback_runway():
    callback(runwayConnector, Source.RUN_WAY)


def callback_pika():
    callback(pikaConnector, Source.PIKA)


# 在项目第一次启动时创建表
if not is_table_created():
    print("初始化中...")
    create_tables()
    print("初始化成功")
# 创建后台调度器


scheduler = BackgroundScheduler()
# scheduler.add_job(fetch_runway, 'interval', seconds=10, next_run_time=datetime.now())
# scheduler.add_job(fetch_pika, 'interval', seconds=10, next_run_time=datetime.now())

# scheduler.add_job(callback_runway, 'interval', seconds=10)
scheduler.add_job(execute_task, 'interval', seconds=60, next_run_time=datetime.now())
scheduler.start()

event = threading.Event()

event.wait()
