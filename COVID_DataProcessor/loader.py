from COVID_DataProcessor.datatype import Country, PreprocessInfo, DatasetInfo
from COVID_DataProcessor.io import load_links, load_I_df

from datetime import timedelta


class I_Loader:
    def __init__(self, I_df, data_info):
        self.test_start = data_info.test_start
        self.test_end = data_info.test_end
        self.x_frames = data_info.x_frames
        self.y_frames = data_info.y_frames

        self.initiate(I_df)

    def __len__(self):
        return self.len - (self.x_frames + self.y_frames) + 1

    def initiate(self, I_df):
        self.start = (self.test_start + timedelta(days=-self.x_frames)).strftime('%Y-%m-%d')
        self.end = (self.test_end + timedelta(days=self.y_frames-1)).strftime('%Y-%m-%d')
        self.I_df = I_df.loc[:, self.start:self.end]
        self.len = len(self.I_df.columns.to_list())

    def __getitem__(self, idx):
        idx += self.x_frames
        data = self.I_df.iloc[:, idx-self.x_frames:idx+self.y_frames]

        x = data.iloc[:, :self.x_frames]
        y = data.iloc[:, self.x_frames:]

        return x, y


if __name__ == '__main__':
    country = Country.ITALY
    link_df = load_links(country)

    pre_info = PreprocessInfo(start=link_df['start_date'], end=link_df['end_date'],
                              increase=True, daily=True, smoothing=True, window=5, divide=True)
    pre_hash = pre_info.get_hash()

    data_info = DatasetInfo(x_frames=15, y_frames=3,
                            test_start='201230', test_end='210306')

    I_df = load_I_df(country, pre_info)

    loader = I_Loader(I_df, data_info)
