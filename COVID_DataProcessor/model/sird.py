from COVID_DataProcessor.datatype import Country, PreprocessInfo, PreType
from COVID_DataProcessor.io import load_sird_dict, load_r0_df, load_links, load_preprocessed_data
from COVID_DataProcessor.io import save_infectious_period, save_dataset_for_sird_model
from COVID_DataProcessor.io import save_sird_initial_info, load_population, load_regions
from COVID_DataProcessor.preprocess.preprocess import get_sird_dict
from COVID_DataProcessor.util import get_common_dates, generate_dataframe
from copy import copy

import pandas as pd


def get_dataset_for_sird_model(country, pre_info, test_info):
    period_df = get_infectious_period(country)
    population_df = load_population(country)
    initial_dict = get_initial_dict(country, pre_info, test_info)
    sird_dict = get_sird_dict(country, pre_info)

    dataset_dict = {'infectious_period': period_df,
                    'population': population_df,
                    'pre_info': pre_info,
                    'test_info': test_info,
                    'initial_dict': initial_dict,
                    'sird_info': pre_info.get_sird_info(),
                    'sird_dict': sird_dict}
    save_dataset_for_sird_model(country, dataset_dict)
    return dataset_dict


def get_initial_dict(country, pre_info, test_info):
    r0_df = load_r0_df(country, pre_info.get_hash(), test_info.get_hash())
    pre_dict = load_preprocessed_data(country, pre_info)
    population_df = load_population(country)

    common_dates = get_common_dates_between_dict_and_df(pre_dict, r0_df)
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
        save_sird_initial_info(f'{pre_info.get_hash()}_{test_info.get_hash()}', region_df, country, region)
        initial_dict.update({region: region_df})

    return initial_dict


def get_infectious_period(country):
    period_df = generate_dataframe(load_regions(country), ['infectious_period'], 'regions')
    period_df.loc[:, 'infectious_period'] = 5
    save_infectious_period(country, period_df)
    return period_df


def get_common_dates_between_dict_and_df(data_dict, data_df):
    dict_dates = data_dict[next(iter(data_dict))].index.tolist()
    df_dates = data_df.columns.to_list()

    common_dates = get_common_dates(dict_dates, df_dates)
    return common_dates


if __name__ == '__main__':
    country = Country.ITALY
    link_df = load_links(country)

    pre_info = PreprocessInfo(country=country, start=link_df['start_date'], end=link_df['end_date'],
                               increase=True, daily=True, remove_zero=True,
                               smoothing=True, window=5, divide=False, pre_type=PreType.PRE)
    test_info = PreprocessInfo(country=country, start=link_df['start_date'], end=link_df['end_date'],
                              increase=True, daily=True, remove_zero=True,
                              smoothing=True, window=5, divide=False, pre_type=PreType.TEST)

    dataset_dict = get_dataset_for_sird_model(country, pre_info, test_info)
