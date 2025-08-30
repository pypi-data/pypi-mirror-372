#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @Author   : Skypekey
# @FileName : unet
# @Time     : 2024-04-22 21:23:55

"""net 模块"""

from __future__ import annotations

import ipaddress
import re
import traceback

from user_tools.common import ucheck

__FILENAME__ = "unet"


def verfiy_ip(arg_ip: str) -> bool:
    """校验 IP 地址是否合法"""
    try:
        ipaddress.ip_address(arg_ip)
    except ValueError:
        return False
    else:
        return True


def verfiy_url(url: str, style: str = "http") -> bool:
    """校验 URL 是否合法

    参数
        url(str): url 信息
    style(str): url 类型。支持的类型: http 或 git。默认 http
    """
    flag = False
    if style == "http":
        flag = bool(re.match(r"^https?:/{2}\w.+$", url))
    elif style == "git":
        flag = bool(
            re.match(
                r"^(http(s)?:\/\/([^\/]+?\/){2}|git@[^:]+:[^\/]+?\/).*?.git$",
                url,
            ),
        )
    return flag


def sort_net(
    netinfo: list, *, is_ip: bool = True, is_reverse: bool = False,
) -> tuple[bool, str | list]:
    """对给定的 netinfo 进行排序。

    参数
        netinfo(list): 待排序的 IP 地址(1.1.1.1)/IP 地址段(1.1.1.0/28)信息。
        is_ip(bool): 指定是否为 IP 地址。
        is_reverse(bool): 指定是否输出倒序结果。
    """
    expr1 = ucheck.arg_check(list, netinfo=netinfo)
    expr2 = ucheck.args_check(bool, is_ip=is_ip, is_reverse=is_reverse)
    errlist = [i for i in [expr1, expr2] if i]
    if errlist != []:
        return (False, "\n".join(errlist))

    try:
        ip_method = ipaddress.ip_address if is_ip else ipaddress.ip_network
        dst_list = sorted(
            [ip_method(i) for i in netinfo], reverse=is_reverse,
        )
    except ValueError:
        return (
            False,
            f"netinfo 解析异常: {traceback.format_exc().strip()}",
        )
    else:
        return (True, dst_list)


if __name__ == "__main__":
    pass
