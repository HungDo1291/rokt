import sqlalchemy as sqla
import pandas as pd
import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import result


class SQLConnector:
    def __init__(self, database_type='sqlite', database_name='',
                 user='', password='',
                 host='', port=3306, table_name='events_test',
                 echo=False):
        self.__db_connection_url = self.get_connection_url(database_type, database_name,
                                                           user, password,
                                                           host, port)

        self.__engine = sqla.create_engine(self.__db_connection_url, echo=echo)
        print('---connected to database ---')
        self.table_name = table_name

        if table_name == 'events':
            self.drop_and_create_events_table()
        else:
            self.__metadata = sqla.MetaData(bind=self.__engine, reflect=True)

    def drop_and_create_events_table(self):
        if self.__engine.dialect.has_table(self.__engine, self.table_name):  # if table already exists in database, drop it.
            print('Table already exists in this database. Dropping this table...')
            base = declarative_base()
            self.__metadata = sqla.MetaData(bind=self.__engine, reflect=True)
            events_table = self.__metadata.tables[self.table_name]
            base.metadata.drop_all(self.__engine, [events_table], checkfirst=True)

        self.__metadata = sqla.MetaData(bind=self.__engine, reflect=True)
        # Create table events
        print('Creating table... ')
        # Describe a table with the appropriate Columns
        events_table = sqla.Table(self.table_name, self.__metadata,
                                  sqla.Column('filename', sqla.VARCHAR(100), nullable=False),
                                  sqla.Column('datetime', sqla.DATETIME, nullable=False),
                                  sqla.Column('email', sqla.VARCHAR(100)),
                                  sqla.Column('session_id', sqla.VARCHAR(100)),
                                  extend_existing=True
                                  )

        # place a unique index on filename and datetime. Assuming that same time stamp can be repeated.
        sqla.Index('search_index', events_table.c.filename, events_table.c.datetime, unique=False)

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

    def get_connection(self):
        connection = self.__engine.connect()
        return connection
    #
    # def close_all_connections(self):
    #     self.__engine.dispose()

    def get_table(self, table_name):
        table = self.__metadata.tables[table_name]
        return table

    def execute_to_df(self, command, commit=False, display=False):
        print('... Executing command: ')
        if display:
            print(command)

        # initialize connection
        connection = self.get_connection()
        transaction = connection.begin()  # start a transaction that commit only if successful

        try:
            results_proxy = connection.execute(command)
            print('Successfully executed!')
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

        # close current session and connections,
        # otherwise new connection in loader would not work
        self.get_engine().dispose()
        print('Closed connection to the database')

        return Results(results_proxy).to_df()


class Results(result.ResultProxy):
    # This function extends sqlalchemy query results,
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
