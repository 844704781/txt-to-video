import json
from abc import abstractmethod
from playwright.sync_api import sync_playwright
import subprocess
import os
from entity.video_const import VideoConst
from typing import Optional, Callable

from logger_config import logger

project_root = os.path.dirname(os.path.abspath(__file__))


class AbstractProcessor:
    def __init__(self, username, password, name, task_id: str = None):
        self.username = username
        self.password = password
        self.content = None
        self.image = None
        self.website = name
        self.name = f'【{name}】'
        if task_id is not None:
            self.name = self.name + f'（{task_id}）'
        self.task_id = task_id
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
        progress = '|' + '■' * num_blocks + ' ' * (bar_length - num_blocks) + '|' + str(percent) + "%"
        logger.info(f'{self.name} {progress}')
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
    def save_cookies_to_file(cookies, local_storage_data, filename):
        cookies_dir = os.path.join(project_root, 'cookies')
        if not os.path.exists(cookies_dir):
            os.makedirs(cookies_dir)
        filename = cookies_dir + filename

        with open(filename, 'w') as file:
            json.dump({'cookies': cookies, 'local_storage': local_storage_data}, file)

    @staticmethod
    # 从文件加载Cookies
    def load_cookies_from_file(filename):
        cookies_dir = os.path.join(project_root, 'cookies')
        filename = cookies_dir + filename
        if not os.path.exists(filename):
            return None
        with open(filename, 'r') as file:
            data = json.load(file)
            return data['cookies'], data['local_storage']

    def run(self):
        if self.const in [VideoConst.PIKA_TXT, VideoConst.PIKA_MIX,
                          VideoConst.RUN_WAY_TXT, VideoConst.RUN_WAY_MIX]:
            if len(self.content) < 256:
                logger.info(f"{self.name}当前提交提示词:\t{self.content}")
        if self.const in [VideoConst.PIKA_IMG, VideoConst.PIKA_MIX, VideoConst.RUN_WAY_IMG, VideoConst.RUN_WAY_MIX]:
            if 0 < len(self.image) < 256:
                logger.info(f"{self.name}当前提交图片:\t{self.image}")

        # 使用 Playwright 执行操作
        with sync_playwright() as p:
            browser = None
            href = None
            try:
                browser = p.chromium.launch(headless=False)

                logger.info(self.name + "准备中...")
                page = browser.new_page()

                # 设置额外的 HTTP 请求头，禁止加载图片，加快请求速度
                def abort_img(route):
                    # 资源类型  "stylesheet", "script", "image", "font", "xhr"
                    if route.request.resource_type in ["image"]:
                        route.abort()
                    else:
                        route.continue_()

                page.route("**/*", abort_img)
                # logger.info(self.name + "登录中...")
                data = self.load_cookies_from_file(self.website)
                if data is not None:
                    page.context.add_cookies(data[0])
                    page.evaluate('''(local_storage_data) => {
                        for (let key in local_storage_data) {
                            localStorage.setItem(key, local_storage_data[key]);
                        }
                    }''', data[1])

                else:
                    cookies, local_storage_data = self.login(page)
                    self.save_cookies_to_file(cookies, local_storage_data, self.website)
                # logger.info(self.name + "登录成功")
                logger.info(self.name + "正在写入内容...")
                self.write(page)

                self.commit(page)
                logger.info(self.name + "提交内容,视频生成中...")
                href = self.loading(page)

                logger.info(self.name + "url:\t{}", href)
            except Exception as e:
                logger.exception(self.name + "playwright出错:", e)
                raise e
            finally:
                browser.close()
                logger.info(self.name + "资源回收")
            return href
