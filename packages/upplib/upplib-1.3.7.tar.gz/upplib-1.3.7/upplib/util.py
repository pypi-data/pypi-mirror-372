from upplib import *


def format_milliseconds(time_str):
    # 匹配小数点后的数字（至少1位），并捕获时区部分
    # param：2025-08-14T12:53:00.05382312323+07:00
    # return：2025-08-14T12:53:00.0538+07:00
    return re.sub(r'\.(\d+)([+-].*)?', lambda m: f".{m.group(1)[:4]}{m.group(2) or ''}", time_str)


def get_log_msg(contents: dict, time_is_necessary: bool = False) -> str:
    """
    time_is_necessary: 日志中的时间参数,是否是必须的
    获得日志
    """
    # time
    _time_ = None
    if '_time_' in contents:
        _time_ = format_milliseconds(contents['_time_'])
    if _time_ is None and 'time' in contents:
        _time_ = format_milliseconds(contents['time'])

    # level
    level = None
    if 'level' in contents:
        level = contents['level']

    # content
    content = None
    if 'content' in contents:
        content = contents['content']
    if content is None and 'message' in contents:
        content = contents['message']
    if content is not None and len(str(content).split(' ')) >= 2:
        time_str = ' '.join(str(content).split(' ')[0:2])
        time_1 = to_datetime(time_str, error_is_none=True)
        if time_1 is not None:
            content = content[len(time_str):].strip()
        else:
            if not time_is_necessary:
                # 如果 content 中，没有时间，那就把默认的时间，去掉
                _time_ = None

    return ' '.join(filter(lambda s: s is not None, [_time_, level, content]))
