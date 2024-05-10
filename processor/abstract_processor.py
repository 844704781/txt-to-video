from abc import abstractmethod
from playwright.sync_api import sync_playwright
import subprocess
import os
from entity.video_const import VideoConst
from typing import Optional, Callable

from logger_config import logger


class AbstractProcessor:
    def __init__(self, username, password, name, task_id: str = None):
        self.username = username
        self.password = password
        self.content = None
        self.image = None
        self.name = f'【{name}】'
        if task_id is not None:
            self.name = self.name + f'（{task_id}）'
        self.task_id = task_id
        self.const = name
        self.progress_callback = None
        self.balance_callback = None
        if 'RUN_WAY' in self.const:
            self.source = 'RUNWAY'
        elif 'PIKA' in self.const:
            self.source = 'PIKA'
        else:
            # nothing...
            pass

    def set_progress_callback(self, progress_callback: object = None):
        self.progress_callback = progress_callback
        return self

    def set_balance_callback(self, balance_callback: object = None):
        self.balance_callback = balance_callback
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
                browser = p.chromium.launch(
                    ignore_default_args=["--enable-automation"],
                    # args=["--no-sandbox",
                    #       "--disable-setuid-sandbox",
                    #       "--disable-gpu",
                    #       "--disable-dev-shm-usage",
                    #       "--no-first-run",
                    #       "--no-zygote",
                    #       "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36",
                    #       "--blink-settings=imagesEnabled=false"
                    #       ],
                    headless=False)

                cookies = os.path.join('cookies', f'{self.source}-{self.username}-state.json')
                logger.info(self.name + "判断是否登录")
                if os.path.exists(cookies):
                    # 使用之前的登录信息
                    context = browser.new_context(storage_state=cookies)
                    logger.info(self.name + "已登录")
                else:
                    context = browser.new_context()
                    logger.info(self.name + "未登录")

                logger.info(self.name + "准备中...")
                page = context.new_page()

                # 设置额外的 HTTP 请求头，禁止加载图片，加快请求速度
                def abort_img(route):
                    # 资源类型  "stylesheet", "script", "image", "font", "xhr"
                    if route.request.resource_type in ["image"]:
                        route.abort()
                    else:
                        route.continue_()

                page.route("**/*", abort_img)

                # logger.info(self.name + "登录成功")
                logger.info(self.name + "尝试获取余额，写入内容...")
                is_login = self.write(page)
                if not is_login:
                    if not os.path.exists(cookies):
                        logger.info(self.name + "登录中...")
                        is_login_success = self.login(page)
                        if not is_login_success:
                            return
                        # 保存登录信息
                        context.storage_state(path=cookies)
                        logger.info(self.name + "登录成功")
                        logger.info(self.name + "尝试获取余额，写入内容...")
                        self.write(page)

                logger.info(self.name + "获取余额、写入内容成功")
                self.commit(page)
                logger.info(self.name + "提交内容,视频生成中...")
                href = self.loading(page)

                logger.info(self.name + "url:\t{}", href)
            except Exception as e:
                logger.exception(self.name + "playwright出错:", e)
                raise e
            finally:
                context.close()
                browser.close()
                logger.info(self.name + "资源回收")
            return href
