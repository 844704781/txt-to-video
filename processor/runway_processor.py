import time
from processor.abstract_processor import AbstractProcessor


class RunWayParser(AbstractProcessor):
    '''
    处理runway
    '''
    LOGIN_PATH = 'https://app.runwayml.com/login'
    GEN_PATH = 'https://app.runwayml.com/video-tools/teams/v2v2/ai-tools/gen-2'

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

    def write_tips(self, page):
        page.goto(self.GEN_PATH, wait_until="domcontentloaded")
        seconds = self.get_seconds(page)
        print(self.name + "当前余额:", seconds)
        print(self.name + "开始提交提示词")
        page.wait_for_selector('button.Button-sc-c1bth8-0')
        text_input = page.locator('textarea[aria-label="Text Prompt Input"]')
        text_input.fill(self.tips)
        return True

    def commit_tips(self, page):
        # 点击按钮
        generate_button = page.locator('button:has-text("Generate 4s")')
        generate_button.click()

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

    def get_seconds(self, page):
        p_tag = page.locator('.Text-sc-cweq7v-1.GetMoreCreditsButton__UnitsLeftText-sc-66lapz-0.fNdEQX')
        return p_tag.inner_text()


# 主函数
def main():
    pass
    # config = configparser.ConfigParser()
    # config.read('../config.ini')
    #
    # parser = argparse.ArgumentParser(description='命令行参数示例')
    # # 添加参数选项
    # parser.add_argument('-u', '--username', type=str, help='用户名')
    # parser.add_argument('-p', '--password', type=str, help='密码')
    # parser.add_argument('-t', '--tips', type=str, help='提示词')
    # # 解析命令行参数
    # args = parser.parse_args()
    # username = args.username
    # password = args.password
    # tips = args.tips
    # if username is None:
    #     username = config['Settings']['username']
    # if password is None:
    #     password = config['Settings']['password']
    #
    # if tips is None:
    #     tips = config['Settings']['tips']
    # if len(tips) < 256:
    #     print(f"当前提示词:\t{tips}")
    #
    # if username is None or username == '' \
    #         or password is None or password == '':
    #     print("账号密码无效")
    #
    # if tips is None or tips == '':
    #     print("请输入提示词")
    #
    # download_link = RunWayParser(username, password).set_tips(tips).run()
    # print("视频链接:", download_link)


if __name__ == "__main__":
    main()
