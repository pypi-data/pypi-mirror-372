#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @Author   : Skypekey
# @FileName : utime
# @Time     : 2024-04-20 17:01:13
"""时间模块"""

from __future__ import annotations

import datetime

from chinese_calendar import (
    get_holidays,
    get_workdays,
    is_holiday,
    is_workday,
)

from user_tools.common import ucheck

__FILENAME__ = "utime"
DATE_STRUCT_DICT = {
    "int": "时间戳",
    "float": "时间戳",
    "str": "时间字符串",
    "date": "datetime 模块的 date 对象",
    "datetime": "datetime 模块的 datetime 对象",
}
WEEK_DICT = {
    0: "星期一",
    1: "星期二",
    2: "星期三",
    3: "星期四",
    4: "星期五",
    5: "星期六",
    6: "星期日",
}


def get_datatime_by_str(
    date_text: str,
    format_str: str = "%Y-%m-%d %H:%M:%S",
) -> tuple[bool, datetime.datetime | str]:
    """将日期字符串根据给定的格式转换为 datetime.datetime 对象"""

    expr = ucheck.arg_check(str, date_text=date_text, format_str=format_str)
    if expr:
        return (False, expr)

    tmp_date = datetime.datetime.strptime(date_text, format_str)  # noqa: DTZ007
    return (True, tmp_date.astimezone(datetime.timezone.utc))


def get_datatime_by_timestamp(
    date_text: float,
) -> tuple[bool, datetime.datetime | str]:
    """将给定的时间戳转换为 datetime.datetime 对象"""

    expr_dict = {
        "int": "不带毫秒时间戳",
        "float": "带毫秒时间戳",
    }
    expr = ucheck.args_check(expr_dict, date_text=date_text)
    if expr:
        return (False, expr)

    tmp_date = datetime.datetime.fromtimestamp(date_text)  # noqa: DTZ006
    return (True, tmp_date.astimezone(datetime.timezone.utc))


def validate_datetime(
    date_text: str,
    format_str: str = "%Y-%m-%d %H:%M:%S",
) -> bool:
    """检查传入的时间字符串是否符合传入的时间格式。
    时间格式详见https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
    """
    if not date_text and not format_str:
        return False
    flag, tmp_date = get_datatime_by_str(date_text, format_str)
    return not (flag is False or date_text != tmp_date.strftime(format_str))


def format_time(
    arg_time:
        None | float | str | datetime.datetime | datetime.date = None,
    dst_fmt: str = "%Y-%m-%d %H:%M:%S",
    src_fmt: str = "",
) -> None | str:
    """格式化时间戳或时间字符串为指定格式。

    参数
        arg_time(int|float|str|datetime.datetime|datetime.date):
            要格式化的时间戳。默认为当前时间戳。
        dst_fmt(str): 目标时间格式。默认为'%Y-%m-%d %H:%M:%S'。
        src_fmt(str): 原始时间格式。当 arg_time 为字符串时, 此参数必须指定。
            全部格式见: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes

    返回值(None|str)
        格式化后的时间, 若出现错误或异常, 则为 None
    """
    today = datetime.datetime.today().astimezone(datetime.timezone.utc)
    arg_time = today if arg_time is None else arg_time
    expr1 = ucheck.args_check(DATE_STRUCT_DICT, arg_time=arg_time)
    expr2 = ucheck.arg_check(str, dst_fmt=dst_fmt, src_fmt=src_fmt)

    if expr1 or expr2:
        return None
    if type(arg_time).__name__ in ("date", "datetime") and dst_fmt:
        return arg_time.strftime(dst_fmt)
    if type(arg_time).__name__ in ("int", "float") and dst_fmt:
        flag, tmp_date = get_datatime_by_timestamp(arg_time)
        if flag:
            return tmp_date.strftime(dst_fmt)
    elif type(arg_time).__name__ == "str" and dst_fmt and src_fmt:
        flag, tmp_date = get_datatime_by_str(arg_time, src_fmt)
        if flag:
            return tmp_date.strftime(dst_fmt)
    return None


