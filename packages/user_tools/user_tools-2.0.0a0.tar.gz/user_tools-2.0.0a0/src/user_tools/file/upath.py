#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @Author   : Skypekey
# @FileName : upath
# @Time     : 2024-04-20 17:01:35

"""路径模块"""

from __future__ import annotations

import pathlib

import filetype

from user_tools.common import ucheck

__FILENAME__ = "upath"
__PATH_STRUCT_DICT = {
    "str": "路径字符串",
    "Path": "pathlib 模块的 Path 对象",
    "PosixPath": "pathlib 模块的 PosixPath 对象",
    "PurePath": "pathlib 模块的 PurePath 对象",
    "PurePosixPath": "pathlib 模块的 PurePosixPath 对象",
    "PureWindowsPath": "pathlib 模块的 PureWindowsPath 对象",
    "WindowsPath": "pathlib 模块的 WindowsPath 对象",
}


def path_check(
    arg_path: pathlib.Path | str,
) -> tuple[bool, pathlib.Path | str]:
    """检查 arg_path 是否为 str 或 pathlib.Path 类型对象"""
    if ucheck.args_check(__PATH_STRUCT_DICT, arg_path=arg_path):
        return (
            False,
            ucheck.args_check(__PATH_STRUCT_DICT, arg_path=arg_path),
        )
    if str(arg_path) == "":
        return (False, "路径不能为空")
    return (True, pathlib.Path(arg_path))


def file_path_check(arg_path: pathlib.Path | str) -> tuple[bool, str]:
    """文件路径判断

    --已对 arg_path 进行了参数校验, 同时判断了是否为文件。

    参数
    arg_path(pathlib.Path|str): 文件路径
    """
    flag, file_path = path_check(arg_path)
    if not flag:
        return (False, file_path)
    if str(arg_path).endswith("\\"):
        return (False, "文件不能以\\结尾")

    if file_path.exists() and not file_path.is_file():
        return (False, f"路径 {arg_path} 必须为文件路径")
    return (True, file_path)


def file_type_get(arg_path: pathlib.Path | str) -> tuple[bool, str]:
    """获取文件类型

    --已对 arg_path 进行了参数校验, 同时判断了是否为文件。

    参数
    arg_path(pathlib.Path|str): 文件路径
    """
    flag, file_path = file_path_check(arg_path)
    if not flag:
        return (False, file_path)

    kind = None
    if file_path.exists():
        try:
            kind = filetype.guess(file_path)
            if kind is not None:
                kind = kind.extension
        except TypeError:
            pass

    return (True, kind)


def is_not_empty(arg_path: pathlib.Path | str) -> bool:
    """判断文件或目录是否为空"""
    flag, file_path = path_check(arg_path)
    if not flag:
        return False

    if file_path.is_dir():
        return bool(len(list(file_path.iterdir())) > 0)
    if file_path.is_file():
        return bool(file_path.stat().st_size != 0)

    return False


def path_get(
    arg_path: pathlib.Path | str,
    path_args: str = "",
    depth: int = -1,
    *,
    contains_empth: bool = True,
) -> tuple[bool, dict | str]:
    """遍历路径, 得到路径下的目录或文件清单。

    参数
        arg_path(pathlib.Path|str): 待检查的路径。
        path_args(str): 获取指定类型的文件路径。
        depth(int): 路径递归深度, 默认为 -1(获取所有路径)。
        contains_empth(bool): 是否包含空目录, 默认是。

    返回值tuple(bool, dict|str)
        正常, 返回路径列表
        异常, 返回报错信息
    """
    flag, file_path = path_check(arg_path)
    if not flag:
        return (False, file_path)

    expr1 = ucheck.arg_check(str, path_args=path_args)
    expr2 = ucheck.arg_check(int, depth=depth)
    expr3 = ucheck.arg_check(bool, contains_empth=contains_empth)
    err_msg = "\n".join(filter(None, [expr1, expr2, expr3]))

    if err_msg:
        return (False, err_msg)

    if depth not in (-1, 1):
        return (False, f"depth 必须等于 1 或 -1, 当前为: {depth}")

    if not file_path.is_dir():
        return (False, f"路径: {arg_path!s} 不存在或不是目录")

    if depth == -1:
        path_arg = "**/*" if path_args == "" else f"**/*.{path_args}"
        path_list = list({str(f) for f in file_path.glob(path_arg)})
    else:
        path_list = []
        for i in file_path.iterdir():
            if path_args:
                if i.name.endswith(path_args):
                    path_list.append(str(i))
            else:
                path_list.append(str(i))
    if contains_empth:
        return (True, path_list)

    return (True, [str(f) for f in path_list if is_not_empty(f)])


if __name__ == "__main__":
    pass
