import pandas as pd
from .fileReader import fileReader
from io import StringIO


def load_csv(path):
    s = fileReader(path)

    csv_file = StringIO(s)

    df = pd.read_csv(csv_file, skiprows=1)
    df.drop(columns=['symbol', 'volume_btc'], inplace=True)

    # Fix timestamp form "2019-10-17 09-AM" to "2019-10-17 09-00-00 AM"
    df['date'] = df['date'].str[:14] + '00-00 ' + df['date'].str[-2:]

    # Convert the date column type from string to datetime for proper sorting.
    df['date'] = pd.to_datetime(df['date'])

    # Make sure historical prices are sorted chronologically, oldest first.
    df.sort_values(by='date', ascending=True, inplace=True)

    df.reset_index(drop=True, inplace=True)

    # Format timestamps as you want them to appear on the chart buy/sell marks.
    df['date'] = df['date'].dt.strftime('%Y-%m-%d %I:%M %p')

    # PlotlyTradingChart expects 'datetime' as the timestamps column name.
    df.rename(columns={'date': 'datetime'}, inplace=True)

    return df
