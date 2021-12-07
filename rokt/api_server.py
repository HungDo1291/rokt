from flask import Flask
from flask import request
import pandas as pd
import sqlalchemy as sqla

app = Flask(__name__)


def api_server(sql_connector, table_name='events'):

    @app.route('/')
    def home_page():
        return "<p>API server by Hung Do for Rokt.</p>"

    @app.route('/', methods=["POST"])
    def query():
        # get json
        req = request.get_json()

        # query from database
        t = sql_connector.get_table(table_name)

        filename = req['filename']
        from_time = pd.to_datetime(req["from"]).strftime('%Y-%m-%d %H:%M:%S')
        to_time = pd.to_datetime(req["from"]).strftime('%Y-%m-%d %H:%M:%S')

        command = t.select().where(sqla.and_(t.c.filename == filename,
                                             t.c.datetime >= from_time,
                                             t.c.datetime >= to_time
                                             )
                                   )

        df = sql_connector.execute_to_df(command)

        ret = df[['datetime', 'email', 'session_id']]
        # reformat the column names
        ret.columns = ['eventTime', 'email', 'sessionId']
        return ret.to_json(orient='records')  # convert to json format

    #app.run(port=8279, host='0.0.0.0')
    return app
