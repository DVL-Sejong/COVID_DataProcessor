from COVID_DataProcessor.datatype import Country, PreprocessInfo, get_country_name
from COVID_DataProcessor.util import get_period, path_to_name
from dataclasses import fields
from os.path import join, abspath, dirname, isfile
from pathlib import Path
from glob import glob

import pandas as pd


ROOT_PATH = Path(abspath(dirname(__file__))).parent
DATASET_PATH = join(ROOT_PATH, 'dataset')
SETTING_PATH = join(ROOT_PATH, 'settings')
RESULT_PATH = join(ROOT_PATH, 'results')


def get_safe_path(directory_list):
    safe_path = ''

    for directory in directory_list:
        safe_path = join(safe_path, directory)

    Path(safe_path).mkdir(parents=True, exist_ok=True)
    return safe_path


def get_base_path(country):
    return get_safe_path([RESULT_PATH, get_country_name(country)])


def load_links(country=None):
    link_path = join(DATASET_PATH, 'links.csv')
    link_df = pd.read_csv(link_path, index_col='country')
    return link_df.loc[get_country_name(country), :] if country is not None else link_df


def load_population(country, region=None):
    population_path = join(DATASET_PATH, get_country_name(country), 'population.csv')
    population_df = pd.read_csv(population_path, index_col='regions')
    return population_df if region is None else population_df.loc[region, 'population']


def load_regions(country):
    population_df = load_population(country)
    regions = population_df.index.tolist()
    regions.sort()
    return regions


def load_raw_data(country):
    raw_path = join(DATASET_PATH, get_country_name(country), 'raw_data')
    raw_path_list = glob(join(raw_path, '*.csv'))

    if len(raw_path_list) == 0:
        print(f'Raw data of {get_country_name(country)} is not existing!')
        raise FileNotFoundError(raw_path)

    raw_dict = dict()
    for file_path in raw_path_list:
        file_name = path_to_name(file_path)
        raw_df = pd.read_csv(file_path)
        raw_dict.update({file_name: raw_df})

    return raw_dict


def load_origin_data(country):
    origin_path = join(DATASET_PATH, get_country_name(country), 'origin_data')
    regions = load_regions(country)
    data_dict = dict()

    for region in regions:
        region_df = pd.read_csv(join(origin_path, f'{region}.csv'), index_col='date')
        data_dict.update({region: region_df})

    return data_dict


def load_us_confirmed_data():
    origin_path = join(DATASET_PATH, get_country_name(Country.US_CONFIRMED), 'origin_data')
    saving_path = join(origin_path, 'US_CONFIRMED.csv')
    us_confirmed_df = pd.read_csv(saving_path, index_col='regions')
    return us_confirmed_df


def load_first_confirmed_date(country):
    first_date_path = join(RESULT_PATH, 'SIRD', get_country_name(country), 'first_confirmed_date.csv')
    first_confirmed_date_df = pd.read_csv(first_date_path, index_col='regions')
    return first_confirmed_date_df


def load_preprocessed_data(country, pre_info):
    pre_path = join(DATASET_PATH, get_country_name(country), pre_info.get_hash())
    regions = load_regions(country)
    pre_dict = dict()

    for region in regions:
        region_df = pd.read_csv(join(pre_path, f'{region}.csv'), index_col='date')
        pre_dict.update({region: region_df})

    return pre_dict


def load_sird_dict(country, pre_info):
    sird_path = join(DATASET_PATH, get_country_name(country), 'sird_data', pre_info.get_hash())
    sird_path_list = glob(f'{sird_path}/*.csv')

    sird_dict = dict()
    for target_path in sird_path_list:
        region_name = path_to_name(target_path)
        sird_df = pd.read_csv(target_path, index_col='date')
        sird_dict.update({region_name: sird_df})

    return sird_dict


def load_I_df(country, pre_info):
    i_path = join(DATASET_PATH, get_country_name(country), 'i_data', pre_info.get_hash(), 'I.csv')
    I_df = pd.read_csv(i_path, index_col='regions')
    return I_df


def sird_to_I(country, pre_info):
    regions = load_regions(country)
    link_df = load_links(country)
    dates = get_period(start_date=link_df['start_date'], end_date=link_df['end_date'], out_date_format='%Y-%m-%d')

    I_df = pd.DataFrame(index=regions, columns=dates)
    I_df.index.name = 'regions'

    sird_dict = load_sird_dict(country, pre_info)
    for region, sird_df in sird_dict.items():
        region_I = sird_df.loc[:, 'infected']
        I_df.loc[region, :] = region_I

    return I_df


def load_r0_df(country):
    r0_path = join(DATASET_PATH, get_country_name(country), 'r0.csv')
    r0_df = pd.read_csv(r0_path, index_col='regions')
    return r0_df


def load_test_number(country, test_info):
    test_path = join(RESULT_PATH, get_country_name(country), 'number_of_tests', test_info.get_hash())
    test_df = pd.read_csv(join(test_path, 'number_of_tests.csv'), index_col='regions')
    return test_df


def save_raw_file(country, raw_df, name):
    raw_path = get_safe_path([DATASET_PATH, get_country_name(country), 'raw_data'])
    raw_df.to_csv(join(raw_path, f'{name}.csv'), index=False)
    print(f'saving raw file to {raw_path}')


