import time

from processor.pika_abstract_processor import PikaAbstractProcessor


class PikaTxtAbstractProcessor(PikaAbstractProcessor):

    def write(self, page):
        for num in range(1, 10):
            page.mouse.click(10, 10)
            time.sleep(1)
        seconds = self.get_seconds(page)
        print(self.name + "当前余额:", seconds)
        print(self.name + "开始提交提示词")
        text_input = page.locator("xpath=//main//textarea[@name='promptText']")
        text_input.fill(self.content)
        return True
