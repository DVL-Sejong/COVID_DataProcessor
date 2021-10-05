from COVID_DataProcessor.util import get_date_format
from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum

import hashlib


class Country(Enum):
    CHINA = 0
    INDIA = 1
    ITALY = 2
    US = 3


@dataclass
class PreprocessInfo:
    start: datetime = None
    _start: datetime = field(init=False, repr=False)
    end: datetime = None
    _end: datetime = field(init=False, repr=False)
    increase: bool = None
    _increase: bool = field(default=True)
    daily: bool = None
    _daily: bool = field(default=False)
    smoothing: bool = None
    _smoothing: bool = field(default=False)
    window: int = None
    _window: int = field(default=False)
    divide: bool = None
    _divide: bool = field(default=True)

    def __init__(self, start, end, increase: bool, daily: bool, smoothing: bool, window: int, divide: bool):
        self.start = start
        self.end = end
        self.increase = increase
        self.daily = daily
        self.smoothing = smoothing
        self.window = window
        self.divide = divide

    def __repr__(self):
        representation = f'PreprocessInfo(start: {self._start}, end: {self._end}, '
        representation += f'increase: {self._increase}, daily: {self._daily}, '
        representation += f'smoothing: {self._smoothing}, window: {self._window}, divide: {self._divide})'
        return representation

    @property
    def start(self):
        if hasattr(self, '_start'):
            return self._start
        else:
            return None

    def start_tostring(self, format: str = '%y%m%d'):
        if hasattr(self, '_start'):
            return self._start.strftime(format)
        else:
            return ''

    @start.setter
    def start(self, start):
        if start is None:
            self._start = datetime.now().date()

        if isinstance(start, str):
            format = get_date_format(start)
            self._start = datetime.strptime(start, format).date()
        elif isinstance(start, datetime):
            self._start = start.date()
        elif isinstance(start, date):
            self._start = start

    @property
    def end(self):
        if hasattr(self, '_end'):
            return self._end
        else:
            return None

    def end_tostring(self, format: str = '%y%m%d'):
        if hasattr(self, '_end'):
            return self._end.strftime(format)
        else:
            return ''

    @end.setter
    def end(self, end):
        if end is None:
            self._end = datetime.now().date()

        if isinstance(end, str):
            format = get_date_format(end)
            self._end = datetime.strptime(end, format).date()
        elif isinstance(end, datetime):
            self._end = end.date()
        elif isinstance(end, date):
            self._end = end

    @property
    def increase(self) -> bool:
        return self._increase

    @increase.setter
    def increase(self, increase: bool):
        self._increase = increase

    @property
    def daily(self) -> bool:
        return self._daily

    @daily.setter
    def daily(self, daily: bool):
        self._daily = daily

    @property
    def smoothing(self) -> bool:
        return self._smoothing

    @smoothing.setter
    def smoothing(self, smoothing: bool):
        self._smoothing = smoothing

    @property
    def window(self) -> int:
        return self._window

    @window.setter
    def window(self, window: int):
        self._window = window

    @property
    def divide(self) -> bool:
        return self._divide

    @divide.setter
    def divide(self, divide: bool):
        self._divide = divide

    def get_hash(self):
        hash_key = hashlib.sha1(self.__repr__().encode()).hexdigest()[:6]
        return hash_key


@dataclass
class DatasetInfo:
    x_frames: int = None
    _x_frames: int = field(default=False)
    y_frames: int = None
    _y_frames: int = field(default=False)
    test_start: datetime = None
    _test_start: datetime = field(init=False, repr=False)
    test_end: datetime = None
    _test_end: datetime = field(init=False, repr=False)

    def __init__(self, x_frames: int, y_frames: int, test_start=None, test_end=None):
        self.x_frames = x_frames
        self.y_frames = y_frames
        self.test_start = test_start
        self.test_end = test_end

    def __repr__(self):
        representation = f'DatasetInfo(x_frames: {self._x_frames}, y_frames: {self._y_frames}, '
        representation += f'test_start: {self._test_start}, test_end: {self._test_end})'
        return representation

    @property
    def x_frames(self) -> int:
        return self._x_frames

    @x_frames.setter
    def x_frames(self, x_frames: int):
        self._x_frames = x_frames

    @property
    def y_frames(self) -> int:
        return self._y_frames

    @y_frames.setter
    def y_frames(self, y_frames: int):
        self._y_frames = y_frames

    @property
    def test_start(self):
        if hasattr(self, '_test_start'):
            return self._test_start
        else:
            return None

    def start_tostring(self, format: str = '%y%m%d'):
        if hasattr(self, '_test_start'):
            return self._test_start.strftime(format)
        else:
            return ''

    @test_start.setter
    def test_start(self, test_start):
        if test_start is None:
            self._test_start = datetime.now().date()

        if isinstance(test_start, str):
            format = get_date_format(test_start)
            self._test_start = datetime.strptime(test_start, format).date()
        elif isinstance(test_start, datetime):
            self._test_start = test_start.date()
        elif isinstance(test_start, date):
            self._test_start = test_start

    @property
    def test_end(self):
        if hasattr(self, '_test_end'):
            return self._test_end
        else:
            return None

    def end_tostring(self, format: str = '%y%m%d'):
        if hasattr(self, '_test_end'):
            return self._test_end.strftime(format)
        else:
            return ''

    @test_end.setter
    def test_end(self, test_end):
        if test_end is None:
            self._test_end = datetime.now().date()

        if isinstance(test_end, str):
            format = get_date_format(test_end)
            self._test_end = datetime.strptime(test_end, format).date()
        elif isinstance(test_end, datetime):
            self._test_end = test_end.date()
        elif isinstance(test_end, date):
            self._test_end = test_end

    def get_hash(self):
        hash_key = hashlib.sha1(self.__repr__().encode()).hexdigest()[:6]
        return hash_key


def get_country_name(country):
    if country == Country.US:
        return country.name
    else:
        return country.name.capitalize()
