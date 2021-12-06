import glob
import argparse

from rokt.sql_connector import SQLConnector
from rokt.data_pipeline import data_pipeline
from rokt.api_server import api_server

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
    sql_connector = SQLConnector(database_type, database_name,
                                 user, password,
                                 host, port,
                                 echo=(not commit))  # do not print sql command in production mode

    """----------------------------------"""
    """ run data pipeline and API server """
    """----------------------------------"""
    data_pipeline(sql_connector, database_type, files, commit)

    api_server(sql_connector)
