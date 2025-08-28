from enum import Enum


class ExitCode(Enum):
    ENV_NOT_EXIST = 10001  # 测试环境不存在
    APP_NOT_EXIST = 10002  # 测试系统不存在
    CONTEXT_YAML_NOT_EXIST = 10003  # 未获取到全局配置文件
    CONTEXT_YAML_DATA_FORMAT_ERROR = 10004  # 全局配置文件格式不正确
    CASE_YAML_NOT_EXIST = 10005  # 未获取到对应的YAML测试数据文件
    CASE_DATA_NOT_EXIST = 10006  # 未获取到用例对应测试数据
    GLOBAL_ATTRIBUTE_NOT_EXIST = 10007  # 未从CONTEXT中获取到对应变量
    FUNCTION_NOT_EXIST = 10008  # 未从common.py中或faker对象中获取到对应函数
    EXTRACT_KEY_NOT_EXIST = 10009  # 未从响应中提取到指定变量
    LOGIN_ERROR = 10010  # 系统登录失败
    YAML_MISSING_FIELDS = 10011  # 缺少必填字段
    MISSING_ASSERTIONS = 10012  # 缺少断言
    APP_OR_ACCOUNT_NOT_EXIST = 10013  # 账号角色不存在
    MORE_THAN_ONE_TEST_SUITE_SETUP = 10014  # test_suite_setup标签只能配置一个
    LOAD_DATABASE_INFO_ERROR = 10015
