from processor.runway_abstract_processor import RunWayAbstractParser

from logger_config import logger



class RunWayTxtParser(RunWayAbstractParser):

    def write(self, page):
        """
        提交提示词
        :param page:
        :return:
        """
        page.goto(self.GEN_PATH, wait_until="domcontentloaded")
        seconds = self.get_seconds(page)
        logger.info(self.name + "当前余额:%s", seconds)
        logger.info(self.name + "开始提交提示词")
        page.wait_for_selector('button.Button-sc-c1bth8-0')
        text_input = page.locator('textarea[aria-label="Text Prompt Input"]')
        text_input.fill(self.content)
        return True
