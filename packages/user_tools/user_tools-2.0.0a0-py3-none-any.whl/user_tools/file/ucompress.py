#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @Author   : Skypekey
# @FileName : ucompress
# @Time     : 2024-04-20 17:02:05

"""压缩文件模块"""

from __future__ import annotations

import lzma
import pathlib
import tarfile
from typing import TYPE_CHECKING
import zipfile

import py7zr
import rarfile

from user_tools.common import ucheck
from user_tools.file import upath

if TYPE_CHECKING:
    from collections.abc import Buffer

__FILENAME__ = "ucompress"
_BASE_TYPE_LIST = ["zip", "rar", "7z"]
_TAR_TYPE_LIST = ["tgz", "tar", "gz"]
COMPRESS_TYPE_LIST = _BASE_TYPE_LIST + _TAR_TYPE_LIST


class _UZip:
    """zip 压缩文件的操作对象"""

    def __init__(self, arg_path: pathlib.Path, password: str) -> None:
        """参数
        arg_path(pathlib.Path|str): 压缩文件路径。
        password(str): 压缩文件密码, 默认为空。
        """
        self.file_path = str(arg_path)
        self.password = password
        self.is_encrypted = bool(
            zipfile.ZipInfo(self.file_path).flag_bits & 0x1,
        )
        self.password = None if self.is_encrypted is False else self.password

        self.filelist = self.__getnames()
        self.flag = bool(self.filelist)

    def __str_decode(self, file_name: Buffer | str) -> str:
        """将乱码的中文编码为 UTF-8"""
        try:
            path_name = file_name.decode("UTF-8")
        except Exception:  # noqa: BLE001
            path_name = file_name.encode("cp437").decode("GBK")
            path_name = path_name.encode("UTF-8").decode("UTF-8")
        return path_name

    def __getnames(self) -> list:
        with zipfile.ZipFile(self.file_path) as tmp_compress:
            tmp_compress.setpassword(self.password)
            return [self.__str_decode(i) for i in tmp_compress.namelist()]

    def extract(self, dst_path: str, filename: list) -> None:
        with zipfile.ZipFile(self.file_path) as tmp_compress:
            tmp_compress.setpassword(self.password)
            for i in tmp_compress.filelist:
                i.filename = self.__str_decode(i.filename)
                if i.filename in filename:
                    tmp_compress.extract(i, dst_path)

    def extractall(self, dst_path: str) -> None:
        self.extract(dst_path, self.filelist)


class _URar:
    """rar 压缩文件的操作对象"""

    def __init__(self, arg_path: pathlib.Path, password: str) -> None:
        """参数
        arg_path(pathlib.Path|str): 压缩文件路径。
        password(str): 压缩文件密码, 默认为空。
        """
        self.file_path = str(arg_path)
        self.password = password
        self.filelist = self.__getinfo()
        self.flag = bool(self.filelist)

    def __getinfo(self) -> list:
        with rarfile.RarFile(self.file_path) as tmp_compress:
            self.is_encrypted = tmp_compress.needs_password()
            self.password = (
                None if self.is_encrypted is False else self.password
            )
            tmp_compress.setpassword(self.password)
            return tmp_compress.namelist()

    def extract(self, dst_path: str, filename: list) -> None:
        with rarfile.RarFile(self.file_path) as tmp_compress:
            tmp_compress.setpassword(self.password)
            for i in self.filelist:
                if i in filename:
                    tmp_compress.extract(i, dst_path)

    def extractall(self, dst_path: str) -> None:
        return self.extract(dst_path, self.filelist)


class _UTar:
    """Tar 类型压缩文件的操作对象"""

    def __init__(self, arg_path: pathlib.Path) -> None:
        """参数
        arg_path(pathlib.Path|str): 压缩文件路径。
        """
        self.file_path = str(arg_path)

        self.filelist = self.__getinfo()
        self.flag = bool(self.filelist)
        self.is_encrypted = False
        self.password = None

    def __getinfo(self) -> list | None:
        with tarfile.open(self.file_path) as tmp_compress:
            return tmp_compress.getnames()

    def extract(self, dst_path: str, filename: list) -> None:
        with tarfile.open(self.file_path) as tmp_compress:
            for i in tmp_compress.getnames():
                if i in filename:
                    tmp_compress.extract(i, dst_path)

    def extractall(self, dst_path: str) -> None:
        return self.extract(dst_path, self.filelist)


class _U7z:
    """7z 压缩文件的操作对象"""

    def __init__(self, arg_path: pathlib.Path, password: str) -> None:
        """参数
        arg_path(pathlib.Path|str): 压缩文件路径。
        password(str): 压缩文件密码, 默认为空。
        """
        self.file_path = str(arg_path)
        self.password = password
        self.__get_info()

    def __get_info(self) -> None:
        """获取 7z 对象"""
        self.flag = False
        self.filelist = []
        self.is_encrypted = False
        try:
            with py7zr.SevenZipFile(
                self.file_path,
                password=None,
            ) as tmp_compress:
                self.filelist = tmp_compress.getnames()
            self.flag = True
        except py7zr.PasswordRequired:
            self.is_encrypted = True

        if self.flag is False:
            try:
                with py7zr.SevenZipFile(
                    self.file_path,
                    password=self.password,
                ) as tmp_compress:
                    self.filelist = tmp_compress.getnames()
                self.flag = True
            except py7zr.PasswordRequired:
                pass
            except lzma.LZMAError:
                pass

        if self.is_encrypted is False:
            self.password = None

    def extract(self, dst_path: str, filename: list) -> None:
        with py7zr.SevenZipFile(
            self.file_path,
            password=self.password,
        ) as tmp_compress:
            tmp_compress.extract(dst_path, filename)

    def extractall(self, dst_path: str) -> None:
        with py7zr.SevenZipFile(
            self.file_path,
            password=self.password,
        ) as tmp_compress:
            tmp_compress.extractall(dst_path)  # noqa: S202


