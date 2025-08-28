from upplib import *


def format_milliseconds(time_str):
    # 匹配小数点后的数字（至少1位），并捕获时区部分
    # param：2025-08-14T12:53:00.05382312323+07:00
    # return：2025-08-14T12:53:00.0538+07:00
    return re.sub(r'\.(\d+)([+-].*)?', lambda m: f".{m.group(1)[:4]}{m.group(2) or ''}", time_str)


def get_log_msg(contents: dict) -> str:
    """
    获得日志
    """
    _time_ = None
    if '_time_' in contents:
        _time_ = format_milliseconds(contents['_time_'])
    content = None
    if 'content' in contents:
        content = contents['content']
    if content is None and 'message' in contents:
        content = contents['message']
    if content is not None and len(str(content).split(' ')) >= 2:
        time_str = ' '.join(str(content).split(' ')[0:2])
        time_1 = to_datetime(time_str, error_is_none=True)
        if time_1 is not None:
            content = content[len(time_str):]
    _time_ = '' if _time_ is None else _time_
    # if content is None:
    #     print('ok')
    return str(_time_) + ' ' + str(content)
