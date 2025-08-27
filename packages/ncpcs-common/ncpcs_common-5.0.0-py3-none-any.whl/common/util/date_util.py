import re
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

num_dict = {'一': '1', '两': '2', '二': '2', '三': '3', '四': '4', '五': '5', '六': '6', '七': '7', '八': '8', '九': '9',
            '十': '10', '壹': '1', '贰': '2', '叁': '3', '肆': '4', '伍': '5', '陆': '6', '柒': '7', '捌': '8', '玖': '9',
            '拾': '10',
            '０': '0', '１': '1', '２': '2', '３': '3', '４': '4', '５': '5', '６': '6', '７': '7', '８': '8', '９': '9',
            '0': '0', '1': '1', '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8', '9': '9'
            }
keyword_dict = {'年': 0, '月': 1, '周': 2, '天': 3, '日': 3}


def current_date():
    return time.strftime('%Y-%m-%d', time.localtime())


def current_time():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())


def convert_compact_timestamp_to_standard(timestamp):
    if len(timestamp) != 14:
        return None
    return timestamp[:4] + '-' + timestamp[4:6] + '-' + timestamp[6:8] + ' ' + timestamp[8:10] + ':' + timestamp[10:12] \
           + ':' + timestamp[12:14]


def convert_standard_timestamp_to_compact(timestamp):
    compact_timestamp = ""
    for ch in timestamp:
        if ch.isdigit():
            compact_timestamp += ch
    return compact_timestamp


def _parse_time_seg_with_dot(time_seg):
    add_dict = {'年余': 93, '月余': 14, '周余': 3}
    unit_dict = {'年': 365, '月': 31, '周': 7, '天': 1, '日': 1}
    days = None
    for keyword, unit in unit_dict.items():
        if time_seg.count(keyword) > 0:
            days = unit
            break
    if not days:
        return None

    num = ""
    for ch in time_seg:
        if ch.isdigit() or ch == '.':
            num += ch
        else:
            break
    if not num:
        return None
    if num.count(".") > 1:
        return None

    days = int(float(num) * days)
    for keyword, add_days in add_dict.items():
        if time_seg.count(keyword) > 0:
            days += add_days
            break

    return [0, 0, 0, days]


