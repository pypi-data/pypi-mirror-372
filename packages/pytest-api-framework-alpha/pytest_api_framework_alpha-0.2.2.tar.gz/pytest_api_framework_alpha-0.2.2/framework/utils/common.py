import decimal
import re
import os
import time
import binascii
from typing import Any
from decimal import Decimal
from datetime import datetime
from urllib.parse import unquote, quote, quote_plus, unquote_plus

import pyotp
import cn2an as c2a
from faker import Faker

from config.settings import CONFIG_DIR


def generate_2fa_code(secret_key):
    """
    获取2fa code
    :return:
    """
    current_time = int(time.time())
    totp = pyotp.TOTP(secret_key)
    google_code = totp.at(current_time)

    return google_code


def is_digit(string):
    """判断是否为数字字符串"""
    digit_re = re.compile(r'^-?[0-9.]+$')
    return digit_re.search(string)


def an2cn(integer):
    """阿拉伯数字转中文数字"""
    return c2a.an2cn(integer)


def cn2an(string):
    """中文数字转阿拉伯数字"""
    return c2a.cn2an(string)


def clean_symbol(text):
    """
    清除字符串特殊符号
    :param text:
    :return:
    """
    return re.sub('[’!"#$`%&\'：|*+～·,-./:;<=「」>@，。?★、…—？“”‘！[\\]^_{}~]+', "", text)


def get_long_timestamp(int_type=False):
    """
    获取毫秒级时间戳
    :param int_type: 默认返回str类型
    :return:
    """

    if int_type:
        return int(time.time() * 1000)
    return str(int(time.time() * 1000))


def get_short_timestamp(int_type=False):
    """
    获取秒级时间戳
    :param int_type: 默认返回str类型
    :return:
    """
    if int_type:
        return int(time.time())
    return str(int(time.time()))


def get_current_datetime():
    """
    获取当前日期和时间 2023-02-19 08:31:51
    :return:
    """
    return time.strftime("%Y-%m-%d %X")


def get_current_date():
    """
    获取当前日期 2023-02-19
    :return:
    """
    return time.strftime("%Y-%m-%d")


def timestamp2datetime(timestamp):
    """
    时间戳转日期时间
    @param timestamp:
    @return:
    """
    if isinstance(timestamp, int):
        timestamp = str(timestamp)
    timestamp = timestamp[:10]
    return datetime.fromtimestamp(int(timestamp))


def timestamp2date(timestamp):
    """
    时间戳转日期
    @param timestamp:
    @return:
    """
    if isinstance(timestamp, int):
        timestamp = str(timestamp)
    timestamp = timestamp[:10]
    return time.strftime("%Y-%m-%d", time.localtime(int(timestamp)))


def valid_hex_format(s):
    """
    判断是否为16进制字符串
    :param s:
    :return:
    """
    hex_re = re.compile(r"^[0-9a-fA-F]+$")
    if hex_re.match(s):
        return True
    return False


def valid_b64_format(s):
    """
    判断是否为base64字符串
    :param s:
    :return:
    """
    b64_re = re.compile(r"^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$")
    if b64_re.match(s):
        return True
    return False


def hex_to_bytes(hex_str):
    """
    16进制->字节
    :param hex_str:
    :return:
    """
    return binascii.a2b_hex(hex_str).strip()


def bytes_to_hex(byte):
    """
    字节->16进制
    :param byte:
    :return:
    """
    return binascii.b2a_hex(byte)


def url_encode(string, use_quote_plus=False, encoding="utf-8"):
    """
    url编码
    :param string:
    :param use_quote_plus: 是否使用quote_plus编码
    :param encoding: 编码格式
    :return:
    """
    if use_quote_plus:
        return quote_plus(string, encoding=encoding)
    return quote(string, encoding=encoding)


def url_decode(string, use_unquote_plus=False, encoding="utf-8"):
    """
    url解码
    :param string:
    :param use_unquote_plus: 是否使用unquote_plus解码
    :param encoding: 编码格式
    :return:
    """
    if use_unquote_plus:
        return unquote_plus(string, encoding=encoding)
    return unquote(string, encoding=encoding)


def singleton(cls):
    """
    单例模式装饰器
    :param cls:
    :return:
    """
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


def snake_to_pascal(name: str) -> str:
    # 将字符串按照下划线分割，然后将每个单词的首字母大写，最后连接起来
    return ''.join(word.capitalize() for word in name.split('_'))


def get_apps():
    """
    获取所有app
    """
    return [name for name in os.listdir(CONFIG_DIR) if
            os.path.isdir(os.path.join(CONFIG_DIR, name)) and not name.startswith(("__", "."))]


# 匹配合法数字字符串（可含千分位）
decimal_pattern = re.compile(r'^\d{1,3}(,\d{3})*(\.\d+)?$|^\d+(\.\d+)?$')


def convert_numbers_to_decimal(obj: Any) -> Any:
    if isinstance(obj, str):
        if decimal_pattern.match(obj):
            int_part = obj.split('.')[0]
            if len(int_part) > 10 and "," not in int_part:
                return obj  # 整数部分超过10位，不转换
            try:
                stripped = obj.replace(",", "")
                return Decimal(stripped)
            except Exception:
                return obj
        else:
            return obj
    elif isinstance(obj, dict):
        return {k: convert_numbers_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numbers_to_decimal(item) for item in obj]
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        # 处理原生数值类型
        int_part = str(obj).split('.')[0]
        if len(int_part) > 10:
            return obj  # 整数部分超过10位，不转换
        return Decimal(str(obj))
    else:
        return obj


class SingletonFaker(object):
    instance = None
    init_flag = False

    def __init__(self, locale):
        if self.init_flag:
            return
        self.faker = Faker(locale)

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance


if __name__ == '__main__':
    a = decimal.Decimal("123")
    print(a)
    assert a == 123
