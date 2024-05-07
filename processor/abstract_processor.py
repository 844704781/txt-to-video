from abc import abstractmethod
from playwright.sync_api import sync_playwright
import subprocess
import os


class AbstractProcessor:
    def __init__(self, username, password, name):
        self.username = username
        self.password = password
        self.content = None
        self.name = f'【{name}】'

    def set_content(self, content):

        """
        设置提示词
        :param content:
        :return:
        """
        self.content = content
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
        print(f'{progress}', end='', flush=True)

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
            print("初次使用,环境准备中")
            self.install_chromium()
            print("准备完成")

        if len(self.content) < 256:
            print(f"{self.name}当前提交内容:\t{self.content}")

        # 使用 Playwright 执行操作
        with sync_playwright() as p:
            browser = None
            href = None
            try:
                browser = p.chromium.launch(headless=False)
                print(self.name + "准备中...")
                page = browser.new_page()
                # print(self.name + "登录中...")
                self.login(page)
                # print(self.name + "登录成功")
                print(self.name + "正在写入内容...")
                self.write(page)

                self.commit(page)
                print(self.name + "提交内容,视频生成中...")
                href = self.loading(page)

                print(self.name + "url:\t", href)
            finally:
                browser.close()
            return href
