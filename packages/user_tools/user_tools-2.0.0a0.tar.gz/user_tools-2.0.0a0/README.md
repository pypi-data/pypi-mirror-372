# user_tools

一些个人常用的模块。
[The English README](README_EN.md)

> **注意:**
>
> *user_tools v2.0.0 以上版本与之前版本代码完全不一致，若正在使用旧版本代码，请指定 user_tools<=2.0.0*
>
> *当前代码为进行完整测试，可能存在一些 bug，会在后续使用中进行处理*
>
> *以下文件中的代码可能存在风险，使用时请提前检查安全风险。*
> `user_tools.common.ucmd.py`: 未对待执行的命令进行安全检查。
> `user_tools.db.umysql.py`: 未对待执行的 SQL 进行安全检查
> `user_tools.file.ucompress.py`: 未对压缩包文件进行检查。尤其在 Unix 系统使用 tarfile 插件时需要注意
> `user_tools.file`: 所有对文件的修改，都允许删除或强行覆盖，使用时需要注意。

## 目录

- [user\_tools](#user_tools)
  - [目录](#目录)
  - [背景](#背景)
  - [安装方式](#安装方式)
  - [使用方法](#使用方法)
  - [相关项目](#相关项目)
  - [开源协议](#开源协议)
  - [待办](#待办)

## 背景

- 在项目开发过程中, 涉及很多相同的功能, 每次编写相同的代码很浪费时间, 且并不是每次都能想到具体的实现代码, 因此开发了这个 Python 模块, 包含了常用的一些方法。

## 安装方式

- 由于此模块已发布到 PyPi, 所以可以直接使用 pip 进行安装, 命令为: `pip install user_tools`

## 使用方法

- 这是一个 `user_tools.common.utime` 的使用示例:

```Python
from user_tools.common import utime

# 输出给定的时间是否符合给定的时间格式, 默认时间格式为 %Y-%m-%d %H:%M:%S
is_time = utime.validate_datetime('2024-01-01 10:10:10')
```

## 相关项目

- 暂无。若有已知被使用的开源项目, 会在这里标注

> **注意：**
>
> 可能存在已被使用的开源代码或基于开源代码进行的二次开发。因本工具主要方便个人使用, 且开源代码来源未知, 所以未注明具体来源
> 如果您认为侵权, 请通过邮件或 GitHub 联系我删除。
> 如果我知道代码的来源, 我会加以说明。


## 开源协议

- 此项目使用的开源协议为: GNU LGPLv3

## 待办

- `user_tools.network.ussh`: 未实现

- `user_tools.db`: 增加 sqlite、ck 查询方法

- `user_tools.file.uexcel`: 增加写文件/读文件方法，并且独立单个 Sheet 写入方法

- `user_tools.file.ufile`: 增加文件清理逻辑
- `user_tools.file.ufile`: 中需要考虑读写的换行符问题。同时增加入参，用于指定是否需要对每行数据进行 strip

- `user_tools.file.upath`: 增加文件查找功能, 参考 path_get 方法, 增加 ignore_dict 参数

- `user_tools.network`: 新建 uapi.py 文件, 构建默认 API 方法

- `user_tools.network.unet`: 增加网络校验功能, 如端口检测, ping 检测, 后续增加 IP 信息的方法, 如CIDR地址格式, 地址排序等等。
