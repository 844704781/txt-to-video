import time
from abc import abstractmethod

from processor.abstract_processor import AbstractProcessor
import net_tools


class PikaAbstractProcessor(AbstractProcessor):

    def __init__(self, username, password, name):
        super().__init__(username, password, name)
        host = 'https://pika.art'
        self.LOGIN_PATH = host + '/login'
        print(self.name + "checking ->" + host)
        check_result = net_tools.check_website_availability(host)
        print(self.name + "result ->" + str(check_result))
        if not check_result:
            raise Exception("无法连接" + host + "请检查网络")

    def login(self, page):
        try:
            page.goto(self.LOGIN_PATH, wait_until="domcontentloaded")
        except Exception as e:
            raise e

        btn = page.wait_for_selector('//main//button[3]')
        for num in range(1, 10):
            try:
                btn.click()
                time.sleep(1)
            except Exception:
                pass

        username_input = page.locator('xpath=//main//form/div[1]/input')
        username_input.fill(self.username)
        password_input = page.locator('xpath=//main//form/div[2]//input')
        password_input.fill(self.password)
        login_btn = page.locator('xpath=//main//form/button')
        login_btn.click()
        faq = page.locator("xpath=//main//a[@href='/faq']").get_attribute('href')
        if faq is None:
            time.sleep(1000)

    @abstractmethod
    def write(self, page):
        pass

    def commit(self, page):
        submit_btn = page.locator("xpath=//main//button[@type='submit']")
        submit_btn.click()

        # 等待按钮变可按状态
        while True:
            disabled = submit_btn.evaluate('(element) => element.disabled')
            if not disabled:
                break
            time.sleep(1)

    def loading(self, page):
        page.mouse.click(0, 0)

        percent = 0
        while True:
            progress_text = page.locator(
                "xpath=//main//div[contains(@class,'group/card')][1]//div[@class='relative']//*[name()='circle'][2]")
            try:
                dasharray = progress_text.get_attribute('stroke-dasharray', timeout=5000)
            except Exception as e:
                dasharray = None

            if dasharray is None:
                percent = 100

            self.print_progress(percent)

            if dasharray is None:

                print("\n" + self.name + "视频生成成功")
                video = page.locator(
                    "xpath=//main//div[contains(@class,'group/card')][1]//div[@class='relative']//video/source")
                try:
                    link = video.get_attribute('src')
                except Exception as e:
                    print(self.name + "Something went wrong while generating this video")
                    link = None
                break
            else:
                # pika给的不准
                dasharray = progress_text.get_attribute('stroke-dasharray')
                dashoffset = progress_text.get_attribute('stroke-dashoffset')
                percent = 100 - float(dashoffset) / float(dasharray) * 100 // 1
            time.sleep(1)
        return link

    def get_seconds(self, page):
        p_tag = page.locator("xpath=//div[contains(@class,'bg-plan-credits')]/p")
        return p_tag.inner_text()
