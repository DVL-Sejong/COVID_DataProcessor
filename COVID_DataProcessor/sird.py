from COVID_DataProcessor.datatype import Country, PreprocessInfo
from COVID_DataProcessor.io import load_links, load_sird_dict, load_r0_df, save_sird_initial_info
from COVID_DataProcessor.io import load_population, load_regions, load_preprocessed_data
from COVID_DataProcessor.preprocessing import get_preprocessed_dict
from COVID_DataProcessor.util import get_common_dates

import pandas as pd


if __name__ == '__main__':
    country = Country.US
    regions = load_regions(country)
    link_df = load_links(country)

    # SIRD data
    pre_info = PreprocessInfo(start=link_df['start_date'], end=link_df['end_date'],
                              increase=True, daily=True, smoothing=True, window=5, divide=False)
    sird_dict = load_sird_dict(country, pre_info)
    sird_dates = sird_dict[regions[0]].index.tolist()

    # R0, Mortality rate
    population_df = load_population(country)
    r0_df = load_r0_df(country)
    r0_dates = r0_df.columns.to_list()

    common_dates = get_common_dates(sird_dates, r0_dates)
    start_date = common_dates[0]
    end_date = common_dates[-1]

    pre_info = PreprocessInfo(start=link_df['start_date'], end=link_df['end_date'],
                              increase=True, daily=False, smoothing=True, window=5, divide=False)
    pre_dict = get_preprocessed_dict(country, pre_info)

    for region in regions:
        if region not in r0_df.index.tolist():
            continue

        region_df = pd.DataFrame(index=common_dates, columns=['r0', 'mortality_rate'])
        region_df.index.name = 'date'

        region_population = population_df.loc[region, 'population']
        region_df.loc[:, 'r0'] = r0_df.loc[region, start_date:end_date]
        region_df.loc[:, 'mortality_rate'] = pre_dict[region].loc[start_date:end_date, 'deaths'] / region_population
        save_sird_initial_info(region_df, country, region)
