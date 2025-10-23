import logging
import datetime
from pathlib import Path


log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_filename = log_dir / "app_{:%Y-%m-%d}.log".format(datetime.datetime.now())

# 创建 Logger 对象
logger = logging.getLogger("my_logger")
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler(log_filename, encoding="utf-8")
handler.setFormatter(
    logging.Formatter('[%(asctime)s] - %(levelname)s - %(filename)s.%(funcName)s:%(lineno)d行 - %(message)s')
)

# 将 Handler 添加到 Logger
logger.addHandler(handler)
