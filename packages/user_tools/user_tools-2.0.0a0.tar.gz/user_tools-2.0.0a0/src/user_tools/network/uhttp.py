#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @Author   : Skypekey
# @FileName : uhttp
# @Time     : 2024-04-22 21:10:12

"""http 模块"""

from __future__ import annotations

import requests
from requests import Session

from user_tools.common import ucheck

__FILENAME__ = "uhttp"


def get_session(
    arg_headers: dict | None = None,
    auth_type: str = "",
    *,
    has_header: bool = True,
) -> tuple[bool, str | Session]:
    """获取 session 对象

    参数
        arg_headers(dict): header 信息
        has_header(bool): 是否需要携带 header 信息
        auth_type(str): 请求格式。json、xml 或空白(即无需携带 header 信息)

    返回值tuple(bool, Session|str)
        正常, 返回路径列表
        异常, 返回报错信息
    """
    arg_headers = {} if arg_headers is None else arg_headers

    if ucheck.arg_check(dict, arg_headers=arg_headers):
        return (False, ucheck.arg_check(dict, arg_headers=arg_headers))
    if ucheck.arg_check(bool, has_header=has_header):
        return (False, ucheck.arg_check(bool, has_header=has_header))
    if ucheck.arg_check(str, auth_type=auth_type):
        return (False, ucheck.arg_check(str, auth_type=auth_type))

    if auth_type == "":
        headers = {}
    elif auth_type == "json":
        headers = {
            "Accept": "application/json",
            "Content-type": "application/json",
        }
    elif auth_type == "xml":
        headers = {
            "Content-Type": "application/xml",
            "Accept": "application/xml",
        }
    else:
        return (False, f"不支持或未实现的 auth_type: {auth_type}")

    headers.update(arg_headers)
    session = requests.Session()
    session.verify = False
    if has_header:
        session.headers.update(headers)
    else:
        session.headers.update(arg_headers)
    return (True, session)


if __name__ == "__main__":
    pass
