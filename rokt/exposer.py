# TODO: change name to api_server
from flask import Flask
from flask import request
from rokt.sql_connector import SQLConnector
import pandas as pd
app = Flask(__name__)
# connect to the database
sql_connector = SQLConnector(database_type='sqlite')  # do not print sql command in production mode
table = sql_connector.get_table('events')
connection = sql_connector.get_connection()
transaction = connection.begin()


@app.route('/')
def web():
    return "<p>Thanks</p>"

@app.route('/', methods=["POST"])
def api():
    req = request.get_json()
    # TODO: rewrite raw SQL command with SQLAlchemy
    df = pd.read_sql(f'select * from events '
                     f'where datetime >= "{req["from"]}" '
                     f'and datetime <= "{req["to"]}"'
                     f' and filename="{req["filename"]}"', con=sql_connector.get_engine())
    ret = df[['datetime', 'email', 'session_id']]
    ret.columns = ['eventTime', 'email', 'sessionId']
    return ret.to_json(orient='records')

app.run(port=8279)




