"""
Find cycle for a given stock
"""

import pandas_datareader as pdr
import pandas as pd
import matplotlib.pyplot as plt
import os.path
import warnings

api_key = '075bcce532428f40548b0dc38e63b33458de3aad'
warnings.filterwarnings("ignore")

def download_stock_data(stock):
    """Download data for the given stock symbol (e.g. MSFT) and save to
    a {stock}.csv file in this folder.
    """
    file_name = f'{stock}.csv'
    if os.path.isfile(file_name):
        print(f'{stock}.csv already exist, skip the download')
        return

    try:
        # Load data from tiingo.com
        data = pdr.get_data_tiingo(stock, api_key=api_key).loc[stock]
        print(f"Done: {stock}")
    except:
        print(f"Failed: {stock}")
        return

    # create file if not exists
    f = open(file_name, 'w+')
    f.close()

    # write data to csv
    data.to_csv(file_name, sep=',')
    print(f'{stock} data is downloaded, and saved to {file_name}')


def plot(stock):
    """Plot the daily stock price ("open" price every day)
    """
    stock_prices = pd.read_csv(f'{stock}.csv', sep=',')
    # Convert the date to datetime
    stock_prices['date'] = pd.to_datetime(stock_prices['date'], format = '%Y-%m-%d')
    # Assign this as index
    stock_prices.set_index(['date'], inplace=True)

    # plot the price
    stock_prices['open'].plot()
    plt.title(f'{stock} daily stock price')
    plt.xlabel('day')
    plt.ylabel('price')
    plt.savefig(f'{stock}.png')
    plt.show()

def plot_n_days_average(stock, n_days):
    """For every day, compute the n_days stock "open" price average from that day,
    then plot the graph.
    """
    stock_prices = pd.read_csv(f'{stock}.csv', sep=',')

    # Convert the date to datetime
    stock_prices['date'] = pd.to_datetime(stock_prices['date'], format = '%Y-%m-%d')
    # Assign this as index
    stock_prices.set_index(['date'], inplace=True)

    # compute n_days average
    for i in range(len(stock_prices)-n_days):
        sum = 0
        for j in range(n_days):
            sum += stock_prices["open"][i+j]
        stock_prices["open"][i] = sum/n_days

    # drop the last n rows
    stock_prices.drop(stock_prices.tail(n_days).index, inplace = True)

    # plot the price
    stock_prices['open'].plot()
    plt.title(f'{stock} {n_days}-day average')
    plt.xlabel('day')
    plt.ylabel('price')
    plt.savefig(f'{stock}_{n_days}-day_average.png')

def print_local_max_and_min(stock, n_days, percentage):
    """Print local max and local min, price and date
    Args:
        stock: e.g. MSFT
        n_days: use the n_days average open price as the stock value
        percentage: e.g. use 0.1 = 10%. If the current price is 10%
            lower than the current local max, then price is considered
            dropping; If the current price is 10% higher than the
            current local min, then the price is considered increasing.
            Otherwise, the price is considered stable to reduce the
            flucatuation noises.
    """
    stock_prices = pd.read_csv(f'{stock}.csv', sep=',')
    # Convert the date to datetime
    stock_prices['date'] = pd.to_datetime(stock_prices['date'], format = '%Y-%m-%d')

    for i in range(len(stock_prices)-n_days):
        sum = 0
        for j in range(n_days):
            sum += stock_prices["open"][i+j]
        stock_prices["open"][i] = sum/n_days
    
    increasing = True
    max_val = stock_prices["open"][0]
    max_date = stock_prices["date"][0]
    min_val = stock_prices["open"][0]
    min_date = stock_prices["date"][0]

    for i in range(len(stock_prices)-n_days):
        if i==0:
            continue
        cur = stock_prices["open"][i]
        cur_date = stock_prices["date"][i]

        if increasing and cur > max_val:
            max_val = cur
            max_date = cur_date
        if not increasing and cur < min_val:
            min_val = cur
            min_date = cur_date

        if cur > min_val+percentage*min_val and not increasing:
            print(f"stock local min, price {min_val}, at date: {min_date}")
            increasing = True
            max_val = cur
            max_date = cur_date
            min_val = cur
            min_date = cur_date
        elif cur < max_val-percentage*max_val and increasing:
            print(f"stock local max, price {max_val}, at date: {max_date}")
            increasing = False
            max_val = cur
            max_date = cur_date
            min_val = cur
            min_date = cur_date

    cur = len(stock_prices)-n_days-1
    print(f'stock current price {stock_prices["open"][cur]}, at date: {stock_prices["date"][cur]}')


if __name__ == "__main__":
    download_stock_data('MSFT')
    n_days = 30
    print_local_max_and_min('MSFT', n_days, 0.1)
    plot_n_days_average('MSFT', n_days)