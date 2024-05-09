from processor.pika_abstract_processor import PikaAbstractProcessor
import logging
import logger_config

class PikaImgProcessor(PikaAbstractProcessor):

    def write(self, page):
        for num in range(1, 10):
            page.mouse.click(10, 10)
        explor_page = page.locator("xpath=//main//a[contains(@class,'font-extra-thick')][2]")
        for i in range(1, 20):
            explor_page.click()

        seconds = self.get_seconds(page)
        logging.info(self.name + "当前余额:%s", seconds)
        logging.info(self.name + "开始提交图片")
        file_path = self.image
        page.locator("xpath=//input[@id='file-input']").set_input_files(file_path)
        pass
