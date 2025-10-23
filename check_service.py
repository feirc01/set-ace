from logger import logger
import win32serviceutil
import win32service
import pywintypes


def is_service_running(service_name):
    """
    检查指定的 Windows 服务是否正在运行，如果服务正在运行返回 True；否则（停止、不存在、异常等）返回 False
    """
    try:
        status = win32serviceutil.QueryServiceStatus(service_name)[1]
        return status == win32service.SERVICE_RUNNING
    except pywintypes.error as e:
        # 常见错误：服务不存在 (error 1060), 访问被拒绝等
        if e.winerror == 1060:
            logger.debug(f"'{service_name}' 服务暂未安装")
        else:
            logger.error(f"Windows error while querying service '{service_name}': {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error when checking service '{service_name}': {e}")
        return False