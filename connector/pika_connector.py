from connector.base_connector import BaseConnector
from entity.result_utils import ResultDo
from entity.task_status import Status

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
            raise Exception(ResultDo(resp.get('code'), resp.get('message')))
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
            raise Exception(ResultDo(resp.get('code'), resp.get('message')))
        return resp.get('data')


def main():
    pika_connector = PikaConnector()
    fetch_data = pika_connector.fetch(1)
    task_id = fetch_data[0]['task_id']
    data = pika_connector.callback({"task_id": task_id, "progress": 1, "status": Status.DOING.value})


if __name__ == "__main__":
    main()
