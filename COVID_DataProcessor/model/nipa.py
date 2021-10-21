from COVID_DataProcessor.datatype import Country, PreType, PreprocessInfo
from COVID_DataProcessor.io import load_population, sird_to_I, save_dataset_for_nipa_model, load_links


def get_dataset_for_sird_model(country, sird_info):
    population_df = load_population(country)
    I_df = sird_to_I(country, sird_info)

    dataset_dict = {'population': population_df,
                    'sird_info': sird_info,
                    'i': I_df}

    save_dataset_for_nipa_model(country, dataset_dict)
    return dataset_dict


if __name__ == '__main__':
    country = Country.ITALY
    link_df = load_links(country)

    sird_info = PreprocessInfo(country=country, start=link_df['start_date'], end=link_df['end_date'],
                               increase=True, daily=True, remove_zero=True,
                               smoothing=True, window=5, divide=False, pre_type=PreType.SIRD)

    dataset_dict = get_dataset_for_sird_model(country, sird_info)
