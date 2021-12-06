from flask import Flask
from flask import request
import pandas as pd
from datetime import datetime
from rokt.sql_connector import Results


def api_server(sql_connector):
    app = Flask(__name__)

    @app.route('/')
    def web():
        return "<p>API server by Hung Do for Rokt.</p>"

    @app.route('/', methods=["POST"])
    def query():
        req = request.get_json()
        # TODO: rewrite raw SQL command with SQLAlchemy
        df = pd.read_sql(f'select * from events '
                         f'where datetime >= "{req["from"]}" '
                         f'and datetime <= "{req["to"]}"'
                         f' and filename="{req["filename"]}"', con=sql_connector.get_engine())
        ret = df[['datetime', 'email', 'session_id']]
        ret.columns = ['eventTime', 'email', 'sessionId']
        return ret.to_json(orient='records')

    app.run(port=8279, host='0.0.0.0')




