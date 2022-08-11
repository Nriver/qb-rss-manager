import re


def try_convert_time(s, date_auto_zfill=1):
    """
    简单粗暴的字符串转换年月
    将以下格式的时间
    2021.11
    2021-11
    2021/11
    自动转换成 2021年11月
    """
    res = re.match(r'^(\d{4})[.\-_\\/](\d{1,2})$', s)
    if res:
        year = str(res[1])
        month = str(res[2])

        if date_auto_zfill == 1:
            month = month.zfill(2)
        s = f'{year}年{month}月'
    return s
