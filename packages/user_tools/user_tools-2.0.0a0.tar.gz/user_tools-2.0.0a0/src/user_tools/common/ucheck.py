#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @Author   : Skypekey
# @FileName : ucheck
# @Time     : 2024-04-20 17:00:31

"""检查模块"""

from __future__ import annotations

__FILENAME__ = "ucheck"


def __get_info(info: str, tmp_info: str) -> str:
    return f"{info}\n{tmp_info}" if info else tmp_info


def arg_check(arg_type: object, **kwargs) -> None | str:
    """针对单个参数进行检查。校验成功返回 None , 异常返回异常信息。

    参数
    arg_type(object): 参数类型。
    """
    if not isinstance(arg_type, object):
        return "arg_type 必须是一个对象, 例如 str 等"

    info = ""
    for k, v in kwargs.items():
        if not isinstance(v, arg_type):
            tmp_info = (
                f"{k} 必须为 {arg_type.__name__} 数据类型, "
                f"当前为: {type(v).__name__}"
            )
            info = __get_info(info, tmp_info)

    return info if info else None


def args_check(
    arg_dict: dict,
    check_type: str = "args",
    **kwargs,
) -> None | str:
    """进行类型或键值检查。校验成功返回 None , 异常返回异常信息。
    检查 arg_info 是否为 arg_dict 类型。
    或检查 arg_dict 的键是否包含 arg_info。

    参数
        check_type(str):
            args: 判断参数的数据类型是否在给定的字典中。
                如 kwargs 为 s=1, arg_dict 为 {"int": "数量", "str", "名称"}
                则 s 的数据类型在给定的字典中
            type: 判断参数是否在给定的字典中。
                如 kwargs 为 s=1, arg_dict 为 {"move": "移动", "check", "检查"}
                则 s 的值不在给定的字典中
        arg_dict(dict):
            当 check_type 为 args 时, 此变量为提供的变量允许的数据类型。
                形如 {'list': '列表格式的命令', 'str': '字符串格式的命令'}
            当 check_type 为 type 时, 此变量为参数允许的列表。
                形如 {"check": "检查信息", "query": "查询信息"}
    """
    arg_type_dict = {
        "args": "判断参数数据类型是否在允许列表中",
        "type": "判断参数是否在参数允许列表中",
    }
    base_err_msg = ", ".join([f"{k}({v})" for k, v in arg_dict.items()])
    arg_err_msg = ", ".join([f"{k}({v})" for k, v in arg_type_dict.items()])

    if arg_check(dict, arg_dict=arg_dict):
        return arg_check(dict, arg_dict=arg_dict)

    info = ""
    if check_type == "args":
        for k, v in kwargs.items():
            tmp_info = ""
            if not tmp_info and type(v).__name__ not in arg_dict:

                return (
                    f"{k} 数据格式错误, 数据格式不能为: {type(v).__name__}, "
                    f"支持的数据格式如下: {base_err_msg}"
                )

            if tmp_info:
                info = __get_info(info, tmp_info)
    elif check_type == "type":
        for k, v in kwargs.items():
            if v not in arg_dict:
                tmp_info = f"{k} 支持的类型如下: {base_err_msg}"
                info = __get_info(info, tmp_info)
    else:
        return f"检查类型错误, 当前支持的检查类型如下:  {arg_err_msg}"

    return info if info else None


if __name__ == "__main__":
    pass
