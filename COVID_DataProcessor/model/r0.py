from COVID_DataProcessor.datatype import Country, PreprocessInfo
from COVID_DataProcessor.io import load_population, load_sird_dict, load_regions
from COVID_DataProcessor.io import load_us_confirmed_data, load_preprocessed_data
from COVID_DataProcessor.io import load_origin_data, save_first_confirmed_date, load_links, save_dataset_for_r0_model
from COVID_DataProcessor.preprocess.test_number import get_test_number

import pandas as pd


def get_dataset_for_r0_model(country, sird_info, test_info):
    first_confirmed_date_df = get_first_confirmed_date(country)
    population_df = load_population(country)
    test_num_df = get_test_number(country, test_info)
    pre_dict = load_preprocessed_data(country, sird_info)
    sird_dict = load_sird_dict(country, sird_info)

    dataset_dict = {'first_confirmed': first_confirmed_date_df, 'population': population_df,
                    'test_info': test_info, 'test_num': test_num_df,
                    'sird_info': sird_info, 'pre_dict': pre_dict, 'sird_dict': sird_dict}
    save_dataset_for_r0_model(country, dataset_dict)
    return dataset_dict


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


if __name__ == '__main__':
    country = Country.ITALY
    link_df = load_links(country)

    sird_info = PreprocessInfo(country=country, start=link_df['start_date'], end=link_df['end_date'],
                               increase=True, daily=True, remove_zero=True,
                               smoothing=True, window=5, divide=False)

    test_info = PreprocessInfo(country=country, start=link_df['start_date'], end=link_df['end_date'],
                              increase=True, daily=True, remove_zero=True,
                              smoothing=True, window=5, divide=False)

    dataset_dict = get_dataset_for_r0_model(country, sird_info, test_info)
