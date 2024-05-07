from processor.abstract_processor import AbstractProcessor
import time
from abc import abstractmethod


class RunWayAbstractParser(AbstractProcessor):
    """
        处理runway公共方法
    """

    def __init__(self, username, password, name):
        super().__init__(username, password, name)
        self.LOGIN_PATH = 'https://app.runwayml.com/login'
        self.GEN_PATH = 'https://app.runwayml.com/video-tools/teams/v2v2/ai-tools/gen-2'

    def login(self, page):
        try:
            page.goto(self.LOGIN_PATH, wait_until="domcontentloaded")
        except Exception as e:
            return
        # 输入账号
        username_input = page.locator('input[name="usernameOrEmail"]')
        username_input.fill(self.username)

        # 输入密码
        password_input = page.locator('input[type="password"]')
        password_input.fill(self.password)

        # 点击提交按钮
        submit_button = page.locator('button[type="submit"]')
        submit_button.click()
        # 等待一段时间确保页面加载完全
        page.wait_for_selector('a[href="/ai-tools/gen-2"]')
        # 示例：保存
        return page.context.cookies()

    def get_seconds(self, page):
        p_tag = page.locator('.Text-sc-cweq7v-1.GetMoreCreditsButton__UnitsLeftText-sc-66lapz-0.fNdEQX')
        return p_tag.inner_text()

    def loading(self, page):
        # 等待生成结果
        # 这里可以根据页面的加载状态或其他条件来判断生成结果是否加载完成
        src_attribute = None
        percent = 0
        while True:
            video_element = page.locator('.OutputVideo___StyledVideoOutputNative-sc-di1eng-2.fLPiNR')
            count = video_element.count()
            percent = percent if count == 0 else 100
            self.print_progress(percent)
            if count > 0:
                print(self.name + "\n视频生成成功")
                src_attribute = video_element.evaluate('''element => element.getAttribute('src')''')
                break
            else:
                # 获取文本内容
                element_locator = page.locator('.ProgressRing__CircleText-sc-1ed2gw0-3.jBjiPh')  # 使用你提供的类名选择器
                try:
                    progress_text = element_locator.inner_html()
                except Exception as e:
                    continue

                progress_text = int(progress_text[:-1])
                percent = 100 / 75 * progress_text // 1
            # 暂停一段时间再进行下一次检查
            time.sleep(1)
        return src_attribute

    @abstractmethod
    def write_tips(self, page):
        pass

    @abstractmethod
    def commit_tips(self, page):
        pass
