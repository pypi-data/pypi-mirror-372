from dataclasses import dataclass

from common.util.date_util import timeseg_parse, timestamp_parse, get_month, _year_rationality_check

TIME_TYPE_DICT = {
    "时间段": 1,
    "时间戳": 2,
    "时间范围": 3,
    "入院时间": 4,
    "模糊时间": 5,
    "异常时间": 9
}

@dataclass
class Timeline:
    base_time: str
    base_time_type: str
    admission_time: str
    base_year: str = None
    base_time_convert: str = None
    start_index: int = None
    end_index: int = None
    content: str = None

    def __init__(self, base_time, base_time_type, admission_time, last_timeline):
        self.base_time = base_time
        self.base_time_type = base_time_type
        self.admission_time = admission_time
        if self.admission_time:
            self.set_base_year(last_timeline)
            self.set_base_time_convert()
            self.base_time_type = TIME_TYPE_DICT.get(self.base_time_type, 9)

    def set_base_time_convert(self):
        def _parse_time_arr(arr):
            first_time = timestamp_parse(arr[0], self.base_year)
            second_time = timestamp_parse(arr[1], self.base_year)
            if not first_time or not second_time or len(first_time) < 7 or len(second_time) < 7:
                return None
            if first_time[:7] != second_time[:7] and second_time < first_time:
                second_time = str(int(second_time[:4]) + 1) + second_time[4:]
            return first_time + '至' + second_time

        if self.base_time_type == '时间段':
            self.base_time_convert = timeseg_parse(self.base_time.replace("入院前", ""), self.admission_time)
        elif self.base_time_type == '时间范围':
            time_arr = self.base_time.split("-")
            if len(time_arr) == 2:
                self.base_time_convert = _parse_time_arr(time_arr)
            time_arr = self.base_time.split("~")
            if len(time_arr) == 2:
                self.base_time_convert = _parse_time_arr(time_arr)
            time_arr = self.base_time.split("～")
            if len(time_arr) == 2:
                self.base_time_convert = _parse_time_arr(time_arr)
            time_arr = self.base_time.split("至")
            if len(time_arr) == 2:
                self.base_time_convert = _parse_time_arr(time_arr)
        elif self.base_time_type == '入院时间':
            self.base_time_convert = self.admission_time
        elif self.base_time_type == '模糊时间':
            self.base_time_convert = self.base_time
        else:
            self.base_time_convert = timestamp_parse(self.base_time, self.base_year)

    def set_base_year(self, last_timeline):
        if not self.base_time:
            return
        if self.base_time.count('同年') and last_timeline:
            self.base_year = last_timeline.base_year
        elif self.base_time_type == '时间段':
            self.base_year = self.admission_time[:4]
        else:
            year = self.base_time[:4]
            if _year_rationality_check(year):
                self.base_year = year
            elif last_timeline:
                add_year = 0
                first_month = get_month(last_timeline.base_time, last_timeline.base_year)
                second_month = get_month(self.base_time, last_timeline.base_year)
                if first_month and second_month and second_month < first_month:
                    add_year = 1
                self.base_year = str(int(last_timeline.base_year) + add_year)
            else:
                self.base_year = self.admission_time[:4]