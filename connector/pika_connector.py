from connector.base_connector import BaseConnector
from entity.result_utils import ResultDo
from entity.task_status import Status
from common.custom_exception import CustomException


class PikaConnector(BaseConnector):
    def fetch(self, _num):
        """
        获取任务
        :param num: 任务数量
        :return
        [
            {
                "task_id": "1", //任务ID
                "make_type": "text", //生成方式：text文本生成，image图片生成，mix图文
                "prompt": "女孩打篮球", //提示词
                "image_url": null //图片地址
            }
        ]
        """
        uri = '/openapi/job/pika/fetch'
        payload = {
            "num": _num
        }
        resp = self.post(uri, payload)
        if resp.get('code') != 0:
            raise CustomException(resp.get('code'), resp.get('message'))
        return resp.get('data')

    def callback(self, payload: dict):
        """
        任务回写
        request payload:
            {
                "task_id": "1",
                "progress": 95,
                "status": 1,
                "errcode": 0,
                "errmsg": "",
                "video_url": ""
            }
        response:
         None
        """

        uri = '/openapi/job/pika/callback'

        resp = self.post(uri, payload)
        if resp.get('code') != 0:
            raise CustomException(resp.get('code'), resp.get('message'))
        return resp.get('data')

    def fetch_accounts(self, worker_id):
        website = "pika"
        uri = f'/openapi/account/{website}/fetch'
        payload = {
            'worker_id': worker_id
        }
        resp = self.post(uri, payload)
        if resp.get('code') != 0:
            raise CustomException(resp.get('code'), resp.get('message'))
        return resp.get('data')

    def callback_account(self, payload):
        """
        {
            "account_no": "account001", //账号
            "status": 9, //1状态正常可用，5状态异常（如果账号不能登陆等未知情况），9账号停用（余额不足，账号被封）
            "balance": 0, //余额，状态为1时该值有效
            "reason": "余额不足" //账号不可用的原因，状态为5或9时，该值有效
        }
        :param payload:
        :return:
        """
        website = "pika"
        uri = f'/openapi/account/{website}/fetch'

        resp = self.post(uri, payload)
        if resp.get('code') != 0:
            raise CustomException(resp.get('code'), resp.get('message'))
        return resp.get('data')


def main():
    pika_connector = PikaConnector()
    data = pika_connector.fetch_accounts('1')
    pass
    # fetch_data = pika_connector.fetch(1)
    # task_id = fetch_data[0]['task_id']
    # data = pika_connector.callback({"task_id": task_id, "progress": 1, "status": Status.DOING.value})


if __name__ == "__main__":
    main()
