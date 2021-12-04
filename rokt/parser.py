import os, glob, getopt, sys
from rokt.sql_connector import SQLConnector
import pandas as pd
import sqlalchemy as sqla
from datetime import datetime as dt

def get_io(argument_list):

    # default arguments
    inputpath = 'resources'
    database_type = 'sqlite'  # for mysql, use 'mysql+pymysql'
    database_name = ''
    user = ''
    password = ''
    host = ''
    port = ''
    commit = False

    short_options = "hi:t:n:u:p:s:r:c"
    long_options = ["help", "inputpath=",  "database_type=", "database_name=", "user=", "password=", "host=", "port=", "commit"]
    try:
        opts, args = getopt.getopt(argument_list, short_options, long_options)
    except getopt.error as err:
        # Output error, and return with an error code
        print(str(err))
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print('To use this software package, use the command:')
            print(
                '"python -m rokt.parser -i <input path> -s <sql credentials file> -d <database name> (-c)"')
            print('"-c" is added only if you want to commit the change to the database.')
            print('If the input and output paths are not provided, the following default values are used: ')
            print('inputpath = "/resources", ')
            print('databasetype = "sqlite", and we will use the test db in resources folder ')
            print('database name = "events", ')
            print('So you can simply use the commands: `python -m rokt.parser` or `python -m rokt.parser -c`.')
            sys.exit()
        elif opt in ("-i", "--inputpath"):
            inputpath = arg
        elif opt in ("-t", "--database_type"):
            database_type = arg
        elif opt in ("-n", "--database_name"):
            database_name = arg
        elif opt in ("-u", "--user"):
            user = arg
        elif opt in ("-p", "--password"):
            password = arg
        elif opt in ("-s", "--host"):
            host = arg
        elif opt in ("-r", "--port"):
            port = arg
        elif opt in ("-c", "--commit"):
            commit = True

    return inputpath, database_type, database_name, user, password, host, port, commit


if __name__ == '__main__':

    # get command line arguments
    args = sys.argv[1:]

    if not args:
        print('no command line arguments. ')
        print('To learn commandline options, type "python -m processor -h")')
    else:
        print('the command line arguments that you passed are ', args, '\n')
        inputpath, database_type, database_name, user, password, host, port, commit = get_io(sys.argv[1:])
        print(inputpath, database_type, database_name, user, password, host, port, commit)

    # get all csv== files from the input path
    # files = glob.glob(os.path.join(ROOT_DIR, inputpath, '*.txt'))
    files = glob.glob(inputpath)

    # print list of files
    print('---list of uploaded csv files----')
    for inFile in files:
        print(inFile)
    print('------------------------')

    # connect to the database
    sql_connector = SQLConnector(database_type, database_name,
                                 user, password,
                                 host, port,
                                 echo=(not commit))  # do not print sql command in production mode
    table = sql_connector.get_table('events')
    connection = sql_connector.get_connection()
    transaction = connection.begin()
    print(table)
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
            df.loc[:, 'datetime'] = pd.to_datetime(df.loc[:, 'datetime']).dt.strftime('%Y-%m-%d %H:%M:%S')
            print(df)
            # prepare data from df to dictionary
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

        if commit:  # commit only if user specify commit=Tue. This is to prevent loading the same data 2 times
            transaction.commit()
            print('Committed.')
        else:
            transaction.rollback()
            print('But rolled back anyway. To commit, explicitly set commit=True in run_processor')
