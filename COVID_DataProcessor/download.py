from COVID_DataProcessor.util import *
from COVID_DataProcessor.io import *
from datetime import datetime, timedelta

import pandas as pd
import requests
import io
import re


def download_raw_file(link):
    raw_file = requests.get(link)
    raw_text = io.StringIO(raw_file.text)
    record_df = pd.read_csv(raw_text, sep=',')
    return record_df


def download_origin_data(country):
    link_df = load_links(country)

    if country == Country.US:
        download_us_origin_data(link_df)
    elif country == Country.CHINA:
        download_china_origin_data(link_df)
    elif country == Country.ITALY:
        download_italy_origin_data(link_df)
    elif country == Country.INDIA:
        download_india_origin_data(link_df)
    elif country == Country.US_CONFIRMED:
        download_us_confirmed_origin_data(link_df)
    else:
        raise Exception(f'not registered country, {country}')


def get_empty_df_dict(data_info):
    country = Country[data_info.name.upper()]
    regions = load_regions(country)
    index_period = get_period(data_info['start_date'], data_info['end_date'], out_date_format='%Y-%m-%d')

    df_dict = dict()
    for region in regions:
        data_df = pd.DataFrame(index=index_period, columns=['confirmed', 'deaths', 'recovered', 'active'])
        data_df.index.name = 'date'
        df_dict.update({region: data_df})

    return df_dict


def download_us_origin_data(data_info):
    country = Country[data_info.name.upper()]
    regions = load_regions(country)
    df_dict = get_empty_df_dict(data_info)

    query_period = get_period(data_info['start_date'], data_info['end_date'],  out_date_format='%m-%d-%Y')
    index_period = get_period(data_info['start_date'], data_info['end_date'], out_date_format='%Y-%m-%d')

    for i, date in enumerate(query_period):
        print(f'download US raw data on {index_period[i]}')

        link = data_info['link']
        raw_df = download_raw_file(f'{link}{date}.csv')
        save_raw_file(country, raw_df, date)

        for region in regions:
            region_df = raw_df.loc[raw_df['Province_State'] == region]
            df_dict[region].loc[index_period[i], 'confirmed'] = region_df['Confirmed'].sum()
            df_dict[region].loc[index_period[i], 'deaths'] = region_df['Deaths'].sum()
            df_dict[region].loc[index_period[i], 'recovered'] = region_df['Recovered'].sum(skipna=True)
            df_dict[region].loc[index_period[i], 'active'] = region_df['Active'].sum(skipna=True)

    save_origin_data(country, df_dict)


def download_us_confirmed_origin_data(data_info):
    country = Country.US_CONFIRMED
    raw_df = download_raw_file(data_info['link'])
    # save_raw_file(country, raw_df, country.name)

    regions = load_regions(country)
    tmp_region_df = raw_df.loc[raw_df['Province_State'] == regions[0]]
    date_columns = [col for col in tmp_region_df.columns.to_list() if re.search(r'\d+\/\d+\/\d+', col)]
    new_columns = get_period(datetime.strptime(date_columns[0], '%m/%d/%y'),
                             datetime.strptime(date_columns[-1], '%m/%d/%y'),
                             out_date_format='%Y-%m-%d')

    origin_df = pd.DataFrame(index=regions, columns=new_columns)
    origin_df.index.name = 'regions'

    for region in regions:
        print(region)
        region_df = raw_df.loc[raw_df['Province_State'] == region]

        for date_column in date_columns:
            date_datetime = datetime.strptime(date_column, '%m/%d/%y')
            date_str = date_datetime.strftime('%Y-%m-%d')
            origin_df.loc[region, date_str] = region_df[date_column].sum()

    origin_dict = {country.name: origin_df}
    save_origin_data(country, origin_dict)


