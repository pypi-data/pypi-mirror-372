import json
import base64
import hashlib

from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES, DES, DES3, PKCS1_v1_5 as PKCS1_cipher
from framework.utils.common import valid_hex_format, valid_b64_format, hex_to_bytes, bytes_to_hex


def md5(string, byte=False, encoding="utf-8"):
    """

    :param string: 加密内容
    :param byte: 返回字节类型，默认返回16进制
    :param encoding: 编码
    :return: 返回字符串
    """
    md_obj = hashlib.md5()
    if isinstance(string, str):
        string = string.encode(encoding=encoding)
    md_obj.update(string)
    if byte:
        return md_obj.digest()
    return md_obj.hexdigest()


def sha(str_list, mode, byte=False, length=None, encoding="utf-8"):
    """

    :param str_list: 加密内容，字节或字符串
    :param mode: sha系列加密方式
    :param byte: 返回字节类型，默认返回16进制
    :param length: 'shake_128', 'shake_256'需要指定返回的长度
    :param encoding:  编码
    :return: 返回字符串
    """
    sha_obj = hashlib.new(mode)
    if not isinstance(str_list, list):
        raise Exception(f"{str_list} 必须是list类型")
    for i in str_list:
        if not isinstance(i, (str, bytes)):
            raise Exception(f"{i} 必须是str或bytes类型")
        if isinstance(i, str):
            i = i.encode(encoding=encoding)
        sha_obj.update(i)

    if mode in ['shake_128', 'shake_256']:
        if byte:
            return sha_obj.digest(length)
        return sha_obj.hexdigest(length)
    else:
        if byte:
            return sha_obj.digest()
        return sha_obj.hexdigest()


def b64_encode(bs, byte=False, encoding="utf-8"):
    """
    bytes -> b64字符串
    :param bs: 二进制字节串
    :param byte: 返回二进制字节或b64字符串，默认b64字符串
    :param encoding:
    :return:
    """
    if not isinstance(bs, bytes):
        raise Exception(f"{bs} 必须是bytes类型")
    if byte:
        return base64.b64encode(bs)
    return base64.b64encode(bs).decode(encoding)


def b64_decode(string, byte=True, encoding="utf-8"):
    """
    b64字符串 -> bytes
    :param string:  b64字符串
    :param byte: 返回二进制字节或字符串，默认返回二进制字节
    :param encoding:
    :return:
    """
    if not isinstance(string, str):
        raise Exception(f"{string} 必须是b64字符串")

    missing_padding = 4 - len(string) % 4
    if missing_padding:
        string += '=' * missing_padding
    if byte:
        return base64.b64decode(string)
    return base64.b64decode(string).decode(encoding=encoding)


class RsaByPubKey(object):

    def __init__(self, pub_key):
        """
        :param pub_key: 公钥
               1.可以直接传公钥的base64字符串；
               2.通过save_publish_key方法先将公钥的base64字符串存到文件，然后使用get_publish_key方法读取文件获取公钥,然后传入
        """
        self.pub_key = pub_key

    def encrypt(self, data, b64=False, encoding="utf-8"):
        """

        :param data: 要加密的数据
        :param b64: 默认返回16进制字符串,True返回base64字符
        :param encoding:
        :return:
        """

        if valid_hex_format(self.pub_key):
            self.pub_key = hex_to_bytes(self.pub_key)

        elif valid_b64_format(self.pub_key):
            self.pub_key = b64_decode(self.pub_key)

        else:
            raise Exception("pub_key参数必须是16进制字符串或b64字符串")

        if not isinstance(data, bytes):
            data = data.encode(encoding=encoding)
        cipher = PKCS1_cipher.new(RSA.import_key(self.pub_key))
        encrypt_text = cipher.encrypt(data)
        if b64:
            return b64_encode(cipher.encrypt(data))  # 转成base64字符串
        return bytes_to_hex(encrypt_text).decode(encoding=encoding)  # 转成base64字符


