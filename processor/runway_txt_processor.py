import time
from processor.runway_abstract_processor import RunWayAbstractParser


class RunWayTxtParser(RunWayAbstractParser):

    def write(self, page):
        """
        提交提示词
        :param page:
        :return:
        """
        page.goto(self.GEN_PATH, wait_until="domcontentloaded")
        seconds = self.get_seconds(page)
        print(self.name + "当前余额:", seconds)
        print(self.name + "开始提交提示词")
        page.wait_for_selector('button.Button-sc-c1bth8-0')
        text_input = page.locator('textarea[aria-label="Text Prompt Input"]')
        text_input.fill(self.content)
        return True

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
