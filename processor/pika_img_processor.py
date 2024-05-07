from processor.pika_abstract_processor import PikaAbstractProcessor


class PikaImgProcessor(PikaAbstractProcessor):

    def write(self, page):
        for num in range(1, 10):
            page.mouse.click(10, 10)
        seconds = self.get_seconds(page)
        print(self.name + "当前余额:", seconds)
        print(self.name + "开始提交图片")
        file_path = self.content
        page.locator("xpath=//input[@id='file-input']").set_input_files(file_path)
        pass
