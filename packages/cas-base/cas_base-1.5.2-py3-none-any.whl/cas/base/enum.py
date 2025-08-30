from enum import Enum


class ConnectType(Enum):
    # 应用
    APP = 1
    # 机器人
    BOT = 2
    # 远程监控
    RC = 3
    # 服务(数据源等)
    SVC = 4
    # 木马
    TRO = 5
    # 服务器
    SVR = 6
