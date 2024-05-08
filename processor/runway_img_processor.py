import time
from processor.runway_abstract_processor import RunWayAbstractParser
import logging
import logger_config

class RunWayImgParser(RunWayAbstractParser):
    def write(self, page):
        """
        选择一张本地图片
        :param page:
        :return:
        """
        page.goto(self.GEN_PATH, wait_until="domcontentloaded")
        seconds = self.get_seconds(page)
        logging.info(self.name + "当前余额:%s", seconds)
        logging.info(self.name + "开始提交图片")
        file_path = self.image
        page.locator("input[type='file']").set_input_files(file_path)
        order_sent = page.locator("div[data-uploading='false']")
        order_sent.wait_for(timeout=60000)
