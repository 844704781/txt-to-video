from abc import abstractmethod
from playwright.sync_api import sync_playwright
import subprocess
import os
from entity.video_const import VideoConst
from typing import Optional, Callable

import logging
import logger_config


class AbstractProcessor:
    def __init__(self, username, password, name):
        self.username = username
        self.password = password
        self.content = None
        self.image = None
        self.name = f'【{name}】'
        self.const = name
        self.progress_callback = None

    def set_progress_callback(self, progress_callback: object = None):
        self.progress_callback = progress_callback
        return self

    def set_form(self, content, image):

        """
        设置提示词
        :param image:
        :param content:
        :return:
        """
        self.content = content
        self.image = image
        return self

    @abstractmethod
    def login(self, page):
        """
        登录
        :param page:
        :return:
        """
        pass

    @abstractmethod
    def write(self, page):
        """
        写提示词/图片
        :param page:
        :return:
        """
        pass

    @abstractmethod
    def commit(self, page):
        """
        提交提示词/图片
        :param page:
        :return:
        """

    def print_progress(self, percent):
        """
        打印进度
        :param percent:
        :return:
        """
        num_blocks = int(percent // 2)
        bar_length = 50
        progress = '\r|' + '■' * num_blocks + ' ' * (bar_length - num_blocks) + '|' + str(percent) + "%"
        logging.info(f'{progress}', end='', flush=True)
        if self.progress_callback is not None:
            self.progress_callback(percent)

    @abstractmethod
    def loading(self, page):
        """
        等待生成结果
        这里可以根据页面的加载状态或其他条件来判断生成结果是否加载完成
        :param page:
        :return:
        """
        pass

    @abstractmethod
    def get_seconds(self, page):
        """
        获取账号剩余积分
        :param page:
        :return:
        """
        pass

    @staticmethod
    def check_chromium_installed():
        """
        检查是否已安装 Chromium 浏览器
        :return:
        """
        with sync_playwright() as p:
            # 获取 Chromium 的可执行文件路径
            chromium_path = p.chromium.executable_path

            if os.path.exists(chromium_path):
                return True
            else:
                return False

    @staticmethod
    def install_chromium():
        """
        安装 Chromium 浏览器
        :return:
        """
        subprocess.run(["playwright", "install", "chromium"])

    def run(self):
        if not self.check_chromium_installed():
            logging.info("初次使用,环境准备中")
            self.install_chromium()
            logging.info("准备完成")
        if self.const in [VideoConst.PIKA_TXT, VideoConst.PIKA_MIX,
                          VideoConst.RUN_WAY_TXT, VideoConst.RUN_WAY_MIX]:
            if len(self.content) < 256:
                logging.info(f"{self.name}当前提交提示词:\t{self.content}")
        if self.const in [VideoConst.PIKA_IMG, VideoConst.PIKA_MIX, VideoConst.RUN_WAY_IMG, VideoConst.RUN_WAY_MIX]:
            if 0 < len(self.image) < 256:
                logging.info(f"{self.name}当前提交图片:\t{self.image}")

        # 使用 Playwright 执行操作
        with sync_playwright() as p:
            browser = None
            href = None
            try:
                browser = p.chromium.launch(headless=True)
                logging.info(self.name + "准备中...")
                page = browser.new_page()
                # logging.info(self.name + "登录中...")
                self.login(page)
                # logging.info(self.name + "登录成功")
                logging.info(self.name + "正在写入内容...")
                self.write(page)

                self.commit(page)
                logging.info(self.name + "提交内容,视频生成中...")
                href = self.loading(page)

                logging.info(self.name + "url:\t%s", href)
            finally:
                browser.close()
            return href
