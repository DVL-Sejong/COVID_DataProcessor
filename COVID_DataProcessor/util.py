from datetime import datetime, timedelta


def get_period(start_date, end_date, out_date_format=None):
    if type(start_date) == str:
        start_date = datetime.strptime(start_date, get_date_format(start_date))

    if type(end_date) == str:
        end_date = datetime.strptime(end_date, get_date_format(end_date))

    duration = (end_date - start_date).days + 1
    period = [start_date + timedelta(days=i) for i in range(duration)]

    if out_date_format is None:
        return period
    else:
        return [elem.strftime(out_date_format) for elem in period]


def get_date_format(date: str) -> str:
    formats = ['%Y-%m-%d', '%y%m%d', '%m-%d-%Y', '%m/%d/%y']
    for format in formats:
        if validate(date, format):
            return format

    return ''


def validate(date: str, format: str) -> bool:
    try:
        if date != datetime.strptime(date, format).strftime(format):
            raise ValueError
        return True
    except ValueError:
        return False


def get_common_dates(dates1, dates2):
    start1 = datetime.strptime(dates1[0], '%Y-%m-%d')
    start2 = datetime.strptime(dates2[0], '%Y-%m-%d')
    start_date = start2 if start1 < start2 else start1

    end1 = datetime.strptime(dates1[-1], '%Y-%m-%d')
    end2 = datetime.strptime(dates2[-1], '%Y-%m-%d')
    end_date = end1 if end1 < end2 else end2

    common_dates = get_period(start_date, end_date, out_date_format='%Y-%m-%d')
    return common_dates


if __name__ == '__main__':
    target_date = '1/1/20'
    format =get_date_format(target_date)
    print(format)
