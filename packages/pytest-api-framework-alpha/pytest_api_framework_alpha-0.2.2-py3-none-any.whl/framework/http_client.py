import re
from typing import List
from urllib.parse import urljoin

import allure
import requests
import json as built_json
from box import Box, BoxList
from jsonpath import jsonpath as jp
from requests.models import Response
from requests_toolbelt import MultipartEncoder

from framework.extract import Extract
from framework.validate import Validate
from framework.utils.log_util import logger
from framework.global_attribute import CONTEXT
from config.settings import CONSOLE_DETAILED_LOG
from framework.utils.common import convert_numbers_to_decimal


class ResponseUtil(object):
    def __init__(self, response: Response):
        self.response = response
        if isinstance(self.response.json(), dict):
            self.box = Box(convert_numbers_to_decimal(self.response.json()))
        elif isinstance(self.response.json(), list):
            self.box = BoxList(convert_numbers_to_decimal(self.response.json()))
        else:
            self.box = self.response.text

    def __getattr__(self, name):
        try:
            return getattr(self.box, name)
        except AttributeError:
            return getattr(self.response, name)

    def __str__(self):
        return self.text

    def jsonpath(self, expr, headers=False):
        """
        使用jsonpath语法从响应体中提取内容
        @param expr: jsonpath语法
        @param headers: 从响应头中提取内容
        @return:
        """
        result = jp(dict(self.response.headers), expr) if headers else jp(self.json(), expr)
        if result is False:
            return ""
        if len(result) == 1:
            return result[0]
        return result

    @property
    def jsonp(self):
        """返回json"""
        jsonp_re = re.compile(r".*?\((?P<text>.*)\)")
        return built_json.loads(jsonp_re.match(self.response.text).group("text"))

    def json(self):
        return self.response.json()

    def extract(self, app, key, expression):
        """
        进行变量提取
        :param app:
        :param key: 保存变量的名称
        :param expression: 提取变量表达式
        :return:
        """
        Extract(self.response, app).extract(key, expression)

    def extracts(self, app, expressions: List[dict]):
        """
        进行变量提取
        :param app:
        :param expressions: 提取变量表达式
        :return:
        """
        Extract(self.response, app).extracts(expressions)


class HttpClient(object):

    def __init__(self, headers=None):
        """

        @param headers: 请求头
        @param cookies: cookies
        """

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Content-Type": "application/json"
        }
        self.headers.update(headers or {})
        self.response = None

    def __send_request(self, data):
        _is_multipart = data.get("_is_multipart")
        request_obj = data.get("request")
        with allure.step("发送请求"):
            if _is_multipart:
                m = MultipartEncoder(fields=request_obj["data"])
                request_obj["data"] = m
                request_obj["headers"].update(self.headers)
                request_obj["headers"]['Content-Type'] = m.content_type
            else:
                request_obj["headers"].update(self.headers)
            self.response = ResponseUtil(requests.request(**request_obj))

            with allure.step(f"请求url: {request_obj.get('url')}"):
                logger.info(f"请求url: {request_obj.get('url')}")
            with allure.step(f"请求method: {request_obj.get('method')}"):
                logger.info(f"请求method: {request_obj.get('method')}")
            with allure.step(f"请求headers: {request_obj.get('headers')}"):
                if CONSOLE_DETAILED_LOG:
                    logger.info(f"请求headers: {request_obj.get('headers')}")
            if request_obj.get('params'):
                with allure.step(f"请求参数params: {request_obj.get('params')}"):
                    logger.info(f"请求参数params: {request_obj.get('params')}")
            if request_obj.get('data'):
                with allure.step(f"请求参数data: {request_obj.get('data')}"):
                    logger.info(f"请求参数data: {request_obj.get('data')}")
            if request_obj.get('json'):
                with allure.step(f"请求参数json: {request_obj.get('json')}"):
                    logger.info(f"请求参数json: {request_obj.get('json')}")

        with allure.step("响应结果"):
            with allure.step(f"响应status code: {self.response.status_code}"):
                logger.info(f"响应status code: {self.response.status_code}")
            with allure.step(f"响应headers: {self.response.headers}"):
                if CONSOLE_DETAILED_LOG:
                    logger.info(f"响应headers: {self.response.headers}")
            with allure.step(f"响应body: {self.response.json()}"):
                logger.info(f"响应body: {self.response.json()}")

        # 断言
        validates = data.get("validate")
        if validates:
            with allure.step("结果断言"):
                Validate(self.response).valid(validates)

        # 提取变量
        expressions = data.get("extract")
        belong_app = data.get("_belong_app")
        if expressions:
            with allure.step("提取变量"):
                Extract(self.response, belong_app).extracts(expressions)

        return self.response

    def request(self, data, **kwargs):
        if data:
            return self.__send_request(data)

        return ResponseUtil(requests.request(headers=self.headers, **kwargs))

    def post(self, app, url, data=None, json=None, **kwargs):
        return self.request(method="post", url=urljoin(CONTEXT.get(app=app, key="domain"), url), data=data,
                            json=json, **kwargs)

    def get(self, app, url, params=None, **kwargs):
        return self.request(method="get", url=urljoin(CONTEXT.get(app=app, key="domain"), url), params=params,
                            **kwargs)

    def put(self, app, url, data=None, **kwargs):
        return self.request(method="put", url=urljoin(CONTEXT.get(app=app, key="domain"), url), data=data,
                            **kwargs)

    def delete(self, app, url, **kwargs):
        return self.request(method="delete", url=urljoin(CONTEXT.get(app=app, key="domain"), url), **kwargs)

    def update_headers(self, headers):
        self.headers.update(headers)
