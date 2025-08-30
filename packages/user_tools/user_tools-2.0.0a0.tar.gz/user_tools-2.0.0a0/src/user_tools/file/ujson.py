#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @Author   : Skypekey
# @FileName : ujson
# @Time     : 2024-04-20 17:01:25

"""json文件模块"""

from __future__ import annotations

import json
import pathlib

from user_tools.common import ucheck, uencoding
from user_tools.file import upath

__FILENAME__ = "ujson"


def verify_json(
    arg_path: pathlib.Path | str,
    encoding: str = "UTF-8",
) -> tuple[bool, pathlib.Path | str]:
    """检查提供的路径是否为 JSON 文件路径

    注意
        判断方法不一定完全准确。

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

    flag, file_type = upath.file_type_get(arg_path)
    if flag:
        file_path = pathlib.Path(arg_path)
        if file_type is None:
            json_flag = True
            try:
                with file_path.open(encoding=encoding) as f:
                    json.load(f)
            except Exception:  # noqa: BLE001
                json_flag = False
            if not json_flag:
                return (False, f"{arg_path!s} 不是 JSON 文件")
        elif file_type != "json":
            return (
                False,
                f"{arg_path!s} 不是 JSON 文件, 这是一个 {file_type} 文件",
            )
        return (True, file_path)

    return (False, file_type)


def read_json(
    arg_path: pathlib.Path | str,
    encoding: str = "UTF-8",
) -> tuple[bool, str | dict | list]:
    """读 json 文件

    参数
        arg_path(pathlib.Path|str): 文件路径
        encoding(str): 文件编码, 默认为 UTF-8

    返回值tuple(bool, dict|list|str):
        正常, 返回文件内容
        异常, 返回错误信息
    """
    flag, file_path = verify_json(arg_path, encoding)
    if not flag:
        return (False, file_path)
    if not upath.is_not_empty(arg_path):
        return (True, {})

    json_dict = {}
    with file_path.open(encoding=encoding) as f:
        json_dict = json.load(f)
    return (True, json_dict)


def write_json(
    arg_path: pathlib.Path | str,
    arg_info: dict | list,
    encoding: str = "UTF-8",
    *,
    rewrite: bool = True,
) -> None | str:
    """写 json 文件

    参数
        arg_path(pathlib.Path|str): 文件路径
        arg_info(dict|list): 文件内容
        encoding(str): 文件编码, 默认为 UTF-8
        rewrite(bool): 当文件存在时, 是否覆盖写入, 默认是。

    返回值(None|str):
        返回 None 或错误信息
    """
    info_type_dict = {"list": "列表格式json", "dict": "字典格式json"}

    flag, file_path = verify_json(arg_path, encoding)
    if not flag:
        return file_path

    if ucheck.args_check(info_type_dict, arg_info=arg_info):
        return ucheck.args_check(info_type_dict, arg_info=arg_info)
    if ucheck.arg_check(bool, rewrite=rewrite):
        return ucheck.arg_check(bool, rewrite=rewrite)
    if upath.is_not_empty(arg_path) and not rewrite:
        return f"当文件 {arg_path} 不为空时, 必须指定 rewrite 为 True"

    with file_path.open(mode="w", encoding=encoding) as f:
        # ensure_ascii = False is to display Chinese,
        # if not written, it will be displayed as unicode encoding.
        # indent is to format the json file,
        # otherwise it will be displayed on one line.
        json.dump(arg_info, f, ensure_ascii=False, indent=4)
    return None


if __name__ == "__main__":
    pass