def save_dict(base_path, data_dict, data_name):
    index = False if data_name == 'raw' else None

    for region, region_df in data_dict.items():
        saving_path = join(base_path, f'{region}.csv')
        region_df.to_csv(saving_path, index=index)
        print(f'saving {region} {data_name} data to {saving_path}')


def save_raw_data(country, raw_dict):
    raw_path = get_safe_path([DATASET_PATH, get_country_name(country), 'raw_data'])
    save_dict(raw_path, raw_dict, 'raw')


def save_origin_data(country, df_dict):
    origin_path = get_safe_path([DATASET_PATH, get_country_name(country), 'origin_data'])
    save_dict(origin_path, df_dict, 'origin')


def save_preprocessed_dict(country, pre_info, preprocessed_dict):
    pre_path = get_safe_path([DATASET_PATH, get_country_name(country), 'preprocessed_data', pre_info.get_hash()])
    save_dict(pre_path, preprocessed_dict, 'preprocessed')


def save_sird_dict(country, pre_info, sird_dict, base_path=None):
    if base_path is None:
        sird_list = [DATASET_PATH, get_country_name(country), 'sird_data', pre_info.get_hash()]
    else:
        sird_list = [base_path, 'sird', pre_info.get_hash()]
    sird_path = get_safe_path(sird_list)
    save_dict(sird_path, sird_dict, 'SIRD')


def save_I_df(country, pre_info, I_df):
    i_path = get_safe_path([DATASET_PATH, get_country_name(country), 'i_data', pre_info.get_hash()])
    saving_path = join(i_path, 'I.csv')
    I_df.to_csv(saving_path)
    print(f'saving I_df to {saving_path}')


def save_sird_initial_info(pre_info, initial_df, country, region, base_path=None):
    base_path = get_base_path(country) if base_path is None else base_path
    initial_path = get_safe_path([base_path, 'initial_values', pre_info.get_hash()])
    saving_path = join(initial_path, f'{region}.csv')
    initial_df.to_csv(saving_path)
    print(f'saving {region} initial value to {saving_path}')


def save_first_confirmed_date(country, first_confirmed_date_df, base_path=None):
    base_path = get_base_path(country) if base_path is None else base_path
    saving_path = join(base_path, 'first_confirmed_date.csv')
    first_confirmed_date_df.to_csv(saving_path)
    print(f'saving first confirmed date of {country.name} to {saving_path}')


def save_test_number(country, pre_info, test_num_df, base_path=None):
    base_path = get_base_path(country) if base_path is None else base_path
    test_number_path = get_safe_path([base_path, 'number_of_tests', pre_info.get_hash()])
    saving_path = join(test_number_path, 'number_of_tests.csv')
    test_num_df.to_csv(saving_path)
    print(f'saving data of number of tests in {country.name} to {saving_path}')


def save_dataset_for_r0_model(country, dataset_dict):
    dataset_path = get_safe_path([RESULT_PATH, 'R0', get_country_name(country)])
    print(f'save dataset for r0 estimating model under {dataset_path}')
    save_test_number(country, dataset_dict['test_info'], dataset_dict['test_num'], dataset_path)
    save_sird_dict(country, dataset_dict['sird_info'], dataset_dict['sird_dict'], dataset_path)
    save_first_confirmed_date(country, dataset_dict['first_confirmed'], dataset_path)
    dataset_dict['population'].to_csv(join(dataset_path, 'population.csv'))


def save_infectious_period(country, period_df, base_path=None):
    base_path = get_base_path(country) if base_path is None else base_path
    period_path = join(base_path, 'infectious_period.csv')
    period_df.to_csv(period_path)
    print(f'saving infectious period to {period_path}')


def save_sird_initial_dict(country, initial_dict, sird_info, base_path):
    for key, initial_df in initial_dict.items():
        save_sird_initial_info(sird_info, initial_df, country, key, base_path)


def save_dataset_for_sird_model(country, dataset_dict):
    dataset_path = get_safe_path([RESULT_PATH, 'SIRD', get_country_name(country)])
    print(f'save dataset for SIRD model under {dataset_path}')
    save_infectious_period(country, dataset_dict['infectious_period'], dataset_path)
    dataset_dict['population'].to_csv(join(dataset_path, 'population.csv'))
    save_sird_initial_dict(country, dataset_dict['initial_dict'], dataset_dict['sird_info'], dataset_path)
    save_sird_dict(country, dataset_dict['sird_info'], dataset_dict['sird_dict'], dataset_path)


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
        Path(SETTING_PATH).mkdir(parents=True, exist_ok=True)
        param_df.to_csv(join(SETTING_PATH, filename))
        print(f'saving settings to {join(SETTING_PATH, filename)}')


if __name__ == '__main__':
    country = Country.INDIA
    link_df = load_links().loc['India', :]
    data_dict = load_origin_data(country)
    population_df = load_population(country)
    pre_info = PreprocessInfo(country=country, start=link_df['start_date'], end=link_df['end_date'],
                              increase=True, daily=True, remove_zero=True,
                              smoothing=True, window=5, divide=True)
    save_setting(pre_info, 'pre_info')
