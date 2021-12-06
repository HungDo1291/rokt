import sqlalchemy as sqla
import pandas as pd
import json
import os, sys

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import result


class SQLConnector:
    def __init__(self, database_type, database_name='',
                 user='', password='',
                 host='', port='',
                 echo=False):
        self.__db_connection_url = self.get_connection_url(database_type, database_name,
                                                           user, password,
                                                           host, port)

        self.__engine = sqla.create_engine(self.__db_connection_url, echo=echo)
        print('---connected to database ---')

        base = declarative_base()
        self.__metadata = sqla.MetaData(bind=self.__engine, reflect=True)

        # create events table in database
        try:
            events_table = self.__metadata.tables['events']
        except KeyError:
            print('Table events does not exits in this database.')
            events_table = None

        if events_table is not None:  # if table already exists in database, drop it.
            print('Table already exists in this database. Dropping this table...')
            base.metadata.drop_all(self.__engine, [events_table], checkfirst=True)
            self.__metadata = sqla.MetaData(bind=self.__engine, reflect=True)

        # Create table events
        print('Creating table... ')
        # Describe a table with the appropriate Columns
        events_table = sqla.Table('events', self.__metadata,
                                  sqla.Column('filename', sqla.VARCHAR(100), nullable=False),
                                  sqla.Column('datetime', sqla.DATETIME, nullable=False),
                                  sqla.Column('email', sqla.VARCHAR(100)),
                                  sqla.Column('session_id', sqla.VARCHAR(100)),
                                  extend_existing=True
                                  )

        # place a unique index on filename and datetime. Assuming that same time stamp can be repeated.
        sqla.Index('search_index', events_table.c.filename, events_table.c.datetime,
                   unique=False)

        # Create the table
        self.__metadata.create_all()



    def get_connection_url(self, database_type, database_name,
                           user, password,
                           host, port):

        if database_type == 'sqlite':  # inbuilt sqlite for testing
            url = 'sqlite:///{}'.format(os.path.join('rokt', 'resources', 'sqlite3_test.db'))
        else:  # connect to external SQL database
            url = sqla.engine.url.URL(database_type,
                                      user, password,
                                      host, port,
                                      database_name)

        return url

    def get_engine(self):
        return self.__engine

    # def get_connection(self):
    #     connection = self.__engine.connect()
    #     return connection
    #
    # def close_all_connections(self):
    #     self.__engine.dispose()

    def get_table(self, table_name):
        table = self.__metadata.tables[table_name]
        return table


class Results(result.ResultProxy):
    # This functions extend sqlalchemy query results,
    # adding functions that convert query result to dataframe and df chunk
    def __init__(self, results_proxy):
        context = results_proxy.context
        super().__init__(context)

    def to_df(self):

        columns = self.keys()
        rows = self.fetchall()
        df = pd.DataFrame(data=rows, columns=columns)

        return df

    def to_df_chunks(self, chunksize):

        columns = self.keys()
        while True:
            rows = self.fetchmany(chunksize)
            if not rows:
                rows = self.fetchall()
            if rows:
                df = pd.DataFrame(data=rows, columns=columns)

                yield df
            if not rows:
                break
