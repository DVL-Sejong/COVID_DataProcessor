from COVID_DataProcessor.datatype import Country, get_country_name, PreprocessInfo, PreType
from COVID_DataProcessor.io import save_setting, load_raw_data, load_regions, save_test_number, load_links
from COVID_DataProcessor.preprocess.preprocess import preprocess
from COVID_DataProcessor.util import get_period, generate_dataframe
from datetime import datetime, timedelta

import pandas as pd


def get_test_number(country, test_info):
    save_setting(test_info, 'test_info')

    if country == Country.US:
        test_num_df = get_test_number_of_us(country, test_info)
    elif country == Country.ITALY:
        test_num_df = get_test_number_of_italy(country, test_info)
    elif country == Country.INDIA:
        test_num_df = get_test_number_of_india(country, test_info)
    else:
        raise Exception(f'not available country, {country}')

    return test_num_df


def preprocess_test_number(test_num_df, test_info):
    regions = test_num_df.index.tolist()
    preprocessed_df = preprocess(test_num_df.T, None, test_info, regions).T
    preprocessed_df.index.name = 'regions'
    return preprocessed_df


def get_test_number_of_us(country, test_info):
    raw_dict = load_raw_data(country)

    regions = load_regions(country)
    period = get_period(test_info.start, test_info.end, out_date_format='%Y-%m-%d')
    test_num_df = generate_dataframe(regions, period, 'regions')

    for date, raw_df in raw_dict.items():
        if datetime.strptime(date, '%m-%d-%Y') > datetime(2020, 11, 8):
            test_column = 'Total_Test_Results'
        else:
            test_column = 'People_Tested'

        print(f'get test number of us on {date}')
        date_str = datetime.strptime(date, '%m-%d-%Y').strftime('%Y-%m-%d')

        for region in regions:
            region_df = raw_df.loc[raw_df['Province_State'] == region]
            test_num_df.loc[region, date_str] = region_df[test_column].sum()

    test_num_df = preprocess_test_number(test_num_df, test_info)
    save_test_number(country, test_info, test_num_df)
    return test_num_df


def get_test_number_of_italy(country, test_info):
    raw_df = load_raw_data(country)[get_country_name(country)]
    raw_df['data'] = pd.to_datetime(raw_df['data'], format='%Y-%m-%dT%H:%M:%S')

    regions = load_regions(Country.ITALY)
    period_str = get_period(test_info.start, test_info.end, '%Y-%m-%d')
    test_num_df = generate_dataframe(regions, period_str, 'regions')

    period = get_period(test_info.start, test_info.end)
    for i, date in enumerate(period):
        print(date, end=' ')
        date_dt = datetime.combine(date.date(), datetime.min.time())
        mask = (raw_df['data'] >= date_dt) & (raw_df['data'] < date_dt + timedelta(days=1))
        date_df = raw_df.loc[mask]

        for region in regions:
            print(region, end=' ')
            region_df = date_df.loc[date_df['denominazione_regione'] == region]
            test_num_df.loc[region, period_str[i]] = region_df['casi_testati'].sum()
        print()

    test_num_df = preprocess_test_number(test_num_df, test_info)
    save_test_number(country, test_info, test_num_df)
    return test_num_df


def get_test_number_of_india(country, test_info):
    raw_df = load_raw_data(country)[get_country_name(country)]

    regions = load_regions(Country.INDIA)
    period = get_period(test_info.start, test_info.end, out_date_format='%Y-%m-%d')
    test_num_df = generate_dataframe(regions, period, 'regions')

    for i, date in enumerate(period):
        print(date, end=' ')
        date_df = raw_df.loc[raw_df['Date'] == date]

        for region in regions:
            print(region, end=' ')
            region_df = date_df.loc[date_df['State'] == region]
            test_num_df.loc[region:, date] = 0 if region_df.empty else region_df['Tested'].sum()
        print()

    test_num_df = preprocess_test_number(test_num_df, test_info)
    save_test_number(country, test_info, test_num_df)
    return test_num_df


if __name__ == '__main__':
    country = Country.ITALY
    link_df = load_links(country)

    test_info = PreprocessInfo(country=country, start=link_df['start_date'], end=link_df['end_date'],
                               increase=False, daily=True, remove_zero=True,
                               smoothing=True, window=5, divide=False, pre_type=PreType.TEST)

    get_test_number(country, test_info)
