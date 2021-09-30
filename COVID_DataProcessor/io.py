from COVID_DataProcessor.datatype import Country, PreprocessInfo
from COVID_DataProcessor.util import get_country_name
from dataclasses import fields
from os.path import join, abspath, dirname, isfile
from pathlib import Path

import pandas as pd

ROOT_PATH = Path(abspath(dirname(__file__))).parent
DATASET_PATH = join(ROOT_PATH, 'dataset')
SETTING_PATH = join(ROOT_PATH, 'settings')


def load_links(country=None):
    link_path = join(DATASET_PATH, 'links.csv')
    link_df = pd.read_csv(link_path, index_col='country')

    if country is not None:
        link_df = link_df.loc[get_country_name(country), :]

    return link_df


def load_population(country):
    population_path = join(DATASET_PATH, get_country_name(country), 'population.csv')
    population_df = pd.read_csv(population_path, index_col='regions')
    return population_df


def load_regions(country):
    population_df = load_population(country)
    regions = population_df.index.tolist()
    return regions


def load_origin_data(country):
    origin_path = join(DATASET_PATH, get_country_name(country), 'origin_data')
    regions = load_regions(country)
    data_dict = dict()

    for region in regions:
        region_df = pd.read_csv(join(origin_path, f'{region}.csv'), index_col='date')
        data_dict.update({region: region_df})

    return data_dict


def save_raw_file(country, raw_df, name):
    raw_path = join(DATASET_PATH, get_country_name(country), 'raw_data')
    Path(raw_path).mkdir(parents=True, exist_ok=True)

    raw_df.to_csv(join(raw_path, f'{name}.csv'))
    print(f'saving raw file to {raw_path}')


def save_dict(base_path, data_dict, data_name):
    for region, region_df in data_dict.items():
        saving_path = join(base_path, f'{region}.csv')
        region_df.to_csv(saving_path)
        print(f'saving {region} {data_name} data to {saving_path}')


def save_origin_data(country, df_dict):
    origin_path = join(DATASET_PATH, get_country_name(country), 'origin_data')
    Path(origin_path).mkdir(parents=True, exist_ok=True)
    save_dict(origin_path, df_dict, 'origin')


def save_preprocessed_dict(country, pre_info, preprocessed_dict):
    pre_path = join(DATASET_PATH, get_country_name(country), 'preprocessed_data', pre_info.get_hash())
    Path(pre_path).mkdir(parents=True, exist_ok=True)
    save_dict(pre_path, preprocessed_dict, 'preprocessed')


def save_sird_dict(country, pre_info, sird_dict):
    sird_path = join(DATASET_PATH, get_country_name(country), 'sird_data', pre_info.get_hash())
    Path(sird_path).mkdir(parents=True, exist_ok=True)
    save_dict(sird_path, sird_dict, 'SIRD')


def save_setting(param_class, class_name):
    new_param_dict = dict()
    new_param_dict.update({'hash': param_class.get_hash()})

    for field in fields(param_class):
        if field.name[0] == '_': continue
        new_param_dict.update({field.name: getattr(param_class, field.name)})

    param_df = pd.DataFrame(columns=list(new_param_dict.keys()))
    param_df = param_df.append(new_param_dict, ignore_index=True)
    param_df = param_df.set_index('hash')

    filename = f'{class_name}.csv'
    if isfile(join(SETTING_PATH, filename)):
        df = pd.read_csv(join(SETTING_PATH, filename), index_col='hash')
        if param_class.get_hash() not in df.index.tolist():
            df = param_df.append(df, ignore_index=False)
            df.to_csv(join(SETTING_PATH, filename))
            print(f'updating settings to {join(SETTING_PATH, filename)}')
    else:
        param_df.to_csv(join(SETTING_PATH, filename))
        print(f'saving settings to {join(SETTING_PATH, filename)}')


if __name__ == '__main__':
    country = Country.INDIA
    link_df = load_links().loc['India', :]
    data_dict = load_origin_data(country)
    population_df = load_population(country)
    pre_info = PreprocessInfo(start=link_df['start_date'], end=link_df['end_date'],
                              increase=True, daily=True, smoothing=True, window=5, divide=True)
    save_setting(pre_info, 'pre_info')
