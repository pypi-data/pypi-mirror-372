#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @Author   : Skypekey
# @FileName : ucmd
# @Time     : 2024-04-20 17:00:41

"""命令模块."""

from __future__ import annotations

import subprocess

from user_tools.common import ucheck

__FILENAME__ = "ucmd"


def run_cmd(arg_cmd: list, arg_timeout: int = -1) -> tuple[str, str]:
    """执行命令并返回结果。
    注意:
        方法中不对命令进行安全检查,
        因此传入的命令建议手动测试正常后再编写为自动化脚本。

    参数
        arg_cmd(list): 命令内容。例如: ['ls', '-l']
        arg_timeout(int): 命令超时时间, 默认为 -1, 即不指定超时时间。

    返回值(tuple(str, str))
        正常时返回 ('info', 命令执行结果)
        错误时返回 ('error', 错误信息)
        异常时返回 ('fatal', 异常信息)
    """
    err_list = [
        ucheck.arg_check(list, arg_cmd=arg_cmd),
        ucheck.arg_check(int, arg_timeout=arg_timeout),
    ]
    err_list = [err_info for err_info in err_list if err_info is not None]
    if err_list != []:
        return ("error", "\n".join(err_list))

    try:
        resp = subprocess.run(
            arg_cmd,
            capture_output=True,
            text=True,
            check=False,
        )
        if resp.returncode == 0:
            return ("info", resp.stdout)
    except FileNotFoundError:
        return ("error", f"未找到此命令: {arg_cmd[0]}")
    else:
        return (
            "fatal",
            (f"错误码为: {resp.returncode}\n    "
             f"错误信息为: \n    {resp.stderr}"),
        )


if __name__ == "__main__":
    pass
