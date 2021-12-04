import sqlalchemy as sqla
import pandas as pd
import json
import os, sys

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base

ROOT_DIR = os.path.dirname(os.path.abspath('README.md'))


# print('Root directory is ', ROOT_DIR)


class SQLConnector():
    def __init__(self, database_type, database_name='',
                 user='', password='',
                 host='', port='',
                 echo=False):
        self.__db_connection_url = self.get_connection_url(database_type, database_name,
                                                           user, password,
                                                           host, port)

        self.__engine = sqla.create_engine(self.__db_connection_url, echo=echo)

        # create events table if not exist in database
        if not self.__engine.dialect.has_table(self.__engine, 'events'):  # If table don't exist, Create.
            print('Table events does not exist in database, creating ... ')
            self.__metadata = sqla.MetaData(self.__engine)

            # Describe a table with the appropriate Columns
            table = sqla.Table('events', self.__metadata,
                       sqla.Column('filename', sqla.VARCHAR(100), nullable=False),
                       sqla.Column('datetime', sqla.DATETIME, nullable=False),
                       sqla.Column('email', sqla.VARCHAR(100)),
                       sqla.Column('session_id', sqla.VARCHAR(100))
                       )

            # place a unique index on filename and datetime
            sqla.Index('search_index', table.c.filename, table.c.datetime, unique=True)

            # Create the table
            self.__metadata.create_all()
        else:
            # reflect the existing events table
            print('Table events already exists in database')
            self.__metadata = sqla.MetaData(bind=self.__engine, reflect=True)

        print('---connected to database ---')
        # # Ask SQLAlchemy to reflect the tables and
        # # create the corresponding ORM classes:
        # self.__Base = automap_base()
        # self.__Base.prepare(self.__engine, reflect=True)

    def get_connection_url(self, database_type, database_name,
                           user, password,
                           host, port):

        if database_type == 'sqlite':
            url = 'sqlite:///sqlite3_test.db'
            # url = 'sqlite:///{}'.format(os.path.join('resources', 'sqlite3_test.db'))
        else:
            url = sqla.engine.url.URL(database_type,
                                      user, password,
                                      host, port,
                                      database_name)

        return url

    def get_engine(self):
        return self.__engine

    def get_connection(self):
        connection = self.__engine.connect()
        return connection

    # def get_session(self):
    #     # create session
    #     Session = sessionmaker(bind=self.__engine)
    #     session = Session()
    #     return session

    # get table in for the old connection.execute. Might be depricated
    def get_table(self, table_name):
        table = self.__metadata.tables[table_name]
        return table

    # # get table from ORM Class, works for the new Session
    # def get_orm_table(self, table_name):
    #     table = self.__Base.classes[table_name]
    #     return table
    #
    # def truncate_orm_table(self, orm_table):
    #     self.__Base.metadata.drop_all(self.__engine, tables=[orm_table.__table__])
    #     self.__Base.metadata.create_all(self.__engine, tables=[orm_table.__table__])

    def csv_to_sql(self, file, table_name, commit=False):
        # read csv
        df = pd.read_csv(file, sep=',', index_col=False)  # , chunksize = 10000)
        print(df)
        print('read csv')

        print('...loading dataframe to SQL ... ')

        transaction = self.__connection.begin()  # start a transaction that commit only if successful

        try:
            df.to_sql(table_name, con=self.__connection,
                      if_exists='append', index=False)  # do not load the index because that will be repetitive
            print('Successfully upload to SQL server!')
            if commit:  # commit only if user specify commit=Tue. This is to prevent loading the same data 2 times
                transaction.commit()
                print('Committed.')
            else:
                transaction.rollback()
                print('But rolled back anyway. To commit, explicitly set commit=True in run_processor')
        except Exception as e:
            transaction.rollback()  # roll back if execution has error
            print('Query FAILED! Rolled back.')
            print(e)  # print the error

    # # TODO: merge two execution functions to an abstract method
    # def execute_to_sql(self, command, commit=False, display=True):
    #     print('... Executing command: ')
    #     if display:
    #         print(command)
    #
    #     # initialize connection
    #     connection = self.get_connection()
    #     transaction = connection.begin()  # start a transaction that commit only if successful
    #
    #     try:
    #         results_proxy = connection.execute(command)
    #         print('Successfully executed!')
    #         if commit:  # commit only if user specify commit=Tue. This is to prevent loading the same data 2 times
    #             transaction.commit()
    #             print('Committed.')
    #         else:
    #             transaction.rollback()
    #             print('But rolled back anyway. To commit, explicitly set commit=True in run_processor')
    #     except Exception as e:
    #         transaction.rollback()  # roll back if execution has error
    #         print('Query FAILED! Rolled back.')
    #         print(e)  # print the error
    #
    #     # close current session and connections,
    #     # otherwise new connection in loader would not work
    #     self.get_engine().dispose()
    #     print('Closed connection to the database')
    #
    #     return Results(results_proxy)
