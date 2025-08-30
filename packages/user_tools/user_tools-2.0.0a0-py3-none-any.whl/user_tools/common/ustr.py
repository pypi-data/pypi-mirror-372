#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @Author   : Skypekey
# @FileName : ustr
# @Time     : 2024-04-20 17:01:03
"""字符串模块"""

from __future__ import annotations

import random

__FILENAME__ = "ustr"


def remove_blank(string: str) -> None | str:
    r"""移除字符串中的所有空格。
    包括以下几种类型:  \r\n, \t, \r, \n, \xa0, \u3000, &nbsp;, [space]
    PS: 此方法主要用于解析 Web 字符串时, 避免空白影响解析。
    """
    if not isinstance(string, str):
        return None

    trans_table = {
        r"\r\n": "",
        r"\t": "",
        r"\r": "",
        r"\xa0": "",
        r"\u3000": "",
        r"&nbsp;": "",
    }

    string = string.strip()
    for k, v in trans_table.items():
        string = string.replace(k, v)
    return string



def random_str(string: str) -> None | str:
    """打乱字符串中字符的顺序并返回打乱后的字符串。
    如果传入的参数不是字符串类型, 则返回None"""

    if isinstance(string, str):
        list_str = list(string)
        random.shuffle(list_str)
        return "".join(list_str)

    return None


if __name__ == "__main__":
    pass
