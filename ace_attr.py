import ctypes
import psutil
from logger import logger


# 根据进程名称查询 pid
def get_pid_by_name(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'].lower() == process_name.lower():
                logger.info(f"找到目标进程: {process_name} (PID: {proc.info['pid']})")
                return proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    logger.info(f"未找到目标进程: {process_name}")
    return None


# 根据 pid 设置最低优先级和cpu相关性
def set_priority_and_cpuCore_by_pid(pid):
    try:
        # 获取进程信息（验证是否可访问）
        proc = psutil.Process(pid)
        logger.info(f"找到目标进程: {proc.name()} (PID: {pid})")

        # 获取进程句柄
        handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, pid)
        if not handle:
            logger.error(f"无法打开进程 (PID: {pid}) 的句柄")
            return

        # 设置优先级为低（IDLE_PRIORITY_CLASS）
        priority_class = 0x00000040  # 对应 Windows 的 IDLE_PRIORITY_CLASS
        if ctypes.windll.kernel32.SetPriorityClass(handle, priority_class) == 0:
            logger.error(f"设置优先级失败: {ctypes.WinError(ctypes.get_last_error())}")
        else:
            logger.info(f"已将进程 (PID: {pid}) 的优先级设置为低")

        # 设置只使用 CPU 的最后一个核心
        cpu_count = psutil.cpu_count(logical=True)
        last_core_mask = 1 << (cpu_count - 1)  # 最后一个逻辑核心的掩码
        if ctypes.windll.kernel32.SetProcessAffinityMask(handle, last_core_mask) == 0:
            logger.error(f"设置 CPU 核心失败: {ctypes.WinError(ctypes.get_last_error())}")
        else:
            logger.info(f"已将进程 (PID: {pid}) 绑定到 CPU 最后一个核心 (核心 {cpu_count - 1})")

        # 关闭句柄
        ctypes.windll.kernel32.CloseHandle(handle)

    except psutil.NoSuchProcess:
        logger.error(f"找不到 PID 为 {pid} 的进程")
    except psutil.AccessDenied:
        logger.error(f"无权访问 PID 为 {pid} 的进程")
    except Exception as e:
        logger.error(f"设置进程失败: {e}")


# 检查进程优先级是否为低
def is_process_priority_low_by_pid(pid):
    kernel32 = ctypes.windll.kernel32
    try:
        # 获取进程句柄（仅需查询权限）
        handle = kernel32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_INFORMATION
        if not handle:
            logger.error(f"无法打开进程 (PID: {pid}) 的句柄")
            return False

        priority_class = kernel32.GetPriorityClass(handle)
        kernel32.CloseHandle(handle)

        if priority_class == 0:
            logger.error(f"获取优先级失败: {ctypes.WinError(ctypes.get_last_error())}")
            return False

        return priority_class == 0x00000040  # IDLE_PRIORITY_CLASS
    except psutil.NoSuchProcess:
        logger.error(f"找不到 PID 为 {pid} 的进程")
    except psutil.AccessDenied:
        logger.error(f"无权访问 PID 为 {pid} 的进程")
    except Exception as e:
        logger.error(f"检查进程优先级时出错: {e}")

    return False