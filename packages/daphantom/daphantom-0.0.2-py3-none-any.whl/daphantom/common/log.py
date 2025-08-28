# -*- coding: utf-8 -*-
"""日志轮子"""
from loguru import logger
import sys
import os

class CustomLogger:
    def __init__(self, log_to_console=True, log_to_file=True, log_to_error_file=True,
                 log_dir='logs', log_file='run.log', error_file='error.log',
                 console_level='DEBUG', file_level='DEBUG', error_level='ERROR', encoding='utf-8'):
        """
        初始化自定义日志记录器

        :param log_to_console: 是否将日志输出到控制台
        :param log_to_file: 是否将正常日志输出到文件
        :param log_to_error_file: 是否将错误日志输出到单独的文件
        :param log_dir: 日志文件夹路径
        :param log_file: 正常日志文件名
        :param error_file: 错误日志文件名
        :param console_level: 控制台日志级别
        :param file_level: 正常日志文件级别
        :param error_level: 错误日志文件级别
        :param encoding: 文件编码
        """
        self.log_to_console = log_to_console
        self.log_to_file = log_to_file
        self.log_to_error_file = log_to_error_file
        self.log_dir = log_dir
        self.log_file = log_file
        self.error_file = error_file
        self.console_level = console_level
        self.file_level = file_level
        self.error_level = error_level
        self.encoding = encoding
        if log_to_file or log_to_error_file:
            # 创建日志目录（如果不存在）
            os.makedirs(self.log_dir, exist_ok=True)

    def _setup_logger(self):
        """
        设置日志记录器
        """
        # # 定义控制台日志输出格式
        # stdout_fmt = '<cyan>{time:YYYY-MM-DD HH:mm:ss,SSS}</cyan> ' \
        #              ' | <level>{level:<7}</level> | ' \
        #              '<blue>{module}</blue>.<blue>{function:<9}</blue>:<cyan>{line:<4}</cyan>' \
        #              ': <level>{message}</level> '

        # 定义控制台日志输出格式
        stdout_fmt = '<cyan>{time:HH:mm:ss,SSS}</cyan> -> <level>{message}</level> '

        # 定义正常日志文件记录格式
        logfile_fmt = '---------------{time:YYYY-MM-DD HH:mm:ss,SSS} [{level}] ---------------\n' \
                        'module：{module}.{function}.{line} \n' \
                        'error_msg：{message} \n'

        # 定义错误日志文件记录格式
        errorfile_fmt = '---------------{time:YYYY-MM-DD HH:mm:ss,SSS} [{level}] ---------------\n' \
                        'module：{module}.{function}.{line} \n' \
                        'error_msg：{message} \n'


        # 移除默认的日志处理器
        logger.remove()

        # 设置编码
        if not os.environ.get('PYTHONIOENCODING'):
            os.environ['PYTHONIOENCODING'] = 'utf-8'

        # 配置日志输出到控制台
        if self.log_to_console:
            logger.add(sys.stderr, level=self.console_level, format=stdout_fmt, enqueue=True)

        # 配置日志输出到正常文件
        if self.log_to_file:
            log_path = os.path.join(self.log_dir, self.log_file)
            '''
            rotation："1 day"（每天生成新日志文件）, "1 week"（每周生成）, "1 month"（每月生成）, "1 year"（每年生成）
            retention："1 day"（只保留最近 1 天的日志）, "1 week"（保留最近 1 周）, "1 month"（保留最近 1 个月）, "1 year"（保留最近 1 年）
            '''
            logger.add(log_path, level=self.file_level, format=logfile_fmt,
                       enqueue=True, encoding=self.encoding, rotation="1 day", retention="1 week")

        # 配置错误日志输出到错误文件
        if self.log_to_error_file:
            error_log_path = os.path.join(self.log_dir, self.error_file)
            logger.add(error_log_path, level=self.error_level, format=errorfile_fmt,
                       enqueue=True, encoding=self.encoding, rotation="1 week", retention="1 month")
        logger.info("日志功能已启动...")
        return logger

__all__ = ['CustomLogger']


if __name__ == "__main__":
    # # 导入模块
    # from logModule import CustomLogger
    # 实例化并运行
    logModule = CustomLogger(log_to_console=True, log_to_file=True, log_to_error_file=True)._setup_logger()
    '''
    :param log_to_console: 是否将日志输出到【控制台】
    :param log_to_file: 是否将【日志】输出到文件
    :param log_to_error_file: 是否将【错误日志】输出到文件
    '''
    # 测试日志输出
    logModule.debug("这是一个调试信息")
    logModule.debug("这是一个调试信息")
    logModule.info("这是一个普通信息")
    logModule.warning("这是一个警告信息")
    logModule.error("这是一个错误信息")
