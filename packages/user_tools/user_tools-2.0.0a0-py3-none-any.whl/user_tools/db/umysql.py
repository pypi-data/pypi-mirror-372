#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @Author   : Skypekey
# @FileName : umysql
# @Time     : 2024-04-23 21:29:44
"""MySQL 模块"""

from __future__ import annotations

import inspect
import math
import traceback

import pymysql

__FILENAME__ = "umysql"


class UserMySQL:
    def __init__(self, method: str = "host", **kwargs) -> None:
        """
        参数
            method(str): 数据库认证方式, 仅支持 host 和 socket
            kwargs: 形如下面的字典
                kwargs = {
                    # required, where use host to access database.
                    "host": "host",
                    "user": "user", # required
                    "password": "password", # required
                    "port": 3306, # optional, default is 3306
                    "database": "mysql", # optional
                    # required, where use socket to access database.
                    "socket": "/tmp/mysql.sock"
                }
        """
        self.info = kwargs
        self.method = method

    def __verify(self) -> tuple[bool, str | dict]:
        """Initialize database authentication information.

        返回值 tuple(bool, str|dict):
            正常, 返回数据库连接所用信息
            异常, 返回异常信息
        """
        arg_list = ["host", "user", "password", "port", "database", "socket"]

        err_info = ""

        if self.method == "host":
            arg_list.pop(arg_list.index("socket"))
        elif self.method == "socket":
            arg_list.pop(arg_list.index("host"))
            arg_list.pop(arg_list.index("port"))
        else:
            err_info = "数据库认证方式, 仅支持 host 和 socket"

        if err_info:
            return (False, err_info)

        err_list = [
            f"{i} 必须提供, 且不能为空"
            for i in arg_list
            if i not in self.info or not self.info[i]
        ]

        if err_list:
            return (False, "\n".join(err_list))

        return (True, self.info)

    def __connect(self) -> None | str:
        """Connect to database."""
        flag, result = self.__verify()
        if flag:
            self.db_conn = pymysql.connect(**result)
            self.db_cur = self.db_conn.cursor(pymysql.cursors.dictCursor)
        else:
            return result
        return None

    def __close(self) -> None:
        self.db_cur.close()
        self.db_conn.close()

    def __check(self, sql: str, *, isquery: bool = True) -> tuple[bool, str]:
        err_info = self.__connect()
        if not err_info:
            isselect = sql.lower().startswith("select")
            into = "into" in sql.lower().split(" ")
            if isquery and (not isselect or into):
                err_info = "当 isquery 为 True 时, 仅允许使用 SELECT 语句"
            elif not isquery and isselect and not into:
                err_info = (
                    "当 isquery 为 False 且 SQL 以 SELECT 开头时, "
                    "SQL 必须包含 INTO 关键字"
                )

        if err_info:
            return (False, err_info)

        return (True, "")

    def query(self, sql: str) -> tuple[bool, str | dict]:
        """Query data from the database.

        :param sql(str): It's a sql statement.
        """
        err_info = ""
        data = ""

        flag, err_info = self.__check(sql)
        if flag:
            try:
                self.db_cur.execute(sql)
                data = self.db_cur.fetchall()
            except Exception:  # noqa: BLE001
                err_info = (
                    f"sql statement is {sql}.\n exception info is:\n"
                    f"{traceback.format_exc().strip()}"
                )
            finally:
                self.__close()

        if err_info:
            return (False, err_info)

        return (True, data)

    def noquery(self, sql: str) -> tuple[bool, str]:
        """Change the data in the database.

        :param sql(str): It's a sql statement.
        """
        err_info = ""
        data = ""

        flag, err_info = self.__check(sql, isquery=False)
        if flag:
            try:
                self.db_cur.execute(sql)
                self.db_conn.commit()
            except Exception:  # noqa: BLE001
                self.db_conn.rollback()
                err_info = (
                    f"sql statement is {sql}.\n exception info is:\n"
                    f"{traceback.format_exc().strip()}"
                )
            finally:
                self.__close()

        if err_info:
            return (False, err_info)

        return (True, data)

    def run_sql(
        self,
        sql: str,
        data: list | None = None,
        *,
        query: bool = False,
        isdel: bool = False,
    ) -> tuple[bool, dict | str]:
        """在项目数据库查询和写入。

        参数
            sql(str) 需要执行的 SQL
            data(list|None) 若不为查询, 则需要提供待更新数据
            query(bool) 是否为查询语句
            isdel(bool) 是否为删除语句
        """
        method_name = inspect.currentframe().f_back.f_code.co_name
        try:
            data_step = 10000
            data = [] if data is None else data
            if query:
                _tmpflag, _tmpinfo = self.query(sql)
            elif isdel:
                _tmpflag, _tmpinfo = self.noquery(sql)
            else:
                length = math.ceil(len(data) / data_step)
                for i in range(length):
                    newdata = data[i * data_step : (i + 1) * data_step]
                    if len(newdata) == 0:
                        break
                    dstsql = f'{sql} {",".join(newdata)};'
                    _tmpflag, _tmpinfo = self.noquery(dstsql)
                    if not _tmpflag:
                        break
        except Exception:  # noqa: BLE001
            return (
                False,
                (f"[{__FILENAME__}]:{method_name} 出现异常: "
                f"{traceback.format_exc().strip()}"),
            )
        else:
            return (_tmpflag, _tmpinfo)


if __name__ == "__main__":
    pass
