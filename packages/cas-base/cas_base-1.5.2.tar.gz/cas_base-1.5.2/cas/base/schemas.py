from pydantic import BaseModel, ConfigDict, field_validator, Field
from pydantic_core.core_schema import FieldValidationInfo
from .validator import *

###########################################################
#   用户登录
###########################################################


class UserLoginRoleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    role_key: str


class UserLoginDeptOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    dept_key: str
    is_active: bool = True


class UserLoginSoftwareOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    is_active: bool = Field(False, title="是否禁用")
    user_id: int = Field(..., title="所属用户")
    software_id: int = Field(..., title="所属软件")
    software_name: str = Field(..., title="软件名称")
    software_data_1: str | None = Field(None, title="扩展数据1")
    software_data_2: str | None = Field(None, title="扩展数据2")
    software_data_3: str | None = Field(None, title="扩展数据3")
    software_data_4: str | None = Field(None, title="扩展数据4")
    software_data_5: str | None = Field(None, title="扩展数据5")
    expiration_at: DatetimeStr = Field(..., title="过期时间")


class UserLoginOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    username: Username
    email: Email | None = None
    nickname: str | None = None
    remark: str | None = None
    avatar: str | None = None
    is_active: bool | None = True
    gender: str | None = "0"
    is_reset_password: bool | None = None
    last_login: DatetimeStr | None = None
    last_ip: str | None = None
    is_admin: bool = False
    data_range: int = 0
    data_deps: list[UserLoginDeptOut] = []
    roles: list[UserLoginRoleOut] = []
    depts: list[UserLoginDeptOut] = []
    softwares: list[UserLoginSoftwareOut] = []
    permissions: list[str] = []
    updated_at: DatetimeStr
    created_at: DatetimeStr


###########################################################
#   用户注册
###########################################################
class UserRegisterIn(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username: Username_Add
    password: Password
    password_two: Password

    @field_validator("password_two")
    def check_passwords_match(cls, v, info: FieldValidationInfo):
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("两次密码不一致!")
        return v


class LoginOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    token_type: str
    access_token: str
    refresh_token: str
