import os
import logging
from logging.handlers import RotatingFileHandler
import sys

# 获取当前项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')

# 如果日志目录不存在，则创建
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 创建日志记录器
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# 创建按大小轮转的日志处理程序
rotating_handler = RotatingFileHandler(os.path.join(LOG_DIR, 'all.log'), maxBytes=10 * 1024 * 1024, backupCount=5)
rotating_handler.setLevel(logging.DEBUG)
rotating_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - Thread %(thread)d - %(message)s'))

# 创建控制台处理程序
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - Thread %(thread)d - %(message)s'))

# 将处理程序添加到日志记录器
logger.addHandler(rotating_handler)
logger.addHandler(console_handler)
