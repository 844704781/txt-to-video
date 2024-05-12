import time
from processor.runway_abstract_processor import RunWayAbstractParser
from logger_config import logger


class RunWayImgParser(RunWayAbstractParser):
    def write(self, page):
        """
        选择一张本地图片
        :param page:
        :return:
        """
        page.goto(self.GEN_PATH, wait_until="load")
        if '/login' in page.url:
            return False
        seconds = self.get_seconds(page)
        logger.info(self.name + "当前余额:{}", seconds)
        logger.info(self.name + "开始提交图片")
        file_path = self.image
        page.locator("input[type='file']").set_input_files(file_path)
        order_sent = page.locator("xpath=//div[contains(@class,'Container-sc-ajvl93-0')]")
        i = 0
        while i < 20:
            uploading = order_sent.get_attribute('data-uploading', timeout=3000)
            logger.info(self.name + f"当前图片状态:uploading:{uploading}")
            if uploading == 'false':
                break
            time.sleep(5)
            i += 1
        return True
