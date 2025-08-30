from setuptools import setup, find_packages

setup(
    name="cas-base",  # 包的名称
    version="1.5.2",  # 版本号
    description="cas-base",  # 包的简短描述
    author="xxoo",  # 作者名称
    author_email="xxoo@example.com",  # 作者邮箱
    packages=find_packages(),  # 自动查找项目中的包
    install_requires=[
        "pydantic==2.8.2",
        "pydantic-settings==2.4.0",
        "pydantic_core==2.20.1",
        "websockets==10.4",
        "requests==2.31.0",
        "loguru==0.7.2",
        "PyJWT==2.8.0",
        "pycryptodome==3.19.1",
        "redis==5.1.1",
        "elasticsearch==8.15.1",
        "psutil==5.9.8",
    ],  # 项目依赖
)
