import unittest
from rokt.api_server import api_server
from rokt.sql_connector import SQLConnector


class TestAPIClient(unittest.TestCase):

    def test_api_server(self):
        # connect to database using the default sqlite database and test table
        table_name = 'events_test'
        sql_connector = SQLConnector()

        # run the app test client
        app = api_server(sql_connector, table_name)
        client = app.test_client()
        response = client.get('/', follow_redirects=True)
        assert response.status_code == 200
