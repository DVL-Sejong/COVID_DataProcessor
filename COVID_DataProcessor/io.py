from COVID_DataProcessor.datatype import Country
from os.path import join, abspath, dirname
from pathlib import Path

import pandas as pd

ROOT_PATH = Path(abspath(dirname(__file__))).parent
DATASET_PATH = join(ROOT_PATH, 'dataset')


def get_country_name(country):
    if country == Country.US:
        return country.name
    else:
        return country.name.capitalize()


def load_links():
    link_path = join(DATASET_PATH, 'links.csv')
    link_df = pd.read_csv(link_path, index_col='country')
    return link_df


def load_population(country):
    population_path = join(DATASET_PATH, get_country_name(country), 'population.csv')
    population_df = pd.read_csv(population_path, index_col='regions')
    return population_df


def load_regions(country):
    population_df = load_population(country)
    regions = population_df.index.tolist()
    return regions


def save_raw_file(country, raw_df, name):
    raw_path = join(DATASET_PATH, get_country_name(country), 'raw_data')
    Path(raw_path).mkdir(parents=True, exist_ok=True)

    raw_df.to_csv(join(raw_path, f'{name}.csv'))
    print(f'saving raw file to {raw_path}')


def save_origin_data(country, df_dict):
    origin_path = join(DATASET_PATH, get_country_name(country), 'origin_data')
    Path(origin_path).mkdir(parents=True, exist_ok=True)

    for region, region_df in df_dict.items():
        saving_path = join(origin_path, f'{region}.csv')
        region_df.to_csv(saving_path)
        print(f'saving {region} origin data to {saving_path}')


if __name__ == '__main__':
    print(load_regions(Country.ITALY))
