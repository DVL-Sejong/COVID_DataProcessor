# COVID_DataProcessor

### Dataset

We have preprocessed COVID-19 dataset of US, Italy, Chana, and India. Raw dataset of each country can be found [here](dataset/links.csv): 

- US: [JHU CSSE COVID-19 Dataset](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data), [link](https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports_us/)
  - Data for getting the date of first confirmed in states from [here](https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv)
- Italy: [Dati COVID-19 Italia](https://github.com/pcm-dpc/COVID-19), [link](https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv)
- China: [JHU CSSE COVID-19 Dataset](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data), [link](https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/)
- India: [COVID19-India API](https://github.com/covid19india/api), [link](https://api.covid19india.org/csv/latest/states.csv)

Population data are collected on online. Population of [US](dataset/US/population.csv), [Italy](dataset/Italy/population.csv), [China](dataset/China/population.csv), [India](dataset/India/population.csv) are on the links.



### How to use DataProcessor

- Download raw files from internet

  - Downloaded files are saved under `dataset\country_name\raw_data` and `dataset\country_name\origin_data`.

  ```python
  # Country that you want to download raw files
  # Country.US, Country,ITALY, Country.CHINA, Country.INDIA, Country.US_CONFIRMED are available
  country = Country.ITALY
  # download raw files
  raw_dict = download_raw_data(country)
  # preprocessing raw files into refined dataset
  origin_dict = get_origin_data(country)
  ```

- Preprocess dataset

  - You must download raw files and have refined dataset before preprocess the dataset.
  - Preprocessed dataset are saved under `dataset\county_name\preprocessed_data` and `dataset\country_name\sird_data`.
  - Preprocessing settings are saved `settings\pre_info.csv` and `settings\sird_info.csv`.

  ```python
  # Country that you want to preprocess raw files
  # Country.US, Country.ITALY, Country.CHINA, Country.INDIA are available
  country = Country.ITALY
  link_df = load_links(country)
  
  # set preprocess conditions
  sird_info = PreprocessInfo(country=country, start=link_df['start_date'], end=link_df['end_date'],
                             increase=True, daily=True, remove_zero=True,
                             smoothing=True, window=5, divide=False, pre_type=PreType.SIRD)
  
  # preprocess
  sird_dict = get_sird_dict(country, sird_info)
  ```

- Get exact dataset for model

  - You can get dataset for NIPA model or model for R0 estimation or SIRD model
  
  - Dataset for each model is saved under `results\model_name\`
  
- You must have preprocessed dataset for getting exact dataset for the model
  
  - [NIPA](https://github.com/DVL-Sejong/NIPA) model
  
    ```python
    country = Country.ITALY
    link_df = load_links(country)
    
    sird_info = PreprocessInfo(country=country, start=link_df['start_date'], end=link_df['end_date'],
                               increase=True, daily=True, remove_zero=True,
                               smoothing=True, window=5, divide=True, pre_type=PreType.SIRD)
    
    dataset_dict = get_dataset_for_sird_model(country, sird_info)
    ```
  
  - [R0_Estimation](https://github.com/DVL-Sejong/R0_Estimation)
  
    ```python
    country = Country.ITALY
    link_df = load_links(country)
    
    pre_info = PreprocessInfo(country=country, start=link_df['start_date'], end=link_df['end_date'],
                              increase=True, daily=True, remove_zero=True,
                              smoothing=True, window=5, divide=False, pre_type=PreType.PRE)
    
    test_info = PreprocessInfo(country=country, start=link_df['start_date'], end=link_df['end_date'],
                               increase=True, daily=True, remove_zero=True,
                               smoothing=True, window=5, divide=False, pre_type=PreType.TEST)
    
    dataset_dict = get_dataset_for_r0_model(country, pre_info, test_info)
    ```
  
  - [SIRD](https://github.com/DVL-Sejong/SIRD) model
  
    ```python
    country = Country.ITALY
    link_df = load_links(country)
    
    pre_info = PreprocessInfo(country=country, start=link_df['start_date'], end=link_df['end_date'],
                              increase=True, daily=True, remove_zero=True,
                              smoothing=True, window=5, divide=False, pre_type=PreType.PRE)
    test_info = PreprocessInfo(country=country, start=link_df['start_date'], end=link_df['end_date'],
                               increase=False, daily=True, remove_zero=True,
                               smoothing=True, window=5, divide=False, pre_type=PreType.TEST)
    
    dataset_dict = get_dataset_for_sird_model(country, pre_info, test_info)
    ```
  



### Preprocessing Conditions

- `PreprocessInfo` dataclass is used for passing preprocessing conditions. `increase`, `daily`, `remove_zero`, `smoothing`, `window`, `divide` are conditions used in the class.
- increase: remove anomalies in increasing data.
- daily: change cumulated data into daily data
- remove_zero: remove data below zero and fill up the gap using interpolate method.
- smoothing, window: apply moving average
- divide: divide data by its population
- pre_type
  - There are three types in PreType. pre_type is used for validate conditions for the type of the data.
  - `PRE`, `SIRD`, `TEST` are available to use.

### We are going to use...

- Ebola
  - [WHO, 2014년 11월 14일부터 2016년 5월 11일까지 주 단위로 업데이트](https://apps.who.int/gho/data/view.ebola-sitrep.ebola-summary-20141112?lang=en)
    - 확진 케이스와 사망 케이스에 대한 누적 데이터가 confirmed, probable, suspected, total로 제공
    - Guinea, Liberia, Sierra Leone 세 지역
  - [Congo, 2018년 8월 4일부터 2020년 7월 11일까지 일 단위로 업데이트](https://data.humdata.org/dataset/ebola-cases-and-deaths-drc-north-kivu)
    - National과 health zone 두 개로 나눠서 데이터셋 제공됨
    - csv 형식으로 제공되기 때문에 파싱 과정은 필요 없음
    - confirmed cases와 probable cases, confirmed deaths가 제공됨
  - [KNOEMA](https://knoema.com/atlas/topics/Ebola/datasets)
    - professional로 계정 전환해야 자료 볼 수 있다는데, 여기서 활용 가능한 데이터는 WHO 데이터밖에 없기 때문에 좀 더 찾아봐야 할 듯?
    - Regional WHO data on Ebola Cases in DR Congo/Guinea/Liberia/Sierra Leone
      - Total number of cases, suspected, probable, confirmed, deaths 제공