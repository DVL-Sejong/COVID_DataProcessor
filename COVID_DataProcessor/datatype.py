from COVID_DataProcessor.util import get_date_format
from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from copy import copy

import hashlib


class Country(Enum):
    CHINA = 0
    INDIA = 1
    ITALY = 2
    US = 3
    US_CONFIRMED = 4


class PreType(Enum):
    PRE = 0
    SIRD = 1
    TEST = 2


@dataclass
class PreprocessInfo:
    country: Country = None
    _country: Country = field(init=False, repr=False)
    start: datetime = None
    _start: datetime = field(init=False, repr=False)
    end: datetime = None
    _end: datetime = field(init=False, repr=False)
    increase: bool = None
    _increase: bool = field(default=True)
    daily: bool = None
    _daily: bool = field(default=False)
    remove_zero: bool = None
    _remove_zero: bool = field(default=False)
    smoothing: bool = None
    _smoothing: bool = field(default=False)
    window: int = None
    _window: int = field(default=False)
    divide: bool = None
    _divide: bool = field(default=True)
    pre_type: PreType = None
    _pre_type: PreType = field(default=True)

    def __init__(self, country, start, end,
                 increase: bool, daily: bool, remove_zero: bool,
                 smoothing: bool, window: int, divide: bool, pre_type: PreType):
        self.country = country
        self.start = start
        self.end = end
        self.increase = increase
        self.daily = daily
        self.remove_zero = remove_zero
        self.smoothing = smoothing
        self.window = window
        self.divide = divide
        self.pre_type = pre_type

        self.check_valid()

    def __repr__(self):
        representation = f'PreprocessInfo(country: {self._country.name}, start: {self._start}, end: {self._end}, '
        representation += f'increase: {self._increase}, daily: {self._daily}, remove_zero: {self._remove_zero}, '
        representation += f'smoothing: {self._smoothing}, window: {self._window}, divide: {self._divide})'
        return representation

    @property
    def country(self) -> Country:
        return self._country

    @country.setter
    def country(self, country: Country):
        self._country = country

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
    def remove_zero(self) -> bool:
        return self._remove_zero

    @remove_zero.setter
    def remove_zero(self, remove_zero: bool):
        self._remove_zero = remove_zero

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

    @property
    def pre_type(self) -> PreType:
        return self._pre_type

    @pre_type.setter
    def pre_type(self, pre_type: PreType):
        self._pre_type = pre_type

    def get_hash(self):
        hash_key = hashlib.sha1(self.__repr__().encode()).hexdigest()[:6]
        return hash_key

    def check_valid(self):
        if self.pre_type is PreType.TEST and self.increase is True:
            raise ValueError(f'increase cannot be True for test number dataset!')

        if self.daily is False and self.remove_zero is True:
            self.remove_zero = False
            print(f'remove_zero cannot be implemented when daily is set to False.', end=' ')
            print(f'remove_zero value is changed to False')

        if self.smoothing is False and self.window != 0:
            self.window = 0
            print(f'window cannot bigger than 0 if smoothing is set to False.', end=' ')
            print(f'window value is changed to 0')

        if self.smoothing is True:
            if self.window <= 0:
                raise ValueError(f'window has to bigger than 0, {self.window}')
            elif self.window % 2 == 0:
                raise ValueError(f'window value has to be odd, {self.window}')

        if self.pre_type is PreType.TEST and self.divide is True:
            raise ValueError(f'divide cannot be True for test number dataset!')

        if self.pre_type is PreType.SIRD and self.divide is False:
            raise ValueError(f'divide CANNOT be False for SIRD dataset!')

    def get_sird_info(self):
        sird_info = copy(self)
        sird_info.pre_type = PreType.SIRD
        sird_info.divide = True
        return sird_info


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
    if country == Country.US or country == Country.US_CONFIRMED:
        return country.name
    else:
        return country.name.capitalize()
