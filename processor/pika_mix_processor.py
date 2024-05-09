import time

from processor.pika_abstract_processor import PikaAbstractProcessor

import logging
import logger_config
from common.custom_exception import CustomException
from entity.error_code import ErrorCode


class PikaMixProcessor(PikaAbstractProcessor):

    def write(self, page):
        if self.image is None:
            raise CustomException(ErrorCode.INVALID_ARG, 'Empty image')
        if self.content is None:
            raise CustomException(ErrorCode.INVALID_ARG, "Empty content")

        for num in range(1, 10):
            page.mouse.click(10, 10)
            time.sleep(1)
        seconds = self.get_seconds(page)
        logging.info(self.name + "当前余额:%s", seconds)
        logging.info(self.name + "开始提交提示词和图片")

        file_path = self.image
        page.locator("xpath=//input[@id='file-input']").set_input_files(file_path)

        text_input = page.locator("xpath=//main//textarea[@name='promptText']")
        text_input.fill(self.content)

        return True
