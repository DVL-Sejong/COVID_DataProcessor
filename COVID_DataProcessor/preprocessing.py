from COVID_DataProcessor.datatype import Country, PreprocessInfo
from COVID_DataProcessor.io import load_links, load_origin_data, load_population
from COVID_DataProcessor.io import save_setting, save_preprocessed_dict, save_sird_dict

import pandas as pd
import numpy as np


def preprocess(parsed_df, population, pre_info):
    if pre_info.increase:
        parsed_df = dataset_to_increased(parsed_df, targets=['confirmed', 'deaths', 'recovered'])
    if pre_info.daily:
        parsed_df = cumulated_to_daily(parsed_df, targets=['confirmed', 'deaths', 'recovered'])
    if pre_info.smoothing:
        parsed_df = apply_moving_average(parsed_df, targets=['confirmed', 'deaths', 'recovered', 'active'], window=pre_info.window)
    if pre_info.divide:
        parsed_df = divide_by_population(parsed_df, population)

    return parsed_df


def preprocess_data_dict(data_dict, pre_info, population_df):
    preprocessed_dict = dict()
    for region, region_df in data_dict.items():
        preprocessed_df = preprocess(region_df, population_df.loc[region, 'population'], pre_info)
        preprocessed_dict.update({region: preprocessed_df})

    return preprocessed_dict


def convert_columns_to_sird(dataset_dict, pre_info, population_df):
    new_columns = ['date', 'susceptible', 'infected', 'recovered', 'deceased']
    new_dataset_dict = dict()

    for region, dataset in dataset_dict.items():
        new_df = pd.DataFrame(columns=new_columns)
        dates = dataset.index.to_list()
        infected = dataset['active'].to_numpy()
        recovered = dataset['recovered'].to_numpy()
        deceased = dataset['deaths'].to_numpy()

        if pre_info.divide is False:
            population = population_df.loc[region][0]
            susceptible = np.full(infected.shape, population) - infected - recovered - deceased
        else:
            susceptible = np.ones_like(infected) - infected - recovered - deceased

        new_df['date'] = dates
        new_df['susceptible'] = susceptible
        new_df['infected'] = infected
        new_df['recovered'] = recovered
        new_df['deceased'] = deceased

        new_df = new_df.set_index('date')

        new_dataset_dict.update({region: new_df})

    return new_dataset_dict


def dataset_to_increased(target_df, targets):
    preprocessed_df = target_df.copy(deep=True)

    for target in targets:
        target_values = target_df[target].to_list()
        new_values = target_to_increased(target_values)
        preprocessed_df[target] = new_values

    return preprocessed_df


def cumulated_to_daily(target_df, targets):
    dates = target_df.index.to_list()

    preprocessed_df = target_df.copy(deep=True)
    for target in targets:
        target_values = preprocessed_df[target].to_list()

        daily_values = []
        daily_values.append(target_values[0])

        for i in range(len(dates) - 1):
            daily_values.append(target_values[i + 1] - target_values[i])

        preprocessed_df[target] = daily_values

    return preprocessed_df


def apply_moving_average(target_df, targets, window):
    preprocessed_df = target_df.copy(deep=True)

    for target in targets:
        target_values = preprocessed_df[target].to_list()
        smoothed = smooth(target_values, window)
        preprocessed_df[target] = smoothed

    return preprocessed_df


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


def get_max_index(region_values, broken_index):
    start_value = region_values[broken_index - 1]

    index = broken_index + 1
    while index < len(region_values):
        if start_value <= region_values[index]:
            return index
        index += 1

    return -1


def interpolate(region_values, start_index, end_index):
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


def get_preprocessed_dict(country, pre_info):
    save_setting(pre_info, 'pre_info')

    data_dict = load_origin_data(country)
    population_df = load_population(country)

    preprocessed_dict = preprocess_data_dict(data_dict, pre_info, population_df)
    save_preprocessed_dict(country, pre_info, preprocessed_dict)

    return preprocessed_dict


if __name__ == '__main__':
    country = Country.ITALY
    link_df = load_links(country)
    population_df = load_population(country)

    pre_info = PreprocessInfo(start=link_df['start_date'], end=link_df['end_date'],
                              increase=True, daily=True, smoothing=True, window=5, divide=True)

    preprocessed_dict = get_preprocessed_dict(country, pre_info)

    sird_dict = convert_columns_to_sird(preprocessed_dict, pre_info, population_df)
    save_sird_dict(country, pre_info, sird_dict)
