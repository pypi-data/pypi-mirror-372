import re
import datetime
from typing import Annotated
from pydantic import AfterValidator, PlainSerializer, WithJsonSchema

forbidden_keywords = [
    # 系统关键字
    "admin",
    "administrator",
    "root",
    "sysadmin",
    "superuser",
    "support",
    "system",
    "helpdesk",
    "webmaster",
    "moderator",
    "owner",
    "security",
    "rootadmin",
    # 通用禁用词
    "password",
    "user",
    "username",
    "guest",
    "test",
    "login",
    "register",
    "account",
    "profile",
    "anonymous",
    # 敏感词汇
    "sex",
    "porn",
    "violence",
    "drugs",
    "racist",
    "hate",
    "terror",
    "abuse",
    "slut",
    "bitch",
    "fuck",
    "shit",
    "damn",
    "whore",
    "cunt",
    "nigger",
    "faggot",
    "kike",
    "chink",
    "gook",
    "spic",
    "tranny",
    # 品牌和商标
    "google",
    "facebook",
    "apple",
    "microsoft",
    "amazon",
    "netflix",
    "twitter",
    "instagram",
    "youtube",
    "linkedin",
    "adobe",
    "ibm",
    "oracle",
    "intel",
    "samsung",
    "sony",
    "huawei",
    "xiaomi",
    "tencent",
    "baidu",
    "alibaba",
    # 特殊字符和空白字符
    "____",
    "....",
    "!!!!",
    " ",
    "***",
    "///",
    "\\\\\\",
    "###",
    "@@@",
    "$$$",
    "%%%",
    # 常见替代和变体
    "adm1n",
    "admln",
    "support1",
    "suрроrt",
    "moder@tor",
    "owner123",
    "secur1ty",
    "root_adm1n",
    "help_desk",
    "web_master",
    "guest_user",
    "test_account",
    "log1n",
    "reg1ster",
    "passw0rd",
    "pro_file",
    "anon_ymous",
]


def is_vali_password(value: str) -> str:
    """
    检测密码强度
    """
    if len(value) < 6 or len(value) > 16:
        raise ValueError("长度需为6-16个字符,请重新输入")
    else:
        for i in value:
            if 0x4E00 <= ord(i) <= 0x9FA5 or ord(i) == 0x20:
                raise ValueError("不能使用空格、中文,请重新输入")
        else:
            key = 0
            key += 1 if bool(re.search(r"\d", value)) else 0
            key += 1 if bool(re.search(r"[A-Za-z]", value)) else 0
            key += 1 if bool(re.search(r"\W", value)) else 0
            if key >= 2:
                return value
            else:
                raise ValueError("至少含数字/字母/字符2种组合,请重新输入")


def is_vali_username(value: str) -> str:
    """
    账号验证器
    :param value: 账号
    :return: 账号
    """
    pattern = r"^[a-zA-Z][a-zA-Z0-9]{1,11}$"
    if not re.match(pattern, value):
        raise ValueError("请输入正确账号")

    return value


def is_valid_name_add(value: str) -> str:
    # 检查用户名是否包含禁止关键字
    for keyword in forbidden_keywords:
        if keyword.lower() in value.lower():
            raise ValueError(f"账号包含非法字符:{keyword}")

    return value


def is_valid_username_add(value: str) -> str:
    # 正则表达式:用户名必须以字母开头,包含字母、数字、下划线或连字符,长度为3到11个字符
    pattern = r"^[a-zA-Z][a-zA-Z0-9]{1,11}$"
    if not re.match(pattern, value):
        raise ValueError("请输入正确账号")

    # 检查用户名是否包含禁止关键字
    for keyword in forbidden_keywords:
        if keyword.lower() in value.lower():
            raise ValueError(f"账号包含非法字符:{keyword}")

    return value


def is_vali_email(value: str) -> str:
    """
    邮箱地址验证器
    :param value: 邮箱
    :return: 邮箱
    """
    if not value:
        raise ValueError("请输入邮箱地址")

    regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not re.match(regex, value):
        raise ValueError("请输入正确邮箱地址")

    return value


def is_vali_datetime(value: str | datetime.datetime | int | float | dict | None):
    """
    日期时间字符串验证
    如果我传入的是字符串,那么直接返回,如果我传入的是一个日期类型,那么会转为字符串格式后返回
    因为在 pydantic 2.0 中是支持 int 或 float 自动转换类型的,所以我这里添加进去,但是在处理时会使这两种类型报错

    官方文档:https://docs.pydantic.dev/dev-v2/usage/types/datetime/
    """
    if isinstance(value, str):
        pattern = "%Y-%m-%d %H:%M:%S"
        try:
            datetime.datetime.strptime(value, pattern)
            return value
        except ValueError:
            pass
    elif isinstance(value, datetime.datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(value, dict):
        # 用于处理 mongodb 日期时间数据类型
        date_str = value.get("$date")
        date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        # 将字符串转换为datetime.datetime类型
        datetime_obj = datetime.datetime.strptime(date_str, date_format)
        # 将datetime.datetime对象转换为指定的字符串格式
        return datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
    return None


def is_vali_date(value: str | datetime.date | int | float):
    """
    日期字符串验证
    如果我传入的是字符串,那么直接返回,如果我传入的是一个日期类型,那么会转为字符串格式后返回
    因为在 pydantic 2.0 中是支持 int 或 float 自动转换类型的,所以我这里添加进去,但是在处理时会使这两种类型报错

    官方文档:https://docs.pydantic.dev/dev-v2/usage/types/datetime/
    """
    if isinstance(value, str):
        pattern = "%Y-%m-%d"
        try:
            datetime.datetime.strptime(value, pattern)
            return value
        except ValueError:
            pass
    elif isinstance(value, datetime.date):
        return value.strftime("%Y-%m-%d")
    raise ValueError("无效的日期时间或字符串数据")


Password = Annotated[
    str,
    AfterValidator(lambda x: is_vali_password(x)),
    PlainSerializer(lambda x: x, return_type=str),
    WithJsonSchema({"type": "string"}, mode="serialization"),
]

Username = Annotated[
    str,
    AfterValidator(lambda x: is_vali_username(x)),
    PlainSerializer(lambda x: x, return_type=str),
    WithJsonSchema({"type": "string"}, mode="serialization"),
]

Username_Add = Annotated[
    str,
    AfterValidator(lambda x: is_valid_username_add(x)),
    PlainSerializer(lambda x: x, return_type=str),
    WithJsonSchema({"type": "string"}, mode="serialization"),
]

Name_Add = Annotated[
    str,
    AfterValidator(lambda x: is_valid_name_add(x)),
    PlainSerializer(lambda x: x, return_type=str),
    WithJsonSchema({"type": "string"}, mode="serialization"),
]

Email = Annotated[
    str,
    AfterValidator(lambda x: is_vali_email(x)),
    PlainSerializer(lambda x: x, return_type=str),
    WithJsonSchema({"type": "string"}, mode="serialization"),
]

DateStr = Annotated[
    str | datetime.date | int | float,
    AfterValidator(is_vali_date),
    PlainSerializer(lambda x: x, return_type=str),
    WithJsonSchema({"type": "string"}, mode="serialization"),
]
DatetimeStr = Annotated[
    str | datetime.datetime | int | float | dict | None,
    AfterValidator(is_vali_datetime),
    PlainSerializer(lambda x: x, return_type=str),
    WithJsonSchema({"type": "string"}, mode="serialization"),
]
