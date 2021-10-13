from COVID_DataProcessor.datatype import Country, PreprocessInfo, get_country_name
from COVID_DataProcessor.io import load_sird_dict, load_r0_df, load_us_confirmed_data, load_preprocessed_data, \
    save_setting
from COVID_DataProcessor.io import load_links, load_raw_data, save_test_number
from COVID_DataProcessor.io import save_sird_initial_info, save_first_confirmed_date
from COVID_DataProcessor.io import load_population, load_regions, load_origin_data
from COVID_DataProcessor.preprocessing import preprocess_test_number
from COVID_DataProcessor.util import get_common_dates, get_period
from datetime import datetime, timedelta
from copy import copy

import pandas as pd


def get_pre_dict_for_mortality_rate(country, pre_info):
    new_info = copy(pre_info)
    new_info.divide = False

    pre_dict = load_preprocessed_data(country, new_info)
    return pre_dict


def get_common_dates_between_dict_and_df(data_dict, data_df):
    dict_dates = data_dict[data_dict.keys()[0]].index.tolist()
    df_dates = data_df.columns.to_list()

    common_dates = get_common_dates(dict_dates, df_dates)
    return common_dates


def get_initial_dict(country, pre_info):
    sird_dict = load_sird_dict(country, pre_info)
    r0_df = load_r0_df(country)
    pre_dict = get_pre_dict_for_mortality_rate(country, pre_info)
    population_df = load_population(country)

    common_dates = get_common_dates_between_dict_and_df(sird_dict, r0_df)
    start_date = common_dates[0]
    end_date = common_dates[-1]

    regions = load_regions(country)
    initial_dict = dict()

    for region in regions:
        if region not in r0_df.index.tolist():
            continue

        region_df = pd.DataFrame(index=common_dates, columns=['r0', 'mortality_rate'])
        region_df.index.name = 'date'

        region_population = population_df.loc[region, 'population']
        region_df.loc[:, 'r0'] = r0_df.loc[region, start_date:end_date]
        region_df.loc[:, 'mortality_rate'] = pre_dict[region].loc[start_date:end_date, 'deaths'] / region_population
        save_sird_initial_info(pre_info, region_df, country, region)
        initial_dict.update({region: region_df})

    return initial_dict


def get_first_confirmed_date(country):
    regions = load_regions(country)
    first_confirmed_date_df = pd.DataFrame(index=regions, columns=['first_date'])
    first_confirmed_date_df.index.name = 'regions'

    if country == Country.US:
        us_confirmed_df = load_us_confirmed_data()
        for region in regions:
            region_values = us_confirmed_df.loc[region, :].to_list()
            index = next(index for index, value in enumerate(region_values) if value > 0)
            first_confirmed_date_df.loc[region, 'first_date'] = us_confirmed_df.columns[index]
    else:
        origin_dict = load_origin_data(country)
        for region in regions:
            region_df = origin_dict[region]
            for index, row in region_df.iterrows():
                if row['confirmed'] > 0:
                    first_confirmed_date_df.loc[region, 'first_date'] = index
                    break

    save_first_confirmed_date(country, first_confirmed_date_df)
    return first_confirmed_date_df


def get_test_number(country, pre_info):
    if pre_info.increase:
        pre_info.increase = False
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


def get_test_number_of_us(country, pre_info):
    raw_dict = load_raw_data(country)

    regions = load_regions(country)
    period = get_period(pre_info.start, pre_info.end, out_date_format='%Y-%m-%d')

    test_num_df = pd.DataFrame(index=regions, columns=period)
    test_num_df.index.name = 'regions'

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
    period = get_period(pre_info.start, pre_info.end)
    period_str = [elem.strftime('%Y-%m-%d') for elem in period]

    test_num_df = pd.DataFrame(index=regions, columns=period_str)
    test_num_df.index.name = 'regions'

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

    test_num_df = pd.DataFrame(index=regions, columns=period)
    test_num_df.index.name = 'regions'

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


if __name__ == '__main__':
    country = Country.US
    link_df = load_links(country)

    pre_info = PreprocessInfo(country=country, start=link_df['start_date'], end=link_df['end_date'],
                              increase=False, daily=True, remove_zero=True,
                              smoothing=True, window=9, divide=False)

    test_num_df = get_test_number(country, pre_info)
