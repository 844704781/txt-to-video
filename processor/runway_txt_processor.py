from processor.runway_abstract_processor import RunWayAbstractParser

import logging
import logger_config


class RunWayTxtParser(RunWayAbstractParser):

    def write(self, page):
        """
        提交提示词
        :param page:
        :return:
        """
        page.goto(self.GEN_PATH, wait_until="domcontentloaded")
        seconds = self.get_seconds(page)
        logging.info(self.name + "当前余额:%s", seconds)
        logging.info(self.name + "开始提交提示词")
        page.wait_for_selector('button.Button-sc-c1bth8-0')
        text_input = page.locator('textarea[aria-label="Text Prompt Input"]')
        text_input.fill(self.content)
        return True
