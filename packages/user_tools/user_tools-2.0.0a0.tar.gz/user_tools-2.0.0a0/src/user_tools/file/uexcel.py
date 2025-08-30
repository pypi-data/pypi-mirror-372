#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @Author   : Skypekey
# @FileName : uexcel
# @Time     : 2024-04-21 06:52:40

"""Excel 模块"""
from __future__ import annotations

import pathlib

from user_tools.file import upath

__FILENAME__ = "uexcel"


def verify_excel(
    arg_path: pathlib.Path | str,
) -> tuple[bool, pathlib.Path | str]:
    """检查提供的路径是否为 Excel 文件路径

    参数
        arg_path(pathlib.Path|str): 文件路径

    返回值tuple(bool, list|str):
        正常, 返回 pathlib.Path 对象
        异常, 返回错误信息
    """
    flag, file_type = upath.file_type_get(arg_path)
    if flag:
        file_path = pathlib.Path(arg_path)
        if file_type is None:
            if file_path.suffix != ".xlsx":
                return (
                    False,
                    f"{arg_path!s} 不是 xlsx 文件, 这是一个 {file_path.suffix} 文件",  # noqa: E501
                )
        elif file_type != "xlsx":
            return (
                False,
                f"{arg_path!s} 不是 xlsx 文件, 这是一个 {file_type} 文件",
            )
        return (True, file_path)

    return (False, file_type)


if __name__ == "__main__":
    pass
