from datetime import datetime, timedelta

import matplotlib.dates as mdates
import matplotlib.pyplot as plt


def plot_data_by_type(data_df, target_column, region,
                        fontsize=60, linewidth=5, grid_linewidth=2, figsize=(80, 15)):
    dates = data_df.index.tolist()
    start_date = datetime.strptime(dates[0], '%Y-%m-%d')
    x_value = [start_date + timedelta(days=i) for i in range(len(dates))]
    x_format = mdates.DateFormatter('%y%m%d')

    plt.rcParams.update({'font.size': fontsize})

    plt.figure(figsize=figsize)
    plt.plot(x_value, data_df.loc[:, target_column], linewidth=linewidth)

    plt.gca().xaxis.set_major_formatter(x_format)
    plt.suptitle(region)
    plt.grid(True, axis='x', which='both', linewidth=grid_linewidth)
    plt.show()