class Aes(object):
    AES_MODE_MAP = {
        "CBC": AES.MODE_CBC,
        "ECB": AES.MODE_ECB,
        "CFB": AES.MODE_CFB,
        "OFB": AES.MODE_OFB,
        "CTR": AES.MODE_CTR,
        "OPENPGP": AES.MODE_OPENPGP,
        "CCM": AES.MODE_CCM,
        "EAX": AES.MODE_EAX,
        "SIV": AES.MODE_SIV,
        "GCM": AES.MODE_GCM,
        "OCB": AES.MODE_OCB
    }

    def __init__(self, key, mode, iv=None, encoding="utf-8"):
        """

        :param key: 必须是16 or 24 or 32字节长度
        :param mode:
        :param iv: 必须是16位字节
        :param encoding:
        """
        self.iv = iv
        self.key = key
        self.mode = mode.upper()
        self.encoding = encoding
        if self.mode in ["CBC", "CFB", "OFB"]:
            if not self.iv or len(self.iv) != 16:
                raise Exception(f"{iv} 必须是16字节长度")

        if len(self.key) not in [16, 24, 32]:
            raise Exception(f"{self.key} 必须是16、24或32字节长度")

        if not isinstance(self.key, bytes):
            self.key = self.key.encode(encoding=self.encoding)

        if self.iv:
            if not isinstance(self.iv, bytes):
                self.iv = self.iv.encode(encoding=self.encoding)
        self.mode = self.AES_MODE_MAP.get(mode)

    def new_aes(self):
        if self.iv:
            return AES.new(key=self.key, mode=self.mode, IV=self.iv)
        return AES.new(key=self.key, mode=self.mode)

    def encrypt(self, data, byte=False, separate=False):
        """
        字符串/字节->加密->b64字符串
        :param data: 加密内容，字节或者字符串，如果是字符串，默认转为字节
        :param byte: 返回b64字符或字节，默认返回b64字符
        :param separate: 序列化时是否需要:，,后面的空格，默认不需要
        :return:b64字符串
        """

        aes_obj = self.new_aes()
        if isinstance(data, dict):
            if separate:
                data = json.dumps(data, separators=(',', ':')).encode(encoding=self.encoding)
            else:
                data = json.dumps(data).encode(encoding=self.encoding)
        else:
            data = str(data).encode(encoding=self.encoding)
        data = pad(data, 16)
        if byte:
            return aes_obj.encrypt(data)
        return b64_encode(aes_obj.encrypt(data))

    def decrypt(self, data, byte=False):
        """
        b64字符串->解密->字符串/字节
        :param data: 解密内容，字节或者字符串,如果是字符串，转为b64字节
        :param byte: 返回字符串或字节，默认字符串
        :return:
        """
        aes_obj = self.new_aes()
        if not isinstance(data, bytes):
            data = b64_decode(data)
        if byte:
            return unpad(aes_obj.decrypt(data), 16)
        try:
            return json.loads(unpad(aes_obj.decrypt(data), 16).decode(encoding=self.encoding))
        except Exception:
            return unpad(aes_obj.decrypt(data), 16).decode(encoding=self.encoding)


class Des(object):
    DES_MODE_MAP = {
        "CBC": DES.MODE_CBC,
        "ECB": DES.MODE_ECB,
        "CFB": DES.MODE_CFB,
        "OFB": DES.MODE_OFB,
        "CTR": DES.MODE_CTR,
        "OPENPGP": DES.MODE_OPENPGP,
        "EAX": DES.MODE_EAX
    }

    def __init__(self, key, mode, iv=None, encoding="utf-8"):
        """

        :param key: 必须是8位字节
        :param mode:
        :param iv: 必须是8位字节
        :param encoding:
        """
        self.iv = iv
        self.key = key
        self.mode = mode.upper()
        self.encoding = encoding
        if self.mode in ["CBC", "CFB", "OFB"]:
            if not self.iv or len(self.iv) != 8:
                raise Exception(f"{self.iv} 必须是8字节长度")

        if len(self.key) != 8:
            raise Exception(f"{self.key} 必须是8字节长度")

        if not isinstance(self.key, bytes):
            self.key = self.key.encode(encoding=self.encoding)

        if self.iv:
            if not isinstance(self.iv, bytes):
                self.iv = self.iv.encode(encoding=self.encoding)

        self.mode = self.DES_MODE_MAP.get(mode)

    def new_des(self):
        if self.iv:
            return DES.new(key=self.key, mode=self.mode, IV=self.iv)
        return DES.new(key=self.key, mode=self.mode)

    def encrypt(self, data, byte=False, separate=False):
        """
        :param data: 加密内容，字节或者字符串,如果是字符串，默认转为字节
        :param byte: 返回base64字符或字节，默认返回base64字符
        :param separate: 序列化时是否需要:，,后面的空格，默认不需要
        :return:
        """
        des_obj = self.new_des()
        if isinstance(data, dict):
            if separate:
                data = json.dumps(data, separators=(',', ':')).encode(encoding=self.encoding)
            else:
                data = json.dumps(data).encode(encoding=self.encoding)
        else:
            data = str(data).encode(encoding=self.encoding)
        data = pad(data, 8)
        if byte:
            return des_obj.encrypt(data)
        return b64_encode(des_obj.encrypt(data))

    def decrypt(self, data, byte=False):
        """

        :param data: 解密内容，字节或者字符串,如果是字符串，默认转为base64字符
        :param byte: 返回字符串或字节，默认字符串
        :return:
        """
        des_obj = self.new_des()
        if not isinstance(data, bytes):
            data = b64_decode(data)
        if byte:
            return unpad(des_obj.decrypt(data), 8)
        try:
            return json.loads(unpad(des_obj.decrypt(data), 8).decode(encoding=self.encoding))
        except Exception:
            return unpad(des_obj.decrypt(data), 8).decode(encoding=self.encoding)


