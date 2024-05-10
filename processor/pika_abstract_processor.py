import time
from abc import abstractmethod
import re

from processor.abstract_processor import AbstractProcessor
import net_tools
from entity.error_code import ErrorCode
from entity.result_utils import ResultDo
from common.custom_exception import CustomException

from logger_config import logger


class PikaAbstractProcessor(AbstractProcessor):

    def __init__(self, username, password, name, task_id: str = None):
        super().__init__(username, password, name, task_id)
        host = 'https://pika.art'
        self.LOGIN_PATH = host + '/login'
        logger.info(self.name + "checking ->" + host)
        check_result = net_tools.check_website_availability(host)
        logger.info(self.name + "result ->" + str(check_result))
        if not check_result:
            raise CustomException(ErrorCode.TIME_OUT, "无法连接" + host + "请检查网络")

    def login(self, page):
        try:
            page.goto(self.LOGIN_PATH, wait_until="domcontentloaded")
        except Exception as e:
            raise CustomException(ErrorCode.TIME_OUT, "无法连接" + self.LOGIN_PATH + "请检查网络")

        btn = page.wait_for_selector('//main//button[3]')
        for num in range(1, 10):
            try:
                btn.click()
                time.sleep(1)
            except Exception:
                pass

        username_input = page.locator('xpath=//main//form/div[1]/input')
        username_input.fill(self.username)
        password_input = page.locator('xpath=//main//form/div[2]//input')
        password_input.fill(self.password)
        login_btn = page.locator('xpath=//main//form/button')
        login_btn.click()
        faq = page.locator("xpath=//main//a[@href='/faq']").get_attribute('href')
        if faq is None:
            time.sleep(60)

    @abstractmethod
    def write(self, page):
        pass

    def commit(self, page):
        submit_btn = page.locator("xpath=//main//button[@type='submit']")
        submit_btn.wait_for(timeout=60000)
        submit_btn.click()

        # 等待按钮变可按状态
        while True:
            disabled = submit_btn.evaluate('(element) => element.disabled')
            if not disabled:
                break
            time.sleep(1)

    def loading(self, page):
        page.mouse.click(0, 0)

        percent = 0
        while True:
            progress_text = page.locator(
                "xpath=//main//div[contains(@class,'group/card')][1]//div[@class='relative']//*[name()='circle'][2]")
            try:
                dasharray = progress_text.get_attribute('stroke-dasharray', timeout=5000)
            except Exception as e:
                dasharray = None

            if dasharray is None:
                percent = 100

            self.print_progress(percent)

            if dasharray is None:

                logger.info("\n" + self.name + "视频生成成功")
                video = page.locator(
                    "xpath=//main//div[contains(@class,'group/card')][1]//div[@class='relative']//video/source")
                f = False
                ec = None
                link = None
                for i in range(0, 10):
                    try:
                        link = video.get_attribute('src', timeout=30000)
                        f = True
                    except Exception as e:
                        ec = e
                        time.sleep(1)
                        continue
                    if f:
                        break
                if not f:
                    logger.exception(self.name + "获取视频链接出错", ec)
                    link = None
                break

            else:
                # pika给的不准
                dasharray = progress_text.get_attribute('stroke-dasharray')
                dashoffset = progress_text.get_attribute('stroke-dashoffset')
                percent = 100 - float(dashoffset) / float(dasharray) * 100 // 1
            time.sleep(5)
        return link

    def get_seconds(self, page):
        def extract_number(text):
            if text is None:
                return 2147483647
            match = re.search(r'\d+', text)
            if match:
                return int(match.group())
            else:
                return 0

        # TODO 处理无次数限制情况

        p_tag = page.locator("xpath=//div[contains(@class,'bg-plan-credits')]/p")
        p_tag_text = None
        try:
            p_tag_text = p_tag.inner_text(timeout=3000)
        except Exception as e:
            pass
        count = extract_number(p_tag_text)
        if count < 10:
            raise CustomException(ErrorCode.INSUFFICIENT_BALANCE, f"当前余额:{count},余额不足,请充值")
        return count
