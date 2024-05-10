import time

from processor.pika_abstract_processor import PikaAbstractProcessor

from logger_config import logger


class PikaTxtAbstractProcessor(PikaAbstractProcessor):

    def write(self, page):
        for num in range(1, 10):
            page.mouse.click(10, 10)
        explor_page = page.locator("xpath=//main//a[contains(@class,'font-extra-thick')][2]")
        i = 0
        while i < 10:
            try:
                explor_page.click()
            except Exception as e:
                time.sleep(1)
                continue

        seconds = self.get_seconds(page)
        logger.info(self.name + "当前余额:{}", seconds)
        logger.info(self.name + "开始提交提示词")
        text_input = page.locator("xpath=//main//textarea[@name='promptText']")
        text_input.fill(self.content)
        return True
