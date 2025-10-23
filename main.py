import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ace_attr import *
from check_service import is_service_running
import time
import yaml

# 读取 YAML 文件
with open('config.yml', 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)

if __name__ == "__main__":
    service_name = config["ace"]["service_name"]
    process_name_list = config["ace"]["process_name_list"]
    interval = config["ace"]["interval"]
    pid_list = []

    while True:
        time.sleep(interval)
        if not is_service_running(service_name):
            logger.info(f"{service_name} 服务未运行")
            if len(pid_list) > 0:
                pid_list = []
            continue
        logger.info(f"{service_name} 服务已运行")
        if len(pid_list) == 0:
            for process_name in process_name_list:
                pid_list.append(get_pid_by_name(process_name))
        if is_process_priority_low_by_pid(pid_list[0]):
            logger.info("本次服务启动后已修改过，跳过。")
            continue
        for pid in pid_list:
            set_priority_and_cpuCore_by_pid(pid)