#!/usr/bin/env python3
#-_- coding: utf-8 -_-

import logging
import os

# 获取上级目录
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 记录日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 添加TimedRotatingFileHandler
# 定义一个1天换一次log文件的handler
# 保留14个旧log文件
timefilehandler = logging.handlers.TimedRotatingFileHandler(
    filename=f"{base_dir}/logs/ss.log",
    when='D',
    interval=1,
    backupCount=14
)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
timefilehandler.setFormatter(formatter)

# 设置后缀名称，跟strftime的格式一样
timefilehandler.suffix = "%Y-%m-%d_%H-%M-%S.log"

logger.addHandler(timefilehandler)