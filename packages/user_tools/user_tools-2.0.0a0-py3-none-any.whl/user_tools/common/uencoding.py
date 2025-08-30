#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @Author   : Skypekey
# @FileName : uencoding
# @Time     : 2024-05-02 22:35:26
"""encoding 模块"""

from __future__ import annotations

from user_tools.common import ucheck

__FILENAME__ = "uencoding"
__CODING_DICT = {
    # https://docs.python.org/3.11/library/codecs.html#standard-encodings
    "base": {
        "ascii": ["646", "us-ascii"],
        "big5": ["big5-tw", "csbig5"],
        "big5hkscs": ["big5-hkscs", "hkscs"],
        "cp037": ["ibm037", "ibm039"],
        "cp1006": [],
        "cp1026": ["ibm1026"],
        "cp1125": ["1125", "ibm1125", "cp866u", "ruscii"],
        "cp1140": ["ibm1140"],
        "cp1250": ["windows-1250"],
        "cp1251": ["windows-1251"],
        "cp1252": ["windows-1252"],
        "cp1253": ["windows-1253"],
        "cp1254": ["windows-1254"],
        "cp1255": ["windows-1255"],
        "cp1256": ["windows-1256"],
        "cp1257": ["windows-1257"],
        "cp1258": ["windows-1258"],
        "cp273": ["273", "ibm273", "csibm273"],
        "cp424": ["ebcdic-cp-he", "ibm424"],
        "cp437": ["437", "ibm437"],
        "cp500": ["ebcdic-cp-be", "ebcdic-cp-ch", "ibm500"],
        "cp720": [],
        "cp737": [],
        "cp775": ["ibm775"],
        "cp850": ["850", "ibm850"],
        "cp852": ["852", "ibm852"],
        "cp855": ["855", "ibm855"],
        "cp856": [],
        "cp857": ["857", "ibm857"],
        "cp858": ["858", "ibm858"],
        "cp860": ["860", "ibm860"],
        "cp861": ["861", "cp-is", "ibm861"],
        "cp862": ["862", "ibm862"],
        "cp863": ["863", "ibm863"],
        "cp864": ["ibm864"],
        "cp865": ["865", "ibm865"],
        "cp866": ["866", "ibm866"],
        "cp869": ["869", "cp-gr", "ibm869"],
        "cp874": [],
        "cp875": [],
        "cp932": ["932", "ms932", "mskanji", "ms-kanji"],
        "cp949": ["949", "ms949", "uhc"],
        "cp950": ["950", "ms950"],
        "euc_jis_2004": ["jisx0213", "eucjis2004"],
        "euc_jisx0213": ["eucjisx0213"],
        "euc_jp": ["eucjp", "ujis", "u-jis"],
        "euc_kr": [
            "euckr",
            "korean",
            "ksc5601",
            "ks_c-5601",
            "ks_c-5601-1987",
            "ksx1001",
            "ks_x-1001",
        ],
        "gb18030": ["gb18030-2000"],
        "gb2312": [
            "chinese",
            "csiso58gb231280",
            "euc-cn",
            "euccn",
            "eucgb2312-cn",
            "gb2312-1980",
            "gb2312-80",
            "iso-ir-58",
        ],
        "gbk": ["936", "cp936", "ms936"],
        "hz": ["hzgb", "hz-gb", "hz-gb-2312"],
        "iso2022_jp": ["csiso2022jp", "iso2022jp", "iso-2022-jp"],
        "iso2022_jp_1": ["iso2022jp-1", "iso-2022-jp-1"],
        "iso2022_jp_2": ["iso2022jp-2", "iso-2022-jp-2"],
        "iso2022_jp_2004": ["iso2022jp-2004", "iso-2022-jp-2004"],
        "iso2022_jp_3": ["iso2022jp-3", "iso-2022-jp-3"],
        "iso2022_jp_ext": ["iso2022jp-ext", "iso-2022-jp-ext"],
        "iso2022_kr": ["csiso2022kr", "iso2022kr", "iso-2022-kr"],
        "iso8859_10": ["iso-8859-10", "latin6", "l6"],
        "iso8859_11": ["iso-8859-11", "thai"],
        "iso8859_13": ["iso-8859-13", "latin7", "l7"],
        "iso8859_14": ["iso-8859-14", "latin8", "l8"],
        "iso8859_15": ["iso-8859-15", "latin9", "l9"],
        "iso8859_16": ["iso-8859-16", "latin10", "l10"],
        "iso8859_2": ["iso-8859-2", "latin2", "l2"],
        "iso8859_3": ["iso-8859-3", "latin3", "l3"],
        "iso8859_4": ["iso-8859-4", "latin4", "l4"],
        "iso8859_5": ["iso-8859-5", "cyrillic"],
        "iso8859_6": ["iso-8859-6", "arabic"],
        "iso8859_7": ["iso-8859-7", "greek", "greek8"],
        "iso8859_8": ["iso-8859-8", "hebrew"],
        "iso8859_9": ["iso-8859-9", "latin5", "l5"],
        "johab": ["cp1361", "ms1361"],
        "koi8_r": [],
        "koi8_t": [],
        "koi8_u": [],
        "kz1048": ["kz_1048", "strk1048_2002", "rk1048"],
        "latin_1": [
            "iso-8859-1",
            "iso8859-1",
            "8859",
            "cp819",
            "latin",
            "latin1",
            "l1",
        ],
        "mac_cyrillic": ["maccyrillic"],
        "mac_greek": ["macgreek"],
        "mac_iceland": ["maciceland"],
        "mac_latin2": ["maclatin2", "maccentraleurope", "mac_centeuro"],
        "mac_roman": ["macroman", "macintosh"],
        "mac_turkish": ["macturkish"],
        "ptcp154": ["csptcp154", "pt154", "cp154", "cyrillic-asian"],
        "shift_jis": ["csshiftjis", "shiftjis", "sjis", "s_jis"],
        "shift_jis_2004": ["shiftjis2004", "sjis_2004", "sjis2004"],
        "shift_jisx0213": ["shiftjisx0213", "sjisx0213", "s_jisx0213"],
        "utf_16": ["u16", "utf16"],
        "utf_16_be": ["utf-16be"],
        "utf_16_le": ["utf-16le"],
        "utf_32": ["u32", "utf32"],
        "utf_32_be": ["utf-32be"],
        "utf_32_le": ["utf-32le"],
        "utf_7": ["u7", "unicode-1-1-utf-7"],
        "utf_8": ["u8", "utf", "utf8", "cp65001"],
        "utf_8_sig": [],
    },
    # https://docs.python.org/3.11/library/codecs.html#text-encodings
    "text": {
        "idna": [],
        "mbcs": ["ansi", "dbcs"],
        "oem": [],
        "palmos": [],
        "punycode": [],
        "raw_unicode_escape": [],
        "undefined": [],
        "unicode_escape": [],
        # https://docs.python.org/3.11/library/codecs.html#text-transforms
        "rot_13": ["rot13"],
    },
    # https://docs.python.org/3.11/library/codecs.html#binary-transforms
    "binary": {
        "base64_codec": ["base64", "base_64"],
        "bz2_codec": ["bz2"],
        "hex_codec": ["hex"],
        "quopri_codec": ["quopri", "quotedprintable", "quoted_printable"],
        "uu_codec": ["uu"],
        "zlib_codec": ["zip", "zlib"],
    },
}
CODINGS = __CODING_DICT["base"]
CODINGS.update(__CODING_DICT["text"])
CODINGS.update(__CODING_DICT["binary"])
PY3_9_CODINGS = CODINGS
PY3_10_CODINGS = CODINGS
PY3_11_CODINGS = CODINGS


def get_encoding(arg_encoding: str) -> tuple[bool, str]:
    """校验并获取标准编码"""
    err_info = ucheck.arg_check(str, arg_encoding=arg_encoding)
    if err_info:
        return (False, err_info)

    arg_encoding = arg_encoding.replace("-", "_")
    if arg_encoding.lower() in CODINGS:
        return (True, arg_encoding)

    for k, v in CODINGS.items():
        if arg_encoding.lower() in v:
            return (True, k)
    return (False, f"{arg_encoding} 不是支持的编码方式")


if __name__ == "__main__":
    pass