class UCompress:
    """压缩文件的操作对象"""

    def __init__(
        self,
        arg_path: pathlib.Path | str,
        password: str = "",
    ) -> None:
        """参数
        arg_path(pathlib.Path|str): 压缩文件路径。
        password(str): 压缩文件密码, 默认为空。
        """

        err_str = ", ".join(i for i in COMPRESS_TYPE_LIST)
        err_msg = (
            f"路径: {arg_path!s} 不是支持的压缩文件类型。"
            f"支持的压缩文件类型如下: {err_str}"
        )
        if not is_compress_file(arg_path, return_type=True):
            raise TypeError(err_msg)

        self.file_type = is_compress_file(arg_path, return_type=True)
        self.compress_file = pathlib.Path(arg_path)

        if ucheck.arg_check(str, password=password):
            raise TypeError(ucheck.arg_check(str, password=password))

        self.filename = self.compress_file.name
        self.basename = self.filename.removesuffix(f".{self.file_type}")
        self.parent = self.compress_file.parent
        self.filepath = str(self.compress_file)
        self.password = password.strip()

        if self.file_type == "zip":
            self.obj = _UZip(self.compress_file, self.password)
        elif self.file_type == "rar":
            self.obj = _URar(self.compress_file, self.password)
        elif self.file_type == "7z":
            self.obj = _U7z(self.compress_file, self.password)
        elif self.file_type in _TAR_TYPE_LIST:
            self.obj = _UTar(self.compress_file)

        self.is_encrypted = self.obj.is_encrypted
        self.password = self.obj.password if self.obj.password else ""
        if self.obj.flag is False:
            if self.is_encrypted:
                err_msg = "请提供压缩包正确的解压密码"
                raise ValueError(err_msg)

            err_msg = "不合法或不支持的压缩文件"
            raise ValueError(err_msg)

        self.filelist = self.obj.filelist

    def _check_file(
        self,
        dst_path: pathlib.Path | str,
        src_filename: list,
        *,
        rewrite: bool,
    ) -> None | str:
        """检查待解压的文件是否存在"""
        expr1 = ucheck.arg_check(list, src_filename=src_filename)
        expr2 = ucheck.arg_check(bool, rewrite=rewrite)
        err_msg = "\n".join(filter(None, [expr1, expr2]))

        if err_msg:
            return err_msg

        if not src_filename:
            return "src_filename 必须为 list 对象, 且不能为空!"

        if not dst_path:
            self.dst_path = self.parent / self.basename
        else:
            flag, info = upath.path_check(dst_path)
            if not flag:
                raise TypeError(info)
            self.dst_path = pathlib.Path(dst_path)

        if self.dst_path.exists() and not self.dst_path.is_dir():
            return "解压路径不为目录"

        err_list = [i for i in src_filename if (self.dst_path / i).exists()]

        if err_list:
            if rewrite:
                for i in err_list:
                    i.unlink()
            else:
                return (
                    "以下文件已存在, 若需覆盖解压, "
                    f"请指定 rewrite 为 True: {'、'.join(err_list)}"
                )
        return None

    def extract(
        self,
        src_filename: list,
        dst_path: pathlib.Path | str = "",
        *,
        rewrite: bool = False,
    ) -> None:
        """解压指定文件

        参数
            src_filename(list): 要解压的文件名
        dst_path(pathlib.Path|str): 解压目的路径, 默认为空, 即文件父目录。
        """
        err_list = [i for i in src_filename if i not in self.filelist]

        if err_list:
            return f"以下文件不在压缩包中, 请确认: {'、'.join(err_list)}"

        err_info = self._check_file(dst_path, src_filename, rewrite=rewrite)
        if err_info:
            return err_info

        self.obj.extract(self.dst_path, src_filename)
        return None

    def extractall(
        self,
        dst_path: pathlib.Path | str = "",
        *,
        rewrite: bool = False,
    ) -> None:
        """解压所有文件

        参数
        dst_path(pathlib.Path|str) 解压目的路径, 默认为空, 即文件父目录。
        """
        err_info = self._check_file(dst_path, self.filelist, rewrite=rewrite)
        if err_info:
            return err_info

        self.obj.extractall(self.dst_path)  # noqa: S202
        return None


def is_compress_file(
    arg_path: pathlib.Path | str,
    *,
    return_type: bool = False,
) -> bool | str:
    """判断是否为支持的压缩文件, 若 return_type 为 True, 返回压缩文件类型"""
    _tmp_type = ""
    file_path = str(arg_path)
    flag, file_type = upath.file_type_get(file_path)
    if flag and file_type is not None:
        expr1 = not zipfile.is_zipfile(file_path)
        expr2 = not rarfile.is_rarfile(file_path)
        expr3 = not py7zr.is_7zfile(file_path)
        expr4 = not tarfile.is_tarfile(file_path)
        _tmp_type = "" if expr1 and expr2 and expr3 and expr4 else file_type
        _tmp_type = "" if file_type not in COMPRESS_TYPE_LIST else file_type

    if return_type:
        return _tmp_type

    return bool(_tmp_type)


if __name__ == "__main__":
    pass
