from COVID_DataProcessor.datatype import Country, PreprocessInfo, PreType
from COVID_DataProcessor.io import load_links, load_population, load_preprocessed_data
from COVID_DataProcessor.io import save_preprocessed_dict, save_setting, save_sird_dict
from COVID_DataProcessor.util import get_period, generate_dataframe
from datetime import datetime, timedelta
from copy import copy

import pandas as pd
import numpy as np


def get_sird_dict(country, pre_info):
    sird_info = pre_info.get_sird_info()
    save_setting(sird_info, 'sird_info')

    preprocessed_dict = load_preprocessed_data(country, pre_info)
    sird_dict = convert_columns_to_sird(country, preprocessed_dict, sird_info)
    save_sird_dict(country, sird_info, sird_dict)

    return sird_dict


def preprocess_origin_dict(country, data_dict, pre_info):
    save_setting(pre_info, 'pre_info')
    preprocessed_dict = dict()

    for region, region_df in data_dict.items():
        preprocessed_df = preprocess(region_df, load_population(country, region), pre_info)
        preprocessed_dict.update({region: preprocessed_df})

    save_preprocessed_dict(country, pre_info, preprocessed_dict)
    return preprocessed_dict


def preprocess(parsed_df, population, pre_info, targets=None):
    if pre_info.increase:
        targets = ['confirmed', 'deaths', 'recovered'] if targets is None else targets
        parsed_df = dataset_to_increased(parsed_df, targets=targets)
    if pre_info.daily:
        targets = ['confirmed', 'deaths', 'recovered'] if targets is None else targets
        parsed_df = cumulated_to_daily(parsed_df, targets=targets)
    if pre_info.remove_zero:
        targets = ['recovered'] if targets is None else targets
        parsed_df = remove_zero_period(parsed_df, targets=targets)
    if pre_info.smoothing:
        targets = ['confirmed', 'deaths', 'recovered', 'active'] if targets is None else targets
        parsed_df = apply_moving_average(parsed_df, targets=targets, window=pre_info.window)
    if pre_info.divide:
        parsed_df = divide_by_population(parsed_df, population)

    if pre_info.pre_type == PreType.TEST:
        parsed_df = cut_first_zeros(parsed_df)

    return parsed_df


def convert_columns_to_sird(country, dataset_dict, sird_info):
    new_columns = ['date', 'susceptible', 'infected', 'recovered', 'deceased']
    sird_dict = dict()

    for region, dataset in dataset_dict.items():
        new_df = pd.DataFrame(columns=new_columns)
        dates = dataset.index.to_list()
        infected = dataset['active'].to_numpy()
        recovered = dataset['recovered'].to_numpy()
        deceased = dataset['deaths'].to_numpy()

        if sird_info.divide is False:
            population = load_population(country, region)
            susceptible = np.full(infected.shape, population) - infected - recovered - deceased
        else:
            susceptible = np.ones_like(infected) - infected - recovered - deceased

        new_df['date'] = dates
        new_df['susceptible'] = susceptible
        new_df['infected'] = infected
        new_df['recovered'] = recovered
        new_df['deceased'] = deceased

        new_df = new_df.set_index('date')

        sird_dict.update({region: new_df})

    save_sird_dict(country, sird_info, sird_dict)
    return sird_dict


def dataset_to_increased(target_df, targets):
    preprocessed_df = target_df.copy(deep=True)

    for target in targets:
        target_values = target_df[target].to_list()
        new_values = target_to_increased(target_values)
        preprocessed_df[target] = new_values

    return preprocessed_df


def cumulated_to_daily(target_df, targets):
    preprocessed_df = target_df.copy(deep=True)
    new_index = preprocessed_df.index[1:]

    for target in targets:
        target_values = preprocessed_df[target].to_list()
        daily_values = target_to_daily(target_values)
        preprocessed_df.loc[new_index, target] = daily_values

    return preprocessed_df.loc[new_index, :]


def apply_moving_average(target_df, targets, window):
    preprocessed_df = target_df.copy(deep=True)

    for target in targets:
        target_values = preprocessed_df[target].to_list()
        smoothed = smooth(target_values, window)
        preprocessed_df[target] = smoothed

    return preprocessed_df


