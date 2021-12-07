import unittest
from rokt.api_server import api_server
from rokt.sql_connector import SQLConnector
import json


class TestAPIClient(unittest.TestCase):
    def setUp(self):
        # connect to database using the default sqlite database and test table
        table_name = 'events_test'
        self.sql_connector = SQLConnector()

        # run the app test client
        app = api_server(self.sql_connector, table_name)
        self.client = app.test_client()

    def tearDown(self):
        engine = self.sql_connector.get_engine()
        engine.dispose()

    def test_api_server(self):

        response = self.client.get('/', follow_redirects=True)
        html = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(html, '<p>API server by Hung Do for Rokt.</p>')

        data = "{\"filename\": \"sample0.txt\", \"from\": \"1998-07-06T23:00:00Z\", \"to\": \"2021-12-06T23:00:00Z\"}"
        response = self.client.post('/', data=data, content_type='application/json')

        self.assertEqual(response.status_code, 200)

        actual = json.loads(response.get_data().decode("utf-8"))
        expected = [{"eventTime": "2000-01-01T17:25:49Z",
                     "email": "dedric_strosin@adams.co.uk",
                     "sessionId": "dfad33e7-f734-4f70-af29-c42f2b467142"},
                    {"eventTime": "2000-01-01T23:59:04Z",
                     "email": "abner@bartolettihills.com",
                     "sessionId": "b3daf720-6112-4a49-9895-62dda13a2932"},
                    {"eventTime": "2000-01-02T20:59:05Z",
                     "email": "janis_nienow@johnson.name",
                     "sessionId": "1f90471c-adc3-4daa-9a6d-ff9d184b7a61"},
                    {"eventTime": "2000-01-02T21:00:55Z",
                     "email": "casey.eichmann@hayes.us",
                     "sessionId": "56cc8832-9f9d-4dc5-b340-8dabc5107430"},
                    {"eventTime": "2000-01-03T16:13:52Z",
                     "email": "clotilde@nolanbalistreri.uk",
                     "sessionId": "8be575ca-2fa6-43d3-bf69-608b70c8be18"}]

        self.assertEqual(actual, expected)
        # app.run(port=8279, host='0.0.0.0')
