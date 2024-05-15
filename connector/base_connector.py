import hashlib
import time
import requests
import configparser
from entity.error_code import ErrorCode
from entity.result_utils import ResultDo
import os
from logger_config import logger

from common.custom_exception import CustomException
import oss2
from oss2 import SizedFileAdapter
from settings import PROJECT_ROOT

'''
针对下面服务器接口的基类
https://ct4.dianbaobao.com
'''


class BaseConnector:

    def __init__(self):
        current_dir = os.path.dirname(__file__)
        project_root = os.path.abspath(os.path.join(current_dir, ".."))
        config = configparser.ConfigParser(interpolation=None)
        config.read(project_root + '/config.ini')
        self.__base_url = config['DIAN_BAOBAO']['base_url']
        self.__private_key = config['DIAN_BAOBAO']['private_key']
        self.__partner_id = config['DIAN_BAOBAO']['partner_id']
        pass

    @staticmethod
    def __generate_md5_signature(timestamp, params, private_key):
        """
        生成签名
        :param timestamp: 时间戳
        :param params: 参数
        :param private_key: 私钥
        :return:
        """
        if params is None:
            params = {}
        sorted_params = sorted(params.items(), key=lambda x: x[0])

        param_str_parts = []
        for key, value in sorted_params:
            if value is not None and value != '':
                param_str_parts.append(f"{key}={str(value)}")

        param_str = "&".join(param_str_parts)

        param_str += f"{timestamp}{private_key}"
        param_str = param_str.lower()
        logger.debug("签名数据:" + param_str)
        md5_hash = hashlib.md5(param_str.encode()).hexdigest()
        return md5_hash

    def post(self, uri, payload):
        logger.debug("-" * 50)
        url = self.__base_url + uri
        logger.debug("请求地址:{}", url)
        timestamp = str(int(time.time()))
        p = self.__private_key
        signature = self.__generate_md5_signature(timestamp, payload, p)
        # 构建请求头
        headers = {
            "Content-Type": "application/json",
            "x-timestamp": timestamp,
            "x-pid": self.__partner_id,
            "x-sign": signature
        }
        logger.debug("请求header:{}", headers)
        logger.debug("请求参数:{}", payload)
        response = requests.post(url, headers=headers, json=payload)
        data = response.text
        logger.debug("请求响应:{}", data)
        logger.debug("-" * 50)
        if response.status_code != 200:
            raise CustomException(ErrorCode.ERR_DIAN_BAOBAO, "服务器错误:" + data)
        data = response.json()
        return data

    def upload(self, file_name):
        config = configparser.ConfigParser(interpolation=None)
        config.read(PROJECT_ROOT + '/config.ini')

        access_key_id = config['ALI_YUN']['access_key_id']
        access_key_secret = config['ALI_YUN']['access_key_secret']
        bucket_name = config['ALI_YUN']['bucket_name']
        endpoint = config['ALI_YUN']['endpoint']
        directory = config['ALI_YUN']['directory']
        oss_url = config['ALI_YUN']['oss_url']
        auth = oss2.Auth(access_key_id, access_key_secret)
        bucket = oss2.Bucket(auth, endpoint, bucket_name)

        key = f'{directory}/{file_name}'
        local_file_path = f'resource/videos/{file_name}'
        try:
            with open(local_file_path, 'rb') as fileobj:
                put_result = bucket.put_object(key, SizedFileAdapter(fileobj, os.path.getsize(local_file_path)))
        except Exception as e:
            logger.error("上传出错", e)
            raise CustomException(ErrorCode.TIME_OUT, '上传出错')
        if put_result.status == 200:
            return f'{oss_url}/{directory}/{file_name}'