def download_csse_raw_data(df_dict, country_name, regions, link, start_date, end_date, country_column, state_column):
    query_period = get_period(start_date, end_date, out_date_format='%m-%d-%Y')
    index_period = get_period(start_date, end_date, out_date_format='%Y-%m-%d')

    for i, date in enumerate(query_period):
        print(f'download {country_name} raw data on {index_period[i]}')
        raw_df = download_raw_file(f'{link}{date}.csv')
        save_raw_file(Country.CHINA, raw_df, date)

        country_df = raw_df.loc[raw_df[country_column] == country_name]

        for region in regions:
            region_df = country_df.loc[country_df[state_column] == region]
            df_dict[region].loc[index_period[i], 'confirmed'] = region_df['Confirmed'].sum()
            df_dict[region].loc[index_period[i], 'deaths'] = region_df['Deaths'].sum()
            df_dict[region].loc[index_period[i], 'recovered'] = region_df['Recovered'].sum(skipna=True)
            if 'Active' not in raw_df.columns.to_list():
                df_dict[region].loc[index_period[i], 'active'] = region_df['Confirmed'].sum() \
                                                                 - region_df['Deaths'].sum() \
                                                                 - region_df['Recovered'].sum(skipna=True)
            else:
                df_dict[region].loc[index_period[i], 'active'] = region_df['Active'].sum(skipna=True)

    return df_dict


def download_china_origin_data(data_info):
    country = Country[data_info.name.upper()]
    regions = load_regions(country)

    df_dict = get_empty_df_dict(data_info)
    df_dict = download_csse_raw_data(df_dict, 'Mainland China', regions, data_info['link'],
                                     data_info['start_date'], '2020-03-21', 'Country/Region', 'Province/State')
    df_dict = download_csse_raw_data(df_dict, 'China', regions, data_info['link'],
                                     '2020-03-22', data_info['end_date'], 'Country_Region', 'Province_State')

    save_origin_data(country, df_dict)


def download_italy_origin_data(data_info):
    country = Country[data_info.name.upper()]
    regions = load_regions(country)
    df_dict = get_empty_df_dict(data_info)
    period = get_period(data_info['start_date'], data_info['end_date'])

    raw_df = download_raw_file(data_info['link'])
    save_raw_file(country, raw_df, 'Italy')
    raw_df['data'] = pd.to_datetime(raw_df['data'], format='%Y-%m-%dT%H:%M:%S')

    for i, date in enumerate(period):
        date_dt = datetime.combine(date.date(), datetime.min.time())
        mask = (raw_df['data'] >= date_dt) & (raw_df['data'] < date_dt + timedelta(days=1))
        date_df = raw_df.loc[mask]
        date_str = date.strftime('%Y-%m-%d')

        for region in regions:
            region_df = date_df.loc[date_df['denominazione_regione'] == region]
            df_dict[region].loc[date_str, 'confirmed'] = region_df['totale_casi'].values[0]
            df_dict[region].loc[date_str, 'deaths'] = region_df['deceduti'].values[0]
            df_dict[region].loc[date_str, 'recovered'] = region_df['dimessi_guariti'].values[0]
            df_dict[region].loc[date_str, 'active'] = region_df['totale_casi'].values[0] \
                                                      - region_df['deceduti'].values[0] \
                                                      - region_df['dimessi_guariti'].values[0]

    save_origin_data(country, df_dict)


def download_india_origin_data(data_info):
    country = Country[data_info.name.upper()]
    regions = load_regions(country)
    df_dict = get_empty_df_dict(data_info)
    period = get_period(data_info['start_date'], data_info['end_date'], out_date_format='%Y-%m-%d')

    raw_df = download_raw_file(data_info['link'])
    save_raw_file(country, raw_df, 'India')

    for date in period:
        date_df = raw_df.loc[raw_df['Date'] == date]

        for region in regions:
            region_df = date_df.loc[date_df['State'] == region]
            if region_df.empty:
                df_dict[region].loc[date, :] = 0
                continue

            df_dict[region].loc[date, 'confirmed'] = region_df['Confirmed'].values[0]
            df_dict[region].loc[date, 'deaths'] = region_df['Deceased'].values[0]
            df_dict[region].loc[date, 'recovered'] = region_df['Recovered'].values[0]
            df_dict[region].loc[date, 'active'] = region_df['Confirmed'].values[0] \
                                                  - region_df['Deceased'].values[0] \
                                                  - region_df['Recovered'].values[0]

    save_origin_data(country, df_dict)


if __name__ == '__main__':
    country = Country.US_CONFIRMED
    download_origin_data(country)
