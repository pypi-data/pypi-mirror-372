import time
import threading
class Time:
    def __init__(self, year=None, month=None, day=None, hour=0, minute=0, second=0):
        if year is None or month is None or day is None:
            t = time.localtime()
            self.year = t.tm_year
            self.month = t.tm_mon
            self.day = t.tm_mday
            self.hour = t.tm_hour
            self.minute = t.tm_min
            self.second = t.tm_sec
        else:
            self.year = year
            self.month = month
            self.day = day
            self.hour = hour
            self.minute = minute
            self.second = second

    def __str__(self):
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d} {self.hour:02d}:{self.minute:02d}:{self.second:02d}"

    def __eq__(self, other):
        return (self.year, self.month, self.day, self.hour, self.minute, self.second) == \
               (other.year, other.month, other.day, other.hour, other.minute, other.second)

    def __lt__(self, other):
        return (self.year, self.month, self.day, self.hour, self.minute, self.second) < \
               (other.year, other.month, other.day, other.hour, other.minute, other.second)

    def __gt__(self, other):
        return (self.year, self.month, self.day, self.hour, self.minute, self.second) > \
               (other.year, other.month, other.day, other.hour, other.minute, other.second)

    @staticmethod
    def is_leap_year(year):
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    @staticmethod
    def days_in_month(year, month):
        if month in [1,3,5,7,8,10,12]:
            return 31
        elif month in [4,6,9,11]:
            return 30
        elif month == 2:
            return 29 if Time.is_leap_year(year) else 28
        return 0

    def add_days(self, days):
        self.day += days
        while self.day > self.days_in_month(self.year, self.month):
            self.day -= self.days_in_month(self.year, self.month)
            self.month += 1
            if self.month > 12:
                self.month = 1
                self.year += 1

    def add_seconds(self, seconds):
        self.second += seconds
        while self.second >= 60:
            self.second -= 60
            self.minute += 1
        while self.minute >= 60:
            self.minute -= 60
            self.hour += 1
        while self.hour >= 24:
            self.hour -= 24
            self.add_days(1)

    def is_expired(self):
        t = time.localtime()
        now = Time(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
        return now > self

    def sleep_until_expired(self, check_interval=1):
        while True:
            if self.is_expired():
                print("انتهى الوقت!")
                break
            time.sleep(check_interval)
        thread = threading.Thread(target=monitor)
        thread.daemon = True
        thread.start()
        return thread

    def format(self, fmt="%Y-%m-%d %H:%M:%S"):
        result = fmt
        result = result.replace("%Y", f"{self.year:04d}")
        result = result.replace("%m", f"{self.month:02d}")
        result = result.replace("%d", f"{self.day:02d}")
        result = result.replace("%H", f"{self.hour:02d}")
        result = result.replace("%M", f"{self.minute:02d}")
        result = result.replace("%S", f"{self.second:02d}")
        return result