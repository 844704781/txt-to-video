import time

from processor.pika_abstract_processor import PikaAbstractProcessor

from logger_config import logger

from common.custom_exception import CustomException
from entity.error_code import ErrorCode
from common.custom_exception import CustomException
from entity.error_code import ErrorCode

class PikaMixProcessor(PikaAbstractProcessor):

    def write(self, page):
        if 'blank' in page.url:
            # 尝试进入首页
            try:
                page.goto(self.host, wait_until="domcontentloaded")
            except Exception as e:
                raise CustomException(ErrorCode.TIME_OUT, "无法连接" + self.LOGIN_PATH + "请检查网络")

        if '/login' in page.url or '/home' in page.url:
            return False


        for num in range(1, 10):
            page.mouse.click(10, 10)
        explor_page = page.locator("xpath=//main//a[contains(@class,'font-extra-thick')][2]")
        for i in range(1, 20):
            explor_page.click()

        if self.image is None:
            raise CustomException(ErrorCode.INVALID_ARG, 'Empty image')
        if self.content is None:
            raise CustomException(ErrorCode.INVALID_ARG, "Empty content")

        for num in range(0, 2):
            page.mouse.click(10, 10)
            time.sleep(1)
        seconds = self.get_seconds(page)
        logger.info(self.name + "当前余额:{}", seconds)
        logger.info(self.name + "开始提交提示词和图片")

        file_path = self.image
        page.locator("xpath=//input[@id='file-input']").set_input_files(file_path)

        text_input = page.locator("xpath=//main//textarea[@name='promptText']")
        text_input.fill(self.content)

        return True
