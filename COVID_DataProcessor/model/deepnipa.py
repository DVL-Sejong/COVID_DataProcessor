from COVID_DataProcessor.datatype import PreType, Country, PreprocessInfo
from COVID_DataProcessor.io import load_population, save_dataset_for_deepnipa, load_links
from COVID_DataProcessor.preprocess.preprocess import get_sird_dict


def get_dataset_for_deepnipa(country, sird_info):
    population_df = load_population(country)
    sird_dict = get_sird_dict(country, sird_info)

    dataset_dict = {'population': population_df,
                    'sird_info': sird_info,
                    'sird_dict': sird_dict}
    save_dataset_for_deepnipa(country, dataset_dict)
    return dataset_dict


if __name__ == '__main__':
    country = Country.ITALY
    link_df = load_links(country)

    sird_info = PreprocessInfo(country=country, start=link_df['start_date'], end=link_df['end_date'],
                               increase=True, daily=True, remove_zero=True,
                               smoothing=True, window=5, divide=True, pre_type=PreType.SIRD)

    deepnipa_dataset = get_dataset_for_deepnipa(country, sird_info)
