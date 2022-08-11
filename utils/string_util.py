import fnmatch
import re


def try_split_date_and_name(s):
    if not s or ' ' not in s:
        return '', s
    tmp_date, tmp_name = s.split(' ', 1)
    pat = '^\d{4}年\d{1,2}月$'
    res = re.match(pat, tmp_date)
    if res:
        return res[0], tmp_name
    return '', s


def wildcard_match_check(s, keywords_groups_string):
    # 多组关键字用 | 隔开
    # 单组关键字内 多个条件用空格隔开
    # 支持通配符匹配

    # logger.info(f'测试字符 {s}')
    # logger.info(f'匹配关键字 {keywords_groups_string}')

    # 关键字分割，不对 \| 进行分割
    # https://stackoverflow.com/questions/18092354/python-split-string-without-splitting-escaped-character
    keywords_groups = re.split(r'(?<!\\)\|', keywords_groups_string)

    # logger.info(f'关键字分组 {keywords_groups}')

    group_results = []
    for keywords in keywords_groups:
        # 防止空格造成空匹配
        keywords = keywords.strip()
        if not keywords:
            continue

        # 单组关键字必须全部满足
        match_list = []
        for keyword in keywords.split():
            # logger.info(keyword)
            # 防止空格造成空匹配
            keyword = keyword.strip()
            if not keyword:
                continue
            # 关键字匹配
            if keyword.lower() in s.lower():
                match_list.append(True)
                continue
            # 通配符匹配
            if fnmatch.fnmatch(s.lower(), keyword.lower()):
                match_list.append(True)
                continue
            match_list.append(False)

        group_results.append(all(match_list))

    return any(group_results)