def remove_zero_period(target_df, targets):
    preprocessed_df = target_df.copy(deep=True)

    for target in targets:
        target_values = preprocessed_df[target].to_list()
        daily_values = make_zero_and_negative_removed(target_values)
        preprocessed_df.loc[:, target] = daily_values

    return preprocessed_df


def make_zero_and_negative_removed(target_values):
    target_values = copy(target_values)

    for i, value in enumerate(target_values):
        if i == 0: continue
        if target_values[i-1] <= 0 or value > 0: continue

        max_index = get_nonzero_index(target_values, i)
        target_values = interpolate(target_values, i - 1, max_index)

    return target_values


def get_nonzero_index(region_values, broken_index):
    index = broken_index + 1
    while index < len(region_values):
        if region_values[index] > 0:
            return index
        index += 1

    return -1


def divide_by_population(target_df, population):
    preprocessed_df = target_df.copy(deep=True)
    preprocessed_df /= population
    return preprocessed_df


def inverse_divide_by_population(df, population_df):
    new_df = df.copy(deep=True)
    for region, row in new_df.iterrows():
        new_df.loc[region, :] *= population_df.loc[region][0]

    return new_df


def smooth(array, size):
    out = np.convolve(array, np.ones(size, dtype=int), 'valid') / size
    r = np.arange(1, size - 1, 2)
    start = np.cumsum(array[:size - 1][::2]) / r
    stop = (np.cumsum(array[:-size:-1])[::2] / r)[::-1]
    return np.concatenate((start, out, stop))


def target_to_increased(target_values):
    for i in range(1, len(target_values)):
        if target_values[i] - target_values[i - 1] < 0:
            max_index = get_max_index(target_values, i)
            target_values = interpolate(target_values, i - 1, max_index)

    return target_values


def target_to_daily(target_values):
    daily_values = []

    zero_ended = False
    for i in range(len(target_values) - 1):
        if zero_ended is False and target_values[i] != 0:
            zero_ended = True
            daily_values.append(0)
        elif zero_ended is False and target_values[i] == 0:
            daily_values.append(target_values[i])
        else:
            daily_values.append(target_values[i + 1] - target_values[i])

    return daily_values


def get_max_index(region_values, broken_index):
    start_value = region_values[broken_index - 1]

    index = broken_index + 1
    while index < len(region_values):
        if start_value <= region_values[index]:
            return index
        index += 1

    return -1


def interpolate(region_values, start_index, end_index):
    region_values = copy(region_values)

    if end_index == -1:
        tail_len = len(region_values[start_index:])
        tail = [region_values[start_index] for i in range(tail_len)]
        region_values[start_index:] = tail
        return region_values

    step = end_index - start_index
    theta = (region_values[end_index] - region_values[start_index]) / step

    step = 1
    for i in range(start_index + 1, end_index + 1):
        region_values[i] = region_values[start_index] + (theta * step)
        step += 1

    return region_values


def cut_first_zeros(target_df):
    origin_dates = target_df.index.tolist()
    regions = target_df.columns.to_list()

    max_diff = 0
    for region in regions:
        region_values = copy(target_df[region].to_list())
        trim_values = np.trim_zeros(region_values, 'f')
        if len(region_values) - len(trim_values) > max_diff:
            max_diff = len(region_values) - len(trim_values)

    new_first_day = datetime.strptime(origin_dates[0], '%Y-%m-%d') + timedelta(days=max_diff)
    new_period = get_period(new_first_day, origin_dates[-1], '%Y-%m-%d')
    cut_df = generate_dataframe(new_period, regions, 'regions')

    for region in regions:
        cut_df[region] = target_df.loc[new_period, region]

    return cut_df


if __name__ == '__main__':
    country = Country.ITALY
    link_df = load_links(country)

    pre_info = PreprocessInfo(country=country, start=link_df['start_date'], end=link_df['end_date'],
                              increase=True, daily=True, remove_zero=True,
                              smoothing=True, window=5, divide=True, pre_type=PreType.PRE)

    sird_dict = get_sird_dict(country, pre_info)
