import glob, os
import argparse

from rokt.sql_connector import SQLConnector
from rokt.data_pipeline import process_chunk
from rokt.api_server import api_server
from joblib import Parallel, delayed,parallel_backend
import pandas as pd

if __name__ == '__main__':

    """------------------------------"""
    """ parse command line arguments """
    """------------------------------"""
    parser = argparse.ArgumentParser(description='digest sample files')
    default_input_path = '/usr/src/app/rokt/resources/*.txt'
    parser.add_argument('-i', '--input_path', type=str, default=default_input_path,
                        nargs='?', const=default_input_path)
    parser.add_argument('-t', "--database_type", type=str, default='sqlite', nargs='?', const='sqlite')
    parser.add_argument("-n", "--database_name", type=str, default='events', nargs='?', const='events')
    parser.add_argument("-u", "--user", type=str, default='root', nargs='?', const='root')
    parser.add_argument("-p", "--password", type=str, default='my_pass', nargs='?', const='my_pass')
    parser.add_argument("-s", "--host", type=str, default='host.docker.internal',
                        nargs='?', const='host.docker.internal')
    parser.add_argument("-r", "--port", type=int, default=3306, nargs='?', const=3306)
    parser.add_argument("-c", "--commit", type=bool, default=True, nargs='?', const=True)

    args = parser.parse_args()

    print('The command line arguments that you passed are ', args, '\n')
    input_path = args.input_path
    database_type = args.database_type
    database_name = args.database_name
    user = args.user
    password = args.password
    host = args.host
    port = args.port
    commit = args.commit
    # print(input_path, database_type, database_name, user, password, host, port, commit)

    """---------------------------------"""
    """ get and display all input files """
    """---------------------------------"""
    files = glob.glob(input_path)
    print('---list of input files----')
    for file in files:
        print(file)

    """---------------------------------"""
    """ connect to the database         """
    """---------------------------------"""
    table_name = 'events'
    sql_connector = SQLConnector(database_type, database_name,
                                 user, password,
                                 host, port, table_name=table_name,
                                 echo=False)  # do not print sql commands
    """----------------------------------"""
    """ run data pipeline                """
    """----------------------------------"""
    engine = sql_connector.get_engine()
    connection = engine.connect()
    transaction = connection.begin()

    # process each input file
    for full_path in files:
        print('---processing ', full_path)
        filename = os.path.split(full_path)[-1]

        # read every input file by chunks of 10000 rows
        chunks = pd.read_csv(full_path, sep=' ', header=None, dtype='str', chunksize=10000)

        # process chunks in parallel
        with parallel_backend("threading", n_jobs=8):
            Parallel()(delayed(process_chunk)(df, engine, filename, database_type, table_name) for df in chunks)

    # commit if all files are processed without error
    if commit:  # commit only if user specify commit=True. This is to prevent loading the same data 2 times
        transaction.commit()
        print('Committed.')
    else:
        transaction.rollback()
        print('But rolled back anyway. To commit, explicitly set commit=True in run_processor')

    # close all current connections,
    # otherwise new connections later would not work
    engine.dispose()
    print('Closed connection to the database')

    #data_pipeline(sql_connector, database_type, files, commit)

    """----------------------------------"""
    """ API server                       """
    """----------------------------------"""
    app = api_server(sql_connector, table_name)
    app.run(port=8279, host='0.0.0.0')
