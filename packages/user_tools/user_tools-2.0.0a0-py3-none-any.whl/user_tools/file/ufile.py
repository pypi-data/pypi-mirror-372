#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @Author   : Skypekey
# @FileName : ufile
# @Time     : 2024-04-21 06:24:57
"""file 模块"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pathlib

from user_tools.common import ucheck, uencoding
from user_tools.file import upath

__FILENAME__ = "ufile"


def verify_text_args(
    arg_path: pathlib.Path | str,
    encoding: str = "UTF-8",
    mode: str = "a",
) -> tuple[bool, pathlib.Path | str]:
    """校验参数

    参数
        arg_path(pathlib.Path|str): 文件路径
        encoding(str): 文件编码, 默认为 UTF-8

    返回值tuple(bool, list|str):
        正常, 返回 pathlib.Path 对象
        异常, 返回错误信息
    """
    flag, encoding = uencoding.get_encoding(encoding)
    if not flag:
        return (False, encoding)

    err_info = ucheck.arg_check(str, mode=mode)
    if err_info:
        return (False, err_info)

    flag, file_path = upath.file_path_check(arg_path)
    return (flag, file_path)


def read_file(
    arg_path: pathlib.Path | str,
    encoding: str = "UTF-8",
    *,
    need_list: bool = False,
    binary: bool = False,
) -> tuple[bool, str | dict | list]:
    """读文本文件

    参数
        arg_path(pathlib.Path|str): 文件路径
        encoding(str): 文件编码, 默认为 UTF-8
        need_list(bool): 是否需要返回按行分割的列表。
        binary(bool): 是否需要字节流

    返回值tuple(bool, dict|list|str):
        正常, 返回文件内容
        异常, 返回错误信息
    """
    flag, file_path = verify_text_args(arg_path, encoding)
    if not flag:
        return (False, file_path)
    err_info = ucheck.arg_check(bool, need_list=need_list, binary=binary)
    if err_info:
        return (False, err_info)

    if not upath.is_not_empty(arg_path):
        return (True, [] if need_list else "")

    if binary:
        msg = file_path.read_bytes()
    else:
        tmp_msg = file_path.read_text(encoding=encoding)
        if need_list:
            msg = []
            for line in tmp_msg.split("\n"):
                msg.append(line.strip())
        else:
            msg = tmp_msg
    return (True, msg)


def write_file(
    arg_path: pathlib.Path | str,
    arg_info: list | str,
    mode: str = "a",
    encoding: str = "UTF-8",
    *,
    rewrite: bool = True,
) -> None | str:
    """写文本文件

    参数
        arg_path(pathlib.Path|str): 文件路径
        arg_info(str|list): 文件内容
        encoding(str): 文件编码, 默认为 UTF-8
        mode(str): 文件写入方式, 默认为追加写入。
            全部格式见: https://docs.python.org/3/library/functions.html#open
        rewrite(bool): 当文件存在时, 是否覆盖写入, 默认是。

    返回值(None|str):
        返回 None 或错误信息
    """
    info_type_dict = {"str": "字符串类型文件内容", "list": "列表类型文件内容"}

    flag, file_path = verify_text_args(arg_path, encoding, mode)
    if not flag:
        return file_path

    if ucheck.args_check(info_type_dict, arg_info=arg_info):
        return ucheck.args_check(info_type_dict, arg_info=arg_info)
    if upath.is_not_empty(arg_path) and ("a" not in mode and not rewrite):
        return (
            f"当文件 {arg_path} 不为空时, "
            "必须指定 rewrite 为 True 或 mode 包含 a"
        )
    if "b" not in mode:
        if isinstance(arg_info, list):
            arg_info = "\n".join([f"{i}" for i in arg_info])
        with file_path.open(mode=mode, encoding=encoding) as f:
            f.write(arg_info)
    else:
        with file_path.open(mode=mode) as f:
            f.write(arg_info)
    return None


if __name__ == "__main__":
    pass