def _parse_time_seg_with_hour(time_seg):
    num = ""
    for ch in time_seg:
        if ch.isdigit():
            num += ch
        else:
            break
    if not num:
        return None

    return [0, 0, 0, int(num) // 24]


def _parse_time_seg(time_seg):
    # 年、月、周、天
    result = [0, 0, 0, 0]

    # 上一个解析成功的关键字
    last = None
    # 容忍度
    tolerate = 1
    cur = ""
    for i, ch in enumerate(time_seg):
        if ch == '+' or ch == '-':
            if last is None:
                # +出现在前面
                if i + 1 < len(time_seg) and time_seg[i + 1] in keyword_dict:
                    last = keyword_dict[time_seg[i + 1]]
            if last is not None:
                if ch == '+':
                    # x年+
                    if last == 0:
                        result[1] += 3
                    # x月+
                    if last == 1:
                        result[2] += 2
                    # x周+
                    if last == 2:
                        result[3] += 3
                if ch == '-':
                    # x年-,减1年，加9个月
                    if last == 0 and result[0] > 0:
                        result[0] -= 1
                        result[1] += 9
                    # x月-，减一个月，加两周
                    if last == 1 and result[1] > 0:
                        result[1] -= 1
                        result[2] += 2
                    # x周-，减一周，加三天
                    if last == 2 and result[2] > 0:
                        result[2] -= 1
                        result[3] += 3

        elif ch == '半':
            if last is None:
                # 半字出现在前面
                if i + 1 < len(time_seg) and time_seg[i + 1] in keyword_dict:
                    last = keyword_dict[time_seg[i + 1]]
            if last is not None:
                # 半年
                if last == 0:
                    result[1] += 6
                # 半月
                if last == 1:
                    result[2] += 2
                # 半周
                if last == 2:
                    result[3] += 3
                last += 1
        elif ch == '余':
            # 余字出现在前面
            if i + 1 < len(time_seg) and time_seg[i + 1] in keyword_dict:
                last = keyword_dict[time_seg[i + 1]]
            if last is not None:
                # 年余
                if last == 0:
                    result[1] += 3
                # 月余
                if last == 1:
                    result[2] += 2
                # 周余
                if last == 2:
                    result[3] += 3

        elif ch in num_dict:
            if ch == '十' or ch == '拾':
                if cur != '':
                    if i + 1 < len(time_seg) and time_seg[i + 1] not in num_dict:
                        cur += '0'
                elif i + 1 < len(time_seg):
                    if time_seg[i + 1] in num_dict:
                        cur += '1'
                    else:
                        cur += num_dict[ch]
            else:
                cur += num_dict[ch]
        elif ch in keyword_dict and cur:
            result[keyword_dict[ch]] = int(cur)
            last = keyword_dict[ch]
            cur = ''
            tolerate = 1
        elif ch == '多' or ch == '个':
            continue
        elif tolerate:
            tolerate -= 1
        else:
            break
    return result


def _clean_time_seg(time_seg, current_year):
    if re.match("\d{1,2}月\d{1,2}日", time_seg):
        return None
    if time_seg.find("+") != -1 and time_seg.find("余") != -1:
        time_seg = time_seg.replace("余", "")
    if time_seg.count('同年'):
        time_seg = time_seg.replace('同', str(current_year))
    if time_seg.count('今年'):
        time_seg = time_seg.replace('今', str(current_year))
    if time_seg.count('去年'):
        time_seg = time_seg.replace('去', str(current_year - 1))
    if time_seg.count('前年'):
        time_seg = time_seg.replace('前', str(current_year - 2))
    return time_seg


def _timeseg_rationality_check(time_period_list):
    if time_period_list[0] > 25 or time_period_list[1] > 100 or time_period_list[2] > 100:
        return False
    return True


def _date_substract(start_date, time_period_list):
    start_date -= relativedelta(years=time_period_list[0])
    start_date -= relativedelta(months=time_period_list[1])
    start_date -= relativedelta(weeks=time_period_list[2])
    start_date -= relativedelta(days=time_period_list[3])
    return start_date


def _date_addition(start_date, time_period_list):
    start_date += relativedelta(years=time_period_list[0])
    start_date += relativedelta(months=time_period_list[1])
    start_date += relativedelta(weeks=time_period_list[2])
    start_date += relativedelta(days=time_period_list[3])
    return start_date


def _clean_timestamp(timestamp):
    timestamp = timestamp.strip()
    if timestamp.isdigit() and len(timestamp) == 4:
        return timestamp[:2] + '-' + timestamp[2:]
    if timestamp.isdigit() and len(timestamp) == 8:
        return timestamp[:4] + '-' + timestamp[4:6] + '-' + timestamp[6:]
    if timestamp.count('年初'):
        return timestamp[:4] + "-" + '01'
    if timestamp.count('年中'):
        return timestamp[:4] + "-" + '06'
    if timestamp.count('年底'):
        return timestamp[:4] + "-" + '12'
    if timestamp.count('年尾'):
        return timestamp[:4] + "-" + '12'
    if timestamp.count('年末'):
        return timestamp[:4] + "-" + '12'
    if timestamp.count('年终'):
        return timestamp[:4] + "-" + '12'
    return timestamp.replace("年", "-").replace("月", "-").replace(".", "-").replace("/", "-").replace('日', '').replace(
        ' ', '-').replace('至', '-')


def _year_rationality_check(year):
    return len(year) == 4 and year.isdigit() and 1997 <= int(year) <= 2024


def _month_rationality_check(month):
    return month.isdigit() and 1 <= int(month) <= 12


def _day_rationality_check(day):
    return day.isdigit() and 1 <= int(day) <= 31


def _get_month(ymd_list):
    if len(ymd_list) >= 2:
        month = ymd_list[1]
        if len(ymd_list[1]) == 1:
            month = '0' + month
        return month
    return None


def _get_day(ymd_list):
    if len(ymd_list) >= 3:
        day = ymd_list[2]
        if len(ymd_list[2]) == 1:
            day = '0' + day
        return day
    return None


def parse_time_period(time_seg):
    if time_seg in ['今天', '今日', '当天', '当日', '今晚', '今早']:
        return [0, 0, 0, 0]
    if time_seg in ['昨天', '昨日', '昨晚', '昨早', '近日']:
        return [0, 0, 0, 1]
    if time_seg in ['前天', '前日', '前晚', '前早']:
        return [0, 0, 0, 2]
    elif time_seg.find("时") != -1:
        time_period_list = _parse_time_seg_with_hour(time_seg)
    elif time_seg.find(".") != -1:
        time_period_list = _parse_time_seg_with_dot(time_seg)
    else:
        time_period_list = _parse_time_seg(time_seg)
    return time_period_list


def timeseg_parse(time_seg, timestamp, op=_date_substract):
    """
    时间段解析
    :param time_seg:
    """
    current_year = int(timestamp[:4])
    time_seg = _clean_time_seg(time_seg, current_year)
    if not time_seg:
        return None
    time_period_list = parse_time_period(time_seg)
    if not time_period_list:
        return None

    if _year_rationality_check(str(time_period_list[0])):
        # 该时间段为时间戳
        return timestamp_parse('-'.join([str(t) for t in time_period_list if t]))

    if not _timeseg_rationality_check(time_period_list):
        return None
    start_date = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    start_date = op(start_date, time_period_list)

    return start_date.strftime('%Y-%m-%d')


def get_month(timestamp, year=None):
    ymd_list = get_ymd_list(timestamp, year)
    if ymd_list and len(ymd_list) > 1:
        return ymd_list[1]
    return None


def get_ymd_list(timestamp, year=None):
    if not timestamp:
        return None
    timestamp = _clean_timestamp(timestamp)
    ymd_list = timestamp.split("-")
    if len(ymd_list) == 3 and len(ymd_list[0]) == 2 and len(ymd_list[1]) == 2 and len(ymd_list[2]) == 2:
        ymd_list[0] = '20' + ymd_list[0]
    ymd_list = [item for item in ymd_list if item]
    if not ymd_list:
        return None
    if not _year_rationality_check(ymd_list[0]):
        if year:
            ymd_list = [year] + ymd_list
        else:
            return None
    month = _get_month(ymd_list)
    if month:
        if _month_rationality_check(month):
            ymd_list[1] = month
        else:
            return None
    day = _get_day(ymd_list)
    if day:
        if _day_rationality_check(day):
            ymd_list[2] = day
        else:
            return None
    return ymd_list


def timestamp_parse(timestamp, year=None):
    ymd_list = get_ymd_list(timestamp, year)
    return '-'.join(ymd_list) if ymd_list else None


def diff_between_dates(t1, t2):
    dt1 = datetime.strptime(t1, "%Y-%m-%d %H:%M:%S")
    dt2 = datetime.strptime(t2, "%Y-%m-%d %H:%M:%S")

    delta = relativedelta(dt2, dt1)

    years = delta.years
    months = delta.months
    days = delta.days

    return str(years) + "-" + str(months) + "-" + str(days)


def diff_within_n_months(a, b, n, date_format='%Y%m%d'):
    if a < b:
        date1, date2 = a, b
    else:
        date1, date2 = b, a

    date1 = datetime.strptime(date1, date_format)
    date2 = datetime.strptime(date2, date_format)

    # 计算月份差
    months_diff = (date2.year - date1.year) * 12 + date2.month - date1.month

    # 考虑日期部分的影响
    if months_diff >= n + 1:
        return False

    if months_diff == n:
        return date2.day <= date1.day

    # 判断月份差是否在n个月以内（含n个月）
    return months_diff <= n