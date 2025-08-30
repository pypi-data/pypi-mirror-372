import os
import sys
import random
import string
import uuid
import hashlib
from datetime import datetime
from .aes_crypto import *
from .gzip_crypto import *
from .rsa_crypto import *


def str_to_dt(date_string, format: str = "%Y-%m-%d %H:%M:%S"):
    return datetime.strptime(date_string, format)


def dt_to_str(dt, format: str = "%Y-%m-%d %H:%M:%S"):
    return dt.strftime(format)


def dt_to_str_now(format: str = "%Y-%m-%d %H:%M:%S"):
    return dt_to_str(datetime.now(), format)


def check_any_in_string(check_set: set, str: str):
    return any(item in str for item in check_set)


def check_none_in_string(check_set: set, str: str):
    return all(item.lower() not in str for item in check_set)


def generate_md5_guid():
    # 生成一个 GUID
    guid = uuid.uuid4()

    # 将 GUID 转换为字符串格式并去掉连字符
    guid_str = guid.hex

    # 计算 GUID 的 MD5 哈希值
    md5_hash = hashlib.md5(guid_str.encode()).hexdigest()

    # 取前 16 位并转换为大写
    md5_16_upper = md5_hash[:16].upper()

    return md5_16_upper


def generate_string(length: int = 8) -> str:
    """
    生成随机字符串
    :param length: 字符串长度
    """
    return "".join(random.sample(string.ascii_letters + string.digits, length))