from COVID_DataProcessor.datatype import Country, get_country_name
from COVID_DataProcessor.io import save_setting, load_raw_data, load_regions, save_test_number
from COVID_DataProcessor.preprocess.preprocess import target_to_daily, make_zero_and_negative_removed
from COVID_DataProcessor.preprocess.preprocess import remove_target_zeros, smooth
from COVID_DataProcessor.util import get_period, generate_dataframe
from datetime import datetime, timedelta

import pandas as pd


def get_test_number(country, pre_info):
    save_setting(pre_info, 'pre_info')

    if country == Country.US:
        test_num_df = get_test_number_of_us(country, pre_info)
    elif country == Country.ITALY:
        test_num_df = get_test_number_of_italy(country, pre_info)
    elif country == Country.INDIA:
        test_num_df = get_test_number_of_india(country, pre_info)
    else:
        raise Exception(f'not available country, {country}')

    return test_num_df


def preprocess_test_number(test_num_df, pre_info):
    regions = test_num_df.index.tolist()

    for region in regions:
        target_value = test_num_df.loc[region, :].to_list()
        if pre_info.daily:
            target_value = target_to_daily(target_value)
        if pre_info.remove_zero:
            target_value = make_zero_and_negative_removed(target_value)
            target_value = remove_target_zeros(target_value)
        if pre_info.smoothing:
            target_value = smooth(target_value, pre_info.window)

        test_num_df.loc[region, :] = target_value

    if pre_info.smoothing:
        test_num_df = test_num_df.iloc[:, pre_info.window:]

    return test_num_df


def get_test_number_of_us(country, pre_info):
    raw_dict = load_raw_data(country)

    regions = load_regions(country)
    period = get_period(pre_info.start, pre_info.end, out_date_format='%Y-%m-%d')
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

    test_num_df = preprocess_test_number(test_num_df, pre_info)
    save_test_number(country, pre_info, test_num_df)
    return test_num_df


def get_test_number_of_italy(country, pre_info):
    raw_df = load_raw_data(country)[get_country_name(country)]
    raw_df['data'] = pd.to_datetime(raw_df['data'], format='%Y-%m-%dT%H:%M:%S')

    regions = load_regions(Country.ITALY)
    period_str = get_period(pre_info.start, pre_info.end, '%Y-%m-%d')
    test_num_df = generate_dataframe(regions, period_str, 'regions')

    period = get_period(pre_info.start, pre_info.end)
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

    test_num_df = preprocess_test_number(test_num_df, pre_info)
    save_test_number(country, pre_info, test_num_df)
    return test_num_df


def get_test_number_of_india(country, pre_info):
    raw_df = load_raw_data(country)[get_country_name(country)]

    regions = load_regions(Country.INDIA)
    period = get_period(pre_info.start, pre_info.end, out_date_format='%Y-%m-%d')
    test_num_df = generate_dataframe(regions, period, 'regions')

    for i, date in enumerate(period):
        print(date, end=' ')
        date_df = raw_df.loc[raw_df['Date'] == date]

        for region in regions:
            print(region, end=' ')
            region_df = date_df.loc[date_df['State'] == region]
            test_num_df.loc[region:, date] = 0 if region_df.empty else region_df['Tested'].sum()
        print()

    test_num_df = preprocess_test_number(test_num_df, pre_info)
    save_test_number(country, pre_info, test_num_df)
    return test_num_df
