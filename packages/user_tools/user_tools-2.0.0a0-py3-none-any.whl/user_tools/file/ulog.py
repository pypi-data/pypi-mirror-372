#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @Author   : Skypekey
# @FileName : ulog
# @Time     : 2024-04-23 20:42:34

"""log 模块"""
from __future__ import annotations

import logging
import logging.handlers
import mimetypes
import pathlib

__FILENAME__ = "ulog"
LEVEL = ["debug", "info", "warning", "warn", "error", "fatal", "critical"]


class Pylog:
    """日志对象, 使用 logging.handlers.TimedRotatingFileHandler"""

    def __init__(
        self,
        log_file: pathlib.Path | str,
        **kwargs,
    ) -> None:
        """初始化日志对象

        参数
            log_file(pathlib.Path|str): 日志文件路径
            datefmt(str): 日志的日期时间格式。默认是 '%Y-%m-%d %H:%M:%S'
                时间格式详见https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
            logfmt(str): 日志格式。
                默认是 '%(asctime)s [%(levelname)s] %(message)s'
            encoding(str): 文件编码格式, 默认是 UTF-8.
            backupcount(int): 日志文件备份数量, 默认是 7
        """
        default = {
            "logfmt": "%(asctime)s [%(levelname)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "encoding": "UTF-8",
            "backupcount": 7,
        }
        self.logfmt = kwargs.get("logfmt", default.get("logfmt"))
        self.datefmt = kwargs.get("datefmt", default.get("datefmt"))
        self.encoding = kwargs.get("encoding", default.get("encoding"))
        self.backupcount = kwargs.get("backupcount",
                                      default.get("backupcount"))
        self.log_file = log_file
        pathlib.Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)

        file_type = mimetypes.guess_type(log_file)[0]
        if file_type is not None and file_type.split("/")[0] != "text":
            err_msg = "文件类型错误, 日志文件必须为文本格式的文件"
            raise TypeError(err_msg)

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.fmt = logging.Formatter(self.logfmt, self.datefmt)

        self.__test_log = True
        self.logger_msg("info", "日志对象初始化成功!")
        self.__test_log = False

    def __console(self, level: str, message: str) -> None:
        """日志记录内部方法

        参数
            level(str): 日志级别
        msg(str): 需要记录的日志内容
        """
        file_handle = logging.handlers.TimedRotatingFileHandler(
            filename=self.log_file,
            encoding=self.encoding,
            backupCount=self.backupcount,
            when="D",
        )
        if self.__test_log:
            file_handle.setFormatter(None)
        else:
            file_handle.setFormatter(self.fmt)

        if level.lower() == "debug":
            file_handle.setLevel(logging.DEBUG)
        else:
            file_handle.setLevel(logging.INFO)
        self.logger.addHandler(file_handle)

        if level == "info":
            self.logger.info(message)
        elif level == "debug":
            self.logger.debug(message)
        elif level in ("warning", "warn"):
            self.logger.warning(message)
        elif level == "error":
            self.logger.error(message)
        elif level in ("fatal", "critical"):
            self.logger.critical(message)

        self.logger.removeHandler(file_handle)
        file_handle.close()

    def logger_msg(self, level: str, msg: str) -> None:
        """记录日志"""
        if not isinstance(level, str) or level not in LEVEL:
            self.__console(
                "error",
                (f"{level}: 不是字符串, 或不是支持的日志级别! "
                 "\n支持的日志级别为: "
                f"{'、'.join(LEVEL)}\n需要记录的日志内容为: {msg}"),
            )
        else:
            self.__console(level, msg)


if __name__ == "__main__":
    pass
