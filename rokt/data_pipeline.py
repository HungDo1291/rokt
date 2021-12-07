import os
import pandas as pd
# import sqlalchemy as sqla
# from joblib import Parallel, delayed, parallel_backend
#
#
# def data_pipeline(sql_connector, database_type, files, commit):
#     engine = sql_connector.get_engine()
#     connection = engine.connect()
#     transaction = connection.begin()
#
#     # process each input file
#     for full_path in files:
#         print('---processing ', full_path)
#         filename = os.path.split(full_path)[-1]
#         chunks = pd.read_csv(full_path, sep=' ', header=None, dtype='str', chunksize=10000)
#         # for df in chunks:
#         #     process_chunk(df, engine, filename, database_type)
#         with parallel_backend("threading", n_jobs=8):
#             Parallel(n_jobs=8)(delayed(process_chunk)(df, engine, filename, database_type) for df in chunks)
#
#     # commit if all files are processed without error
#     if commit:  # commit only if user specify commit=Tue. This is to prevent loading the same data 2 times
#         transaction.commit()
#         print('Committed.')
#     else:
#         transaction.rollback()
#         print('But rolled back anyway. To commit, explicitly set commit=True in run_processor')
#
#     # close all current connections,
#     # otherwise new connections later would not work
#     engine.dispose()
#     print('Closed connection to the database')


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
