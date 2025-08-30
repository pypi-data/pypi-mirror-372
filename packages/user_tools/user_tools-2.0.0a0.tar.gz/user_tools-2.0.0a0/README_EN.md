# user_tools

- Some personally used modules.

> **Note:**
>
> **English is not my native language, so the English version is from the machine translation, please excuse typing errors.**
>
> *user_tools v2.0.0 and above are completely incompatible with previous versions. If you are using older version code, please specify user_tools<=2.0.0*
>
> *The current code has not undergone complete testing and may contain some bugs, which will be addressed during subsequent usage.*
>
> *The code in the following files may pose potential risks. Please check for security risks before use.*
> `user_tools.common.ucmd.py`: No security checks are performed on commands to be executed.
> `user_tools.db.umysql.py`: No security checks are performed on SQL queries to be executed.
> `user_tools.file.ucompress.py`: No checks are performed on compressed files. Special attention is required when using the tarfile module on Unix systems.
> `user_tools.file`: All file modification operations allow deletion or forced overwriting. Please exercise caution when using these functions.

## Catalog

- [user\_tools](#user_tools)
  - [Catalog](#catalog)
  - [Background](#background)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Related Projects](#related-projects)
  - [Open Source Protocol](#open-source-protocol)
  - [TODO](#todo)

## Background

- In the process of project development, many of the same functions are involved, writing the same code every time is a waste of time, and it is not always possible to think of specific implementation code, so this Python module was developed, including some common methods.

## Installation

- Since this module has been published to PyPi, it can be installed directly with pip, with the command: `pip install user_tools`

## Usage

- This is an example of `user_tools.common.utime`

```Python
from user_tools.common import utime

# Verify if the provided time matches the given time format (default: %Y-%m-%d %H:%M:%S)
is_time = utime.validate_datetime('2024-01-01 10:10:10')
```

## Related Projects

- Not yet.If an open source project is known to be used, it will be marked here

> **Note:**
>
> Some modules may be open source or secondary development based on open source code. Because this tool is mainly convenient for personal use, and the source of the open source code is unknown, so the specific source is not indicated
> If you think it is infringing, please contact me by email or GitHub to delete.
> If I know the source of the code, I will explain it.

## Open Source Protocol

- The open source protocol used for this project is: GNU LGPLv3.

## TODO

- `user_tools.network.ussh`: Not implemented

- `user_tools.db`: Add SQLite and ClickHouse query methods

- `user_tools.file.uexcel`: Add read/write file methods, and implement independent single Sheet writing methods

- `user_tools.file.ufile`: Add file cleanup logic
- `user_tools.file.ufile`: Consider line break handling in read/write operations. Also add parameters to specify whether to perform strip() on each line of data

- `user_tools.file.upath`: Add file search functionality, reference the path_get method and add an ignore_dict parameter

- `user_tools.network`: Create new uapi.py file to implement default API methods

- `user_tools.network.unet`: Add network validation features such as port detection and ping testing. Subsequent updates will include IP information methods such as CIDR format validation and address sorting.
