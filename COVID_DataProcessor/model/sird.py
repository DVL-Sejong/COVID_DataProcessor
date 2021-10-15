from COVID_DataProcessor.io import load_sird_dict, load_r0_df
from COVID_DataProcessor.io import save_sird_initial_info, load_population, load_regions
from COVID_DataProcessor.util import get_common_dates
from copy import copy

import pandas as pd


def get_initial_dict(country, pre_info):
    sird_dict = load_sird_dict(country, pre_info)
    r0_df = load_r0_df(country)
    pre_dict = get_sird_dict_for_mortality_rate(country, pre_info)
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
        region_df.loc[:, 'mortality_rate'] = pre_dict[region].loc[start_date:end_date, 'deceased'] / region_population
        save_sird_initial_info(pre_info, region_df, country, region)
        initial_dict.update({region: region_df})

    return initial_dict


def get_sird_dict_for_mortality_rate(country, pre_info):
    new_info = copy(pre_info)
    new_info.divide = False

    sird_dict = load_sird_dict(country, new_info)
    return sird_dict


def get_common_dates_between_dict_and_df(data_dict, data_df):
    dict_dates = data_dict[data_dict.keys()[0]].index.tolist()
    df_dates = data_df.columns.to_list()

    common_dates = get_common_dates(dict_dates, df_dates)
    return common_dates
