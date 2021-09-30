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
    formats = ['%Y-%m-%d', '%y%m%d', '%m-%d-%Y']
    for format in formats:
        if validate(date, format):
            return format

    raise Exception(f'date {date} is not datetime type')


def validate(date: str, format: str) -> bool:
    try:
        if date != datetime.strptime(date, format).strftime(format):
            raise ValueError
        return True
    except ValueError:
        return False


if __name__ == '__main__':
    start_date = '2020-01-01'
    end_date = '2020-01-05'
    period = get_period(start_date, end_date, out_date_format='%m-%d-%Y')
    print(period)
