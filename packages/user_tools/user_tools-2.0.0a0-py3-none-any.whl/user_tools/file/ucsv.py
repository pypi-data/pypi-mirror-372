#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @Author   : Skypekey
# @FileName : ucsv
# @Time     : 2024-04-23 00:11:33
"""CSV 模块"""

from __future__ import annotations

import csv
import pathlib
import string

from user_tools.common import ucheck, uencoding
from user_tools.file import upath

__FILENAME__ = "ucsv"


def verify_csv(
    arg_path: pathlib.Path | str,
    encoding: str = "UTF-8",
) -> tuple[bool, pathlib.Path | str]:
    """检查提供的路径是否为 CSV 文件路径

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
            if file_path.suffix != ".csv":
                return (
                    False,
                    (f"{arg_path!s} 不是 CSV 文件, "
                     "这是一个 {file_path.suffix} 文件"),
                )
            csv_flag = True
            # 以下代码可能来自 stackoverflow, 具体来源已经不清楚
            try:
                with file_path.open(newline="", encoding=encoding) as csvfile:
                    start = csvfile.read(4096)
                    # isprintable does not allow newlines,
                    # printable does not allow umlauts...
                    if not all(
                        c in string.printable or c.isprintable()
                        for c in start
                    ):
                        csv_flag = False
                    csv.Sniffer().sniff(start)
            except Exception:  # noqa: BLE001
                # Could not get a csv dialect -> probably not a csv.
                csv_flag = False
            if not csv_flag:
                return (False, f"{arg_path!s} 不是 CSV 文件")
        elif file_type != "csv":
            return (
                False,
                f"{arg_path!s} 不是 CSV 文件, 这是一个 {file_type} 文件",
            )
        return (True, file_path)

    return (False, file_type)


def read_csv(
    arg_path: pathlib.Path | str,
    encoding: str = "UTF-8-sig",
) -> tuple[bool, list | str]:
    """读 CSV 文件

    参数
        arg_path(pathlib.Path|str): 文件路径
        encoding(str): 文件编码, 默认为 UTF-8-sig
            若 CSV 中存在 BOM 信息, 使用 UTF-8 时, 首行首个单元格会返回 \\ufeff

    返回值tuple(bool, list|str):
        正常, 返回文件内容
        异常, 返回错误信息
    """
    flag, file_path = verify_csv(arg_path, encoding)
    if not flag:
        return (flag, file_path)

    csvlist = []
    with file_path.open(encoding=encoding) as f:
        csvlist = csv.dictReader(f)
    return (True, csvlist)


def write_csv(
    arg_path: pathlib.Path | str,
    arg_info: list[dict],
    fieldnames: None | list = None,
    encoding: str = "UTF-8",
    *,
    rewrite: bool = True,
) -> None | str:
    """写 CSV 文件

    参数
        arg_path(pathlib.Path|str): 文件路径
        arg_info(list[dict]): 文件内容
        fieldnames(list): 标题。默认为空, 即默认使用第一个内容的键作为标题。
        encoding(str): 文件编码, 默认为 UTF-8
        rewrite(bool): 当文件存在时, 是否覆盖写入, 默认是。

    返回值(None|str):
        返回 None 或错误信息
    """
    fieldnames = fieldnames if fieldnames else []

    err_list = [
        ucheck.arg_check(list, arg_info=arg_info, fieldnames=fieldnames),
        ucheck.arg_check(bool, rewrite=rewrite),
    ]
    err_list = [err_info for err_info in err_list if err_info is not None]
    if err_list != []:
        return "\n".join(err_list)

    flag, file_path = verify_csv(arg_path, encoding)
    if not flag:
        return file_path

    if upath.is_not_empty(arg_path) and not rewrite:
        return f"当文件 {arg_path} 不为空时, 必须指定 rewrite 为 True"

    not_dict_length = len({
        ucheck.arg_check(dict, i=i)
        for i in arg_info
        if ucheck.arg_check(dict, i=i)
    })
    if not_dict_length != 0:
        return f"arg_info 中有以下数量的元素不为 dict: {not_dict_length}"

    if file_path.exists() and rewrite:
        file_path.unlink()

    err_info = "、".join([i for i in fieldnames if i not in arg_info[0]])
    if fieldnames and arg_info:
        if len([i for i in fieldnames if i not in arg_info[0]]) > 0:
            return f"以下标题不存在: {err_info}"
    elif not fieldnames and arg_info:
        fieldnames = list(arg_info[0].keys())

    with file_path.open(mode="w", newline="", encoding=encoding) as csvfile:
        writer = csv.dictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(arg_info)
    return None


if __name__ == "__main__":
    pass