class Des3(object):
    DES3_MODE_MAP = {
        "CBC": DES3.MODE_CBC,
        "ECB": DES3.MODE_ECB,
        "CFB": DES3.MODE_CFB,
        "OFB": DES3.MODE_OFB,
        "CTR": DES3.MODE_CTR,
        "OPENPGP": DES3.MODE_OPENPGP,
        "EAX": DES3.MODE_EAX
    }

    def __init__(self, key, mode, iv=None, encoding="utf-8"):
        """

        :param key: 必须是16，24位字节
        :param mode:
        :param iv: 必须是8位字节
        :param encoding:
        """
        self.iv = iv
        self.key = key
        self.mode = mode.upper()
        self.encoding = encoding

        if self.mode in ["CBC", "CFB", "OFB"]:
            if not self.iv or len(self.iv) != 8:
                raise Exception(f"{self.iv} 必须是8字节长度")

        if len(self.key) not in [16, 24]:
            raise Exception(f"{self.key} 必须是16或24字节长度")

        if not isinstance(self.key, bytes):
            self.key = self.key.encode(encoding=self.encoding)

        if self.iv:
            if not isinstance(iv, bytes):
                self.iv = self.iv.encode(encoding=self.encoding)

        self.mode = self.DES3_MODE_MAP.get(mode)

    def new_des3(self):
        if self.iv:
            return DES3.new(key=self.key, mode=self.mode, IV=self.iv)
        return DES3.new(key=self.key, mode=self.mode)

    def encrypt(self, data, byte=False, separate=False):
        """
        :param data: 加密内容，字节或者字符串,如果是字符串，默认转为字节
        :param byte: 返回base64字符或字节，默认返回base64字符
        :param separate: 序列化时是否需要:，,后面的空格，默认不需要
        :return:
        """
        des3_obj = self.new_des3()
        if isinstance(data, dict):
            if separate:
                data = json.dumps(data, separators=(',', ':')).encode(encoding=self.encoding)
            else:
                data = json.dumps(data).encode(encoding=self.encoding)
        else:
            data = str(data).encode(encoding=self.encoding)
        data = pad(data, 8)
        if byte:
            return des3_obj.encrypt(data)
        else:
            return b64_encode(des3_obj.encrypt(data))

    def decrypt(self, data, byte=False):
        """

        :param data: 解密内容，字节或者字符串,如果是字符串，默认转为base64字符
        :param byte: 返回字符串或字节，默认字符串
        :return:
        """
        des3_obj = self.new_des3()
        if not isinstance(data, bytes):
            data = b64_decode(data)
        if byte:
            return unpad(des3_obj.decrypt(data), 8)
        else:
            try:
                return json.loads(unpad(des3_obj.decrypt(data), 8).decode(encoding=self.encoding))
            except Exception:
                return unpad(des3_obj.decrypt(data), 8).decode(encoding=self.encoding)


if __name__ == '__main__':
    key = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCqJA8yliEYgp9aorMNzayIyJex4ukgwEXi+Us2xVJlttB2Uy9Bsh9ugTqNcc1bf7R5WW/QIN/EbA+yJC1FCqZHzZdYw54O+IN9oV9I+pE2ziK6vlOjUYmKbi2NO84xAYW83uaWee6MkH8m87qn5hrd7JzksPJS3HdHNZCcOOOemwIDAQAB"
    rsa = RsaByPubKey(pub_key=key)
    a = rsa.encrypt(test_data="password", b64=True)
    print(a)
