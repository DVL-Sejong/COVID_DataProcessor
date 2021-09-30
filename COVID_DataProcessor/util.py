from datetime import datetime, timedelta


def get_period(start_date, end_date, in_date_format=None, out_date_format=None):
    if type(start_date) == str:
        start_date = datetime.strptime(start_date, in_date_format)

    if type(end_date) == str:
        end_date = datetime.strptime(end_date, in_date_format)

    duration = (end_date - start_date).days + 1
    period = [start_date + timedelta(days=i) for i in range(duration)]

    if out_date_format is None:
        return period
    else:
        return [elem.strftime(out_date_format) for elem in period]


if __name__ == '__main__':
    start_date = '2020-01-01'
    end_date = '2020-01-05'
    period = get_period(start_date, end_date, in_date_format='%Y-%m-%d', out_date_format='%m-%d-%Y')
    print(period)
