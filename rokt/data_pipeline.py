import pandas as pd


def process_chunk(df, engine, filename, database_type, table_name='events'):
    print('...loading data in chunk from row ', df.index[0], ' to ', df.index[-1])

    # process the dataframe
    df = process_df(df, filename, database_type)

    # loading dataframe to sql
    try:
        df.to_sql(table_name, con=engine, index=False, if_exists='append')
    except Exception as e:
        print('ERROR: ', e, '\n')
    print('...Successfully upload to SQL server!')


def process_df(df, filename, database_type):
    # drop blank rows
    df.dropna(how="all", axis=0, inplace=True)

    # change column names and add col filename
    df.columns = (['datetime', 'email', 'session_id'])
    df['filename'] = filename

    # convert col datetime to datetime format
    df.loc[:, 'datetime'] = pd.to_datetime(df.loc[:, 'datetime'], errors='coerce')
    df.dropna(subset=['datetime'], axis=0, inplace=True)  # drop rows with empty datetime

    if database_type == 'mysql+pymysql':
        df.loc[:, 'datetime'] = df.loc[:, 'datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')  # avoid error with mysql
    return df
