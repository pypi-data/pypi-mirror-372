import os
import re
import importlib
import traceback

import allure
import pytest
from box import Box
from framework.exit_code import ExitCode
from framework.utils.log_util import logger
from framework.global_attribute import CONTEXT
from framework.utils.common import SingletonFaker
from config.settings import FAKER_LANGUAGE, DATA_DIR

module = importlib.import_module("framework.utils.common")


class RenderData(object):
    def __init__(self, data):
        self.data = data
        self.request = data.get("request")
        try:
            self.scenario = Box(data.get("_scenario").get("data"))
        except AttributeError:
            self.scenario = dict()
        self.context = CONTEXT
        self.faker = SingletonFaker(locale=FAKER_LANGUAGE).faker
        self._is_multipart = False

    def render(self):
        """
        占位符赋值
        :return:
        """
        with allure.step("渲染数据"):
            self.replace_attribute(self.scenario)
            self.replace_attribute(self.request)
        self.data["request"] = self.request
        self.data["_is_multipart"] = self._is_multipart
        return self.data

    def replace_attribute(self, data):
        pattern = re.compile(r"\$\{([\w.\[\]0-9]+(?:\(\w*(?:,\w*)*\))?)}")
        file_path_pattern = re.compile(
            r'^(?:[^/\\]+\\)*[^/\\]+\.(txt|doc|docx|pdf|xls|xlsx|ppt|pptx|md|jpg|jpeg|png|gif|svg|webp|ico|mp4|avi|mov|wmv|flv|mkv|webm|mp3|exe)$')

        # 如果数据是字典类型，则遍历其键值对
        if isinstance(data, dict):
            for key, value in data.items():
                # 递归遍历嵌套的字典或列表
                if isinstance(value, (dict, list)):
                    self.replace_attribute(value)
                # 如果是字符串类型并匹配正则表达式，则替换
                elif isinstance(value, str):
                    if pattern.search(value):
                        data[key] = self.get_attribute(value[2:-1])
                    elif file_path_pattern.search(value):
                        data[key] = self.open_file_for_multipart(value)
                        self._is_multipart = True

        # 如果数据是列表类型，则遍历其元素
        elif isinstance(data, list):
            for index, item in enumerate(data):
                # 递归遍历嵌套的字典或列表
                if isinstance(item, (dict, list)):
                    self.replace_attribute(item)
                # 如果是字符串类型并匹配正则表达式，则替换
                elif isinstance(item, str):
                    if pattern.search(item):
                        data[index] = self.get_attribute(item[2:-1])
                    elif file_path_pattern.search(item):
                        data[index] = self.open_file_for_multipart(item)
                        self._is_multipart = True

    def get_attribute(self, keyword):
        if not keyword.endswith(")"):
            return self.get_attribute_variable(keyword)
        # 如果关键字是函数
        else:
            pattern = re.compile(r'(?P<func_name>.+)\((?P<args>.*)\)')
            match = re.match(pattern, keyword)
            # 匹配方法名
            func_name = match.group("func_name")
            # 匹配方法位置参数
            args = match.group("args")
            if args:
                # 将参数中字符串类型的数字转成数字类型
                args = [eval(i) for i in args.replace(",", "").split(",")]
                return self.get_func_variable(keyword, func_name, *args)
            else:
                return self.get_func_variable(keyword, func_name)

    def get_attribute_variable(self, expression):
        """
        去全局上下文中获取value并进行替换
        :param expression:
        :return:
        """
        if not expression.startswith(tuple(f"{app}." for app in self.context.all_app)):
            belong_app = self.data.get('_belong_app')
            new_expression = f"{belong_app}.{expression}"
        else:
            new_expression = expression
        value = (
            self.get_nested_value(self.scenario, expression)
            if self.get_nested_value(self.scenario, expression) is not None else
            self.get_nested_value(self.context, new_expression)
            if self.get_nested_value(self.context, new_expression) is not None else
            self.get_nested_value(self.context, expression)
        )
        # if value.endswith(")}"):
        #     keyword = value[2:-1]
        #     try:
        #         pattern = re.compile(r'(?P<func_name>.+)\((?P<args>.*)\)')
        #         match = re.match(pattern, keyword)
        #         # 匹配方法名
        #         func_name = match.group("func_name")
        #         # 匹配方法位置参数
        #         args = match.group("args")
        #         if args:
        #             # 将参数中字符串类型的数字转成数字类型
        #             args = [eval(i) for i in args.replace(",", "").split(",")]
        #             value = self.get_func_variable(keyword, func_name, *args)
        #         else:
        #             value = self.get_func_variable(keyword, func_name)
        #     except Exception:
        #         pass

        with allure.step(f"{expression}: {value}"):
            logger.info(f"前置读取变量: {expression}: {value}")
            return value

    def get_func_variable(self, keyword, func_name, *args):
        """
        去utils>common.py中或faker对象中执行对应的方法并进行替换
        :param keyword:
        :param func_name:
        :param args:
        :return:
        """
        try:
            value = getattr(module, func_name)(*args)
        except AttributeError:
            value = getattr(self.faker, func_name, None)(*args)

        if not value:
            logger.error(f"common.py文件或faker对象中不存在函数:{keyword}")
            traceback.print_exc()
            pytest.exit(ExitCode.FUNCTION_NOT_EXIST)
        else:
            with allure.step(f"{keyword}: {value}"):
                logger.info(f"前置读取函数: {keyword}: {value}")
                return value

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

    @staticmethod
    def open_file_for_multipart(filepath):
        f = open(os.path.join(DATA_DIR, "file", filepath), "rb")
        return os.path.basename(f.name), f, "application/octet-stream"