def get_dates(
    end_date:
        None | float | str | datetime.datetime | datetime.date = None,
    start_date:
        None | float | str | datetime.datetime | datetime.date = None,
    date_type: str = "isholiday",
    src_fmt: str = "%Y-%m-%d",
) -> tuple[bool, bool | int | str | list]:
    """根据给定的日期类型, 获取相应的日期信息

    参数
        start_date(int|float|str|datetime.date|datetime.datetime):
            开始时间, 默认为现在。
        end_date(int|float|str|datetime.date|datetime.datetime):
            结束时间, 默认为现在。
            当结束时间和开始时间都为字符串类型时,
            时间格式需要一致, 必须均为 src_fmt 格式。
        date_type(str): 指定要获取的时间类型。默认为 isholiday。支持以下类型:
            isholiday: 判断结束时间是否为节假日。返回布尔类型: True/False。
            isworkday: 判断结束时间是否为工作日。返回布尔类型: True/False。
            year: 获取结束时间年份。返回整型数字。
            month: 获取结束时间月份。返回整型数字。
            day: 获取结束时间天数。返回整型数字。
            week: 获取结束时间是星期几。返回字符串: 星期一到星期天任意一个。
            year_week: 获取结束时间所在周是本年的第几周。返回整型数字。
            year_day: 获取结束时间是本年的第几天。返回整型数字。
            holidays: 获取开始时间到结束时间范围内的节假日。
                返回列表格式: 元素为 datetime.date。
            workdays: 获取开始时间到结束时间范围内的工作日。
                返回列表格式: 元素为 datetime.date。
        src_fmt(str): 原始时间格式。
            当且仅当 end_date 为字符串时, 此参数必须指定。
            全部格式见: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes

    返回值tuple(bool, bool|int|list|str)
        根据 date_type 返回相应的值。
    """

    this_year = datetime.datetime.now(tz=datetime.timezone.utc).year
    dst_fmt = "%Y-%m-%d"
    date_arg_dict = {
        "isholiday": "判断结束时间是否为节假日。返回布尔类型: True/False。",
        "isworkday": "判断结束时间是否为工作日。返回布尔类型: True/False。",
        "year": "获取结束时间年份。返回整型数字。",
        "month": "获取结束时间月份。返回整型数字。",
        "day": "获取结束时间天数。返回整型数字。",
        "week": "获取结束时间是星期几。返回字符串: 星期一到星期天任意一个。",
        "year_week": "获取结束时间所在周是本年的第几周。返回整型数字。",
        "year_day": "获取结束时间是本年的第几天。返回整型数字。",
        "holidays": (
            "获取开始时间到结束时间范围内的节假日。"
            "返回列表格式: 元素为 datetime.date。"
        ),
        "workdays": (
            "获取开始时间到结束时间范围内的工作日。"
            "返回列表格式: 元素为 datetime.date。"
        ),
    }

    err_list = [
        ucheck.args_check(
            date_arg_dict,
            check_type="type",
            date_type=date_type,
        ),
        ucheck.args_check(
            DATE_STRUCT_DICT,
            start_date=start_date,
            end_date=end_date,
        ),
    ]
    err_list = [err_info for err_info in err_list if err_info is not None]
    if err_list != []:
        return (False, "\n".join(err_list))

    def _get_date(
        arg_date: datetime.datetime, dst_fmt: str, src_fmt: str,
    ) -> tuple[bool, str | datetime.datetime]:
        dst_date = format_time(arg_date, dst_fmt=dst_fmt, src_fmt=src_fmt)
        if dst_date:
            flag, dst_date = get_datatime_by_str(dst_date, dst_fmt)
            if flag:
                return (True, dst_date)

            return (False, "时间格式不正确")

        return (False, "时间格式不正确")

    flag, start_date = _get_date(start_date, dst_fmt, src_fmt)
    if not flag:
        return (False, f"start_date {start_date}")
    flag, end_date = _get_date(end_date, dst_fmt, src_fmt)
    if not flag:
        return (False, f"end_date {end_date}")

    expr1 = date_type in ("isholiday", "isworkday", "holidays", "workdays")
    expr2 = end_date.year not in range(2004, this_year + 1)
    if expr1 and expr2:
        return (False, "节假日和工作日的判断只支持 2004 年(包含)到现在")

    result_dict = {
        "isholiday": bool(is_holiday(end_date)),
        "isworkday": bool(is_workday(end_date)),
        "year": end_date.year,
        "month": end_date.month,
        "day": end_date.day,
        "week": WEEK_DICT[end_date.timetuple().tm_wday],
        "year_week": end_date.isocalendar()[1],
        "year_day": end_date.timetuple().tm_yday,
        "holidays": [
            format_time(i, "%Y-%m-%d")
            for i in get_holidays(start_date, end_date)
        ],
        "workdays":[
            format_time(i, "%Y-%m-%d")
            for i in get_workdays(start_date, end_date)
        ],
    }

    result = result_dict.get(date_type)
    if result is None:
        return (False, f"方法: {date_type} 不在清单中")

    return (True, result)


if __name__ == "__main__":
    pass
