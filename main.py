from playwright.sync_api import sync_playwright
import subprocess
import os
import time
import configparser
import argparse


# 检查是否已安装 Chromium 浏览器
def check_chromium_installed():
    with sync_playwright() as p:
        # 获取 Chromium 的可执行文件路径
        chromium_path = p.chromium.executable_path

        if os.path.exists(chromium_path):
            return True
        else:
            return False
    # if os.path.exists(
    #         '/Users/watermelon/Library/Caches/ms-playwright/chromium-1112/chrome-mac/Chromium.app/Contents/MacOS/Chromium'):
    #     return True
    # else:
    #     return False


# 安装 Chromium 浏览器
def install_chromium():
    subprocess.run(["playwright", "install", "chromium"])


class RunWayParser:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.tips = None

    def set_tips(self, tips):
        self.tips = tips
        return self

    def login(self, page):
        print("登录中...")
        try:
            page.goto("https://app.runwayml.com/login", wait_until="domcontentloaded")
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
        print("登录成功")
        # 示例：保存
        return page.context.cookies()

    def write_tips(self, page):
        page.goto("https://app.runwayml.com/video-tools/teams/v2v2/ai-tools/gen-2", wait_until="domcontentloaded")
        seconds = self.get_seconds(page)
        print("当前余额:", seconds)
        print("开始提交提示词")
        page.wait_for_selector('button.Button-sc-c1bth8-0')
        text_input = page.locator('textarea[aria-label="Text Prompt Input"]')
        text_input.fill(self.tips)
        return True

    def commit_tips(self, page):
        # 点击按钮
        generate_button = page.locator('button:has-text("Generate 4s")')
        generate_button.click()
        print("提示词提交成功,正在生成视频中...")

    def print_progress(self, percent):
        num_blocks = int(percent // 2)
        bar_length = 50
        progress = '|' + '■' * num_blocks + ' ' * (bar_length - num_blocks) + '|' + str(percent) + "%"
        print(f'\r {progress}', end='', flush=True)

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
                print("\n视频生成成功")
                src_attribute = video_element.evaluate('''element => element.getAttribute('src')''')
                percent = 100
                break
            else:
                # 获取文本内容
                element_locator = page.locator('.ProgressRing__CircleText-sc-1ed2gw0-3.jBjiPh')  # 使用你提供的类名选择器
                progress_text = None
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

    def run(self):
        # 使用 Playwright 执行操作
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            print("准备中...")
            page = browser.new_page()
            self.login(page)
            self.write_tips(page)
            self.commit_tips(page)

            href = self.loading(page)
            browser.close()
            return href


# 主函数
def main():
    config = configparser.ConfigParser()
    config.read('./config.ini')

    parser = argparse.ArgumentParser(description='命令行参数示例')
    # 添加参数选项
    parser.add_argument('-u', '--username', type=str, help='用户名')
    parser.add_argument('-p', '--password', type=str, help='密码')
    parser.add_argument('-t', '--tips', type=str, help='提示词')
    # 解析命令行参数
    args = parser.parse_args()
    username = args.username
    password = args.password
    tips = args.tips
    if username is None:
        username = config['Settings']['username']
    if password is None:
        password = config['Settings']['password']

    if tips is None:
        tips = config['Settings']['tips']
    if len(tips) < 256:
        print(f"当前提示词:\t{tips}")

    if username is None or username == '' \
            or password is None or password == '':
        print("账号密码无效")

    if tips is None or tips == '':
        print("请输入提示词")

    if not check_chromium_installed():
        print("初次使用,环境准备中")
        install_chromium()
        print("准备完成")

    download_link = RunWayParser(username, password).set_tips(tips).run()
    print("视频链接:", download_link)


if __name__ == "__main__":
    main()
