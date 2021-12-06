import os
import pandas as pd
import sqlalchemy as sqla


def data_pipeline(sql_connector, database_type, files, commit):
    table = sql_connector.get_table('events')
    connection = sql_connector.get_connection()
    transaction = connection.begin()

    # process each input file
    for full_path in files:
        print('---processing ', full_path)
        filename = os.path.split(full_path)[-1]
        chunks = pd.read_csv(full_path, sep=' ', header=None, dtype='str', chunksize=10000)
        for df in chunks:
            print('...loading data in chunk from row ', df.index[0], ' to ', df.index[-1])

            # drop blank rows
            df.dropna(how="all", axis=0, inplace=True)

            # change column names and add col filename
            df.columns = (['datetime', 'email', 'session_id'])
            df['filename'] = filename

            # convert col datetime to datetime format
            df.loc[:, 'datetime'] = pd.to_datetime(df.loc[:, 'datetime'])  # sqlite only accepts datetime object
            if database_type == 'mysql+pymysql':
                df.loc[:, 'datetime'] = df.loc[:, 'datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')  # avoid error with mysql

            # print(df)
            # prepare data from df to dictionary
            # TODO: truncate the table before running, change to df.to_sql instead of uploading row by row.
            for i, row in df.iterrows():  # note that each rows has to be processed separately due to null entries that are dropped
                d = row.to_dict()
                data = {k: v for k, v in d.items() if pd.notnull(v)}  # drop null values since null dates cannot be inserted as far as I tried
                # print(data)
                try:
                    results_proxy = connection.execute(sqla.insert(table), data)
                except Exception as e:
                    print('ERROR: ', e, '\n')  # in case death row already exist, just skip it.
                    print('==> Skipped uploading this row to the database.\n')
            print('...Successfully upload to SQL server!')

    # commit if all files are processed without error
    if commit:  # commit only if user specify commit=Tue. This is to prevent loading the same data 2 times
        transaction.commit()
        print('Committed.')
    else:
        transaction.rollback()
        print('But rolled back anyway. To commit, explicitly set commit=True in run_processor')

    # close all current connections,
    # otherwise new connection later would not work
    sql_connector.close_all_connections()
    print('Closed connection to the database')
