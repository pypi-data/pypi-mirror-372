import re
import traceback
from typing import List

import allure
import pytest
from box import Box, BoxList
from jsonpath import jsonpath

from framework.exit_code import ExitCode
from framework.utils.common import is_digit
from framework.utils.log_util import logger
from framework.global_attribute import CONTEXT


class Extract(object):
    def __init__(self, response, belong_app):
        if isinstance(response.json(), dict):
            self.response = Box(response.json())
        elif isinstance(response.json(), list):
            self.response = BoxList(response.json())
        else:
            self.response = response
        self.belong_app = belong_app
        self.context = CONTEXT

    def extracts(self, expressions: List[dict]):
        for item in expressions:
            key = list(item.keys())[0].strip()
            expression = item.get(key).strip()
            try:
                # jsonpath表达式
                if expression.lower().startswith("$."):
                    self.extract_by_jsonpath(key, expression)
                # 正则表达式
                elif expression.startswith("/") and expression.endswith("/"):
                    self.extract_by_regex(key, expression[1: -1])
                # box句点表达式
                else:
                    self.extract_by_box(key, expression)

            except Exception as e:
                with allure.step(f"后置提取变量{key}失败, 失败原因: {e}"):
                    logger.error(f"后置提取变量{key}失败, 失败原因: {e}")
                    traceback.print_exc()
                    pytest.exit(ExitCode.EXTRACT_KEY_NOT_EXIST)

    def extract(self, key, expression):
        return self.extracts([{key.strip(): expression.strip()}])

    def extract_by_jsonpath(self, key, expression):
        try:
            if key.startswith(tuple(f"{app}." for app in self.context.all_app)):
                self.belong_app, key = key.split(".", 1)

            extract_value = jsonpath(self.response, expression)[0]
            with allure.step(f"后置提取变量: {key}: {extract_value}"):
                self.context.set(key, extract_value, self.belong_app)
                logger.info(f"后置提取变量: {key}: {extract_value}")

        except Exception as e:
            logger.error(f"jsonpath表达式错误或响应内容异常{e} 表达式: {expression};响应内容: {self.response}")
            logger.error(f"后置提取变量{key}失败")

    def extract_by_regex(self, key, reg_expression):
        try:
            if key.startswith(tuple(f"{app}." for app in self.context.all_app)):
                self.belong_app, key = key.split(".", 1)
            extract_value = re.search(reg_expression, self.response.text, flags=re.S).group()
            with allure.step(f"后置提取变量: {key}: {extract_value}"):
                if is_digit(extract_value):
                    self.context.set(key, eval(extract_value), self.belong_app)
                else:
                    self.context.set(key, extract_value, self.belong_app)
                logger.info(f"后置提取变量: {key}: {extract_value}")

        except Exception as e:
            logger.error(f"正则表达式或响应内容异常{e} 表达式: {reg_expression}; 响应内容: {self.response.text}")
            logger.error(f"后置提取变量{key}失败")

    def extract_by_box(self, key, expression):
        if key.startswith(tuple(f"{app}." for app in self.context.all_app)):
            self.belong_app, key = key.split(".", 1)
        extract_value = self.get_nested_value(Box(self.response), expression)
        if not extract_value:
            logger.error(f"box表达式或响应内容异常 表达式: {expression}; 响应内容: {self.response}")
            logger.error(f"后置提取变量{key}失败")
        else:
            with allure.step(f"后置提取变量: {key}: {extract_value}"):
                self.context.set(key, extract_value, self.belong_app)
                logger.info(f"后置提取变量: {key}: {extract_value}")

    @staticmethod
    def get_nested_value(obj, attr_path):
        """通过字符串路径（如 'a.b[0].c'）获取嵌套属性值"""
        # 使用正则表达式分解路径，支持属性和索引的组合
        path_elements = re.findall(r'(\w+)|\[(\d+)]', attr_path)
        try:
            for attr, index in path_elements:
                if attr:  # 属性部分
                    obj = getattr(obj, attr)
                if index:  # 索引部分
                    obj = obj[int(index)]
            return obj
        except Exception:
            return None
