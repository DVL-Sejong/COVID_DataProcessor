# COVID_DataProcessor

NIPA, DeepNIPA, DeepNIPA_baselines 등 COVID19 관련 레포지토리에서 사용하는 데이터를 전처리하는 기능을 수행합니다.

[첫 날 리스트 추출]

us
https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv

italy
원래 있던거에서 찾으면 될 듯

china
원래 있던거에서 찾으면 될 듯

india
원래 있던거에서 찾으면 될 듯

us -> 원본 데이터 'Total_Test_Results'에서 daily로 변환
china -> 없는데?
italy -> 'casi_testati'에서 daily로 변환
india -> 'Tested'에서 daily로 변환

### remove inadeguate regions

US
확정
california
district of columbia
florida
georgia
illinois
missouri
new jersey
new york
vermont
washington

후보
connecticut
delaware
messachusetts
nevada
oregon

CHINA

나라 데이터 자체가 이상함