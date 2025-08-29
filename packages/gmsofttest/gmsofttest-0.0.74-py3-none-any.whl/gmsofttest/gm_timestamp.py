"""
Name : gm_timestamp_utils.py
Author  : 写上自己的名字
Contact : 邮箱地址
Time    : 2023-05-16 9:45
Desc:
"""

"""
Name : timestamphandler.py
Author  : 写上自己的名字
Contact : 邮箱地址
Time    : 2021/3/25 10:27
Desc: 根据调用时间，生成时间戳，精确到毫秒，用于生成文件名
"""

# 年-月-日 时:分:秒
import datetime
import time

nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
# 年-月-日
dayTime = datetime.datetime.now().strftime('%Y-%m-%d')
# 时:分:秒
hourTime = datetime.datetime.now().strftime('%H:%M:%S.%f')
file_name = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')


def create_current_timestamp_filename(name, file_format):
    """生成当前时间的文件名
    :param name: 文件名
    :param file_format:  当前时间戳
    :return:
    """
    create_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
    my_file_name = name + "_" + create_time + file_format
    return my_file_name


def now_timestamp():
    create_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    return create_time

def today_start_timestamp():
    """获取调用时间当天0点的时间戳"""
    day_time = int(
        round(
            time.mktime(
                datetime.date.today().timetuple())) *
        1000)
    return day_time

def today_end_timestamp():
    """获取调用时间当天23点59分59秒的时间戳"""
    now = datetime.datetime.now()
    # 今天0点
    zerotoday = now - datetime.timedelta(hours=now.hour,
                                         minutes=now.minute,
                                         seconds=now.second,
                                         microseconds=now.microsecond)
    # 偏移23:59:59
    lasttoday = zerotoday + \
                datetime.timedelta(hours=23, minutes=59, seconds=59)
    # 解析为unix时间戳
    todayend = int(round(time.mktime(lasttoday.timetuple())) * 1000)
    return todayend


#
def after_timestamp(n):
    """获取n天后23小时59分59秒时间戳"""
    hours = int((n + 1) * 24) - 1
    now = datetime.datetime.now()
    zerotoday = now - datetime.timedelta(hours=now.hour,
                                         minutes=now.minute,
                                         seconds=now.second,
                                         microseconds=now.microsecond)
    dd = zerotoday + datetime.timedelta(hours=hours, minutes=59, seconds=59)
    aftertimestemp = int(round(time.mktime(dd.timetuple())) * 1000)
    # 返回第n天后0点时间戳
    return aftertimestemp


def get_current_year_first_day_timestatmp():
    """获取本年度第1天0点的时间戳"""
    now = datetime.datetime.now()
    dd = datetime.datetime(now.year, 1, 1)
    firstdaytimestamp = int(round(time.mktime(dd.timetuple())) * 1000)
    # 返回第n天后0点时间戳
    return firstdaytimestamp


if __name__ == '__main__':
    print(today_start_timestamp())
    print(after_timestamp(3))
    print(create_current_timestamp_filename('hello', '.txt'))
