#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @Author   : Skypekey
# @FileName : uhash
# @Time     : 2024-04-20 17:00:53
"""哈希模块"""

from __future__ import annotations

import hashlib
import hmac

from user_tools.common import ucheck

__FILENAME__ = "uhash"


def get_str_md5(arg_str: str) -> tuple[bool, str]:
    """返回字符串的 md5 值

    参数
        arg_str(str): 字符串值

    返回值(tuple(bool, str))
        异常时返回 (False, 异常信息)
        正常时返回 (True, 字符串的 md5 值)
    """
    err_info = ucheck.arg_check(str, arg_str=arg_str)
    if err_info:
        return (False, err_info)

    md5name = ""
    if arg_str:
        tmp_md5 = hashlib.md5(bytes(arg_str, encoding="UTF-8"))
        md5name = tmp_md5.hexdigest().upper()
    return (True, md5name)


def hmac_str(
    arg_str: str,
    arg_key: str = "",
    special: str = "",
    arg_length: int = 20,
) -> tuple[bool, str]:
    """将字符串通过一定的转换逻辑进行转换并输出。

    参数
        arg_str(str): 字符串值
        arg_key(str): 转换时使用的关键字。若为空, 则无需添加
        special(str): 转换后需要添加的特殊字符。若为空, 则无需添加
        arg_length(int): 转换后字符串的长度。
            默认为 20 位, 最小为 8 位, 最大为 60 位

    返回值(tuple(bool, str))
        异常时返回 (False, 异常信息)
        正常时返回 (True, 按照一定逻辑转换后的字符串)
    """
    err_list = [
        ucheck.arg_check(
            str,
            arg_str=arg_str,
            arg_key=arg_key,
            special=special,
        ),
        ucheck.arg_check(int, arg_length=arg_length),
    ]
    err_list = [err_info for err_info in err_list if err_info is not None]
    if err_list != []:
        return (False, "\n".join(err_list))

    if arg_length not in range(8, 61):
        return (False, "arg_length 默认为 20, 最小为 8, 最大为 60.")

    tmp_str = arg_str.encode(encoding="UTF-8")
    key = arg_key.encode(encoding="UTF-8")

    hmd5 = (
        hmac.new(key, tmp_str, hashlib.sha256)
        .hexdigest()
        .encode(encoding="UTF-8")
    )
    rule = list(
        hmac.new(
            b"u!K8Y",
            hmd5,
            hashlib.sha256,
        ).hexdigest(),
    )
    source = list(
        hmac.new(
            b"aJpde_9",
            hmd5,
            hashlib.sha256,
        ).hexdigest(),
    )

    for i in range(32):
        if not (source[i].isdigit()) and rule[i] in "TalkischeapShowmethecode":
                source[i] = source[i].upper()

    tmp_code = "".join(source[1:arg_length])

    step = 5
    for flag_num, i in enumerate(source):
        if not (i.isdigit()):
            tmp_code = i + tmp_code
        if flag_num > step:
            break

    code = list(tmp_code)

    if special:
        for i in range(1, arg_length, 5):
            code.insert(i, special)

    code = "".join(code)
    return (True, code)


if __name__ == "__main__":
    pass
