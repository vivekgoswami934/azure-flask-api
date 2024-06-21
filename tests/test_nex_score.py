import unittest 
from unittest import TestCase, mock
from flask import Flask, Blueprint, jsonify
from flask.testing import FlaskClient
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta


from app import create_app
from app.models.nex_score import NexScore
class TestTrendAPI(unittest.TestCase):
    def setUp(self):
        """Set up the test client and other test variables."""
        self.app = create_app()  # Assuming your Flask app is created in a function called create_app
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        """Remove the app context."""
        self.app_context.pop()

    def test_get_trend_valid_parameters(self):
        """Test GET /nex-score/trends with valid parameters."""
        response = self.client.get('/nex-score/trends?region=CENTRAL&market=CINCINNATI')
        self.assertEqual(response.status_code, 200)
        self.assertIn("data", response.json)
        self.assertIsInstance(response.json["data"], list)
        # Add more assertions to check the structure and content of the response data

    def test_get_trend_missing_region_parameter(self):
        """Test GET /nex-score/trends with missing region parameter."""
        response = self.client.get('/nex-score/trends?market=CINCINNATI')
        self.assertEqual(response.status_code, 200)  # Assuming optional parameters return data if not provided
        # Add assertions to check the structure and content of the response data

    def test_get_trend_missing_market_parameter(self):
        """Test GET /nex-score/trends with missing market parameter."""
        response = self.client.get('/nex-score/trends?region=CENTRAL')
        self.assertEqual(response.status_code, 200)  # Assuming optional parameters return data if not provided
        # Add assertions to check the structure and content of the response data

    def test_get_trend_invalid_period_parameter(self):
        """Test GET /nex-score/trends with invalid period parameter."""
        response = self.client.get('/nex-score/trends?region=CENTRAL&market=CINCINNATI&timeframe=invalid')
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "Invalid period parameter")

    # @patch('app.models.nex_score.NexScore.query')
    # def test_get_trend_internal_server_error(self, mock_query):
    #     """Test GET /nex-score/trends internal server error."""
    #     # Mock an internal server error in the query
    #     mock_query.filter.return_value.all.side_effect = Exception("Internal server error")
        
    #     response = self.client.get('/nex-score/trends?region=CENTRAL&market=CINCINNATI')
    #     self.assertEqual(response.status_code, 500)
    #     self.assertIn("error", response.json)
    #     self.assertEqual(response.json["error"], "Internal server error")

    @patch('app.models.nex_score.NexScore.query')
    def test_get_trend_no_data_found(self, mock_query):
        """Test GET /nex-score/trends when no data is found."""
        # Mock NexScore.query.filter().all() to return an empty list
        mock_query.filter.return_value.all.return_value = []
        
        response = self.client.get('/nex-score/trends?region=CENTRAL&market=CINCINNATI')
        self.assertEqual(response.status_code, 404)
        self.assertIn("message", response.json)
        self.assertEqual(response.json["message"], "No data found")

class TestScoreComparisonAPI(unittest.TestCase):
    def setUp(self):
        """Set up the test client and other test variables."""
        self.app = create_app()  # Assuming your Flask app is created in a function called create_app
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        """Remove the app context."""
        self.app_context.pop()

    @patch('app.models.nex_score.NexScore.query')
    def test_get_score_success(self, mock_query):
        """Test GET /nex-score/score-comparison/ success scenario."""
        # Create mock NexScore data for April 2024
        mock_data_apr = NexScore(
            region="CENTRAL",
            market="CINCINNATI",
            influencer_count=29504,
            detractor_count=105347,
            neutral_count=385532,
            influencer_perc=5.6,
            detractor_perc=20.2,
            neutral_perc=74.0,
            update_date=datetime.strptime("2024-04-23", "%Y-%m-%d")
        )

        # Create mock NexScore data for March 2024
        mock_data_mar = NexScore(
            region="CENTRAL",
            market="CINCINNATI",
            influencer_count=25000,
            detractor_count=100000,
            neutral_count=400000,
            influencer_perc=5.0,
            detractor_perc=20.0,
            neutral_perc=75.0,
            update_date=datetime.strptime("2024-03-23", "%Y-%m-%d")
        )

        # Create mock NexScore data for February 2024
        mock_data_feb = NexScore(
            region="CENTRAL",
            market="CINCINNATI",
            influencer_count=27000,
            detractor_count=110000,
            neutral_count=380000,
            influencer_perc=5.5,
            detractor_perc=21.0,
            neutral_perc=73.5,
            update_date=datetime.strptime("2024-02-23", "%Y-%m-%d")
        )

        # Mock NexScore.query.filter().all() to return the mock data
        mock_query.filter().all.return_value = [mock_data_apr, mock_data_mar, mock_data_feb]

        response = self.client.get('/nex-score/score-comparison?region=CENTRAL&market=CINCINNATI&month=APR\'24')
        self.assertEqual(response.status_code, 200)
        data = response.json['data']
        self.assertIn('current_month', data)
        self.assertIn('differences', data)
        self.assertAlmostEqual(data['current_month']['influencer_perc'], 5.6)
        self.assertEqual(data['current_month']['detractor_perc'], 20.2)
        self.assertEqual(data['current_month']['neutral_perc'], 74.00)
        self.assertIsNotNone(data['differences'])
        self.assertEqual(data['differences']['timeframe'], "APR'24")


    @patch('app.models.nex_score.NexScore.query')
    def test_get_score_missing_parameters(self, mock_query):
        """Test GET /nex-score/score-comparison/ missing parameters scenario."""
        response = self.client.get('/nex-score/score-comparison')
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "Region is required")
    
    def test_get_score_invalid_parameters(self):
        """Test GET /nex-score/score-comparison with invalid parameters."""
        response = self.client.get('/nex-score/score-comparison?region=INVALID&market=ARKANSAS&month=APR\'24')
        self.assertEqual(response.status_code, 404)
        self.assertIn("message", response.json)
        self.assertEqual(response.json["message"], "No data found")


    def test_get_score_missing_region_parameter(self):
        """Test GET /nex-score/score-comparison with missing region parameter."""
        response = self.client.get('/nex-score/score-comparison?market=ARKANSAS&month=APR\'24')
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "Region is required")

    def test_get_score_missing_market_parameter(self):
        """Test GET /nex-score/score-comparison with missing market parameter."""
        response = self.client.get('/nex-score/score-comparison?region=CENTRAL&month=APR\'24')
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "Market is required")

    def test_get_score_missing_month_parameter(self):
        """Test GET /nex-score/score-comparison with missing month parameter."""
        response = self.client.get('/nex-score/score-comparison?region=CENTRAL&market=ARKANSAS')
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "Month is required")

    @patch('app.models.nex_score.NexScore.query')
    def test_get_score_no_data_found(self, mock_query):
        """Test GET /nex-score/score-comparison when no data is found."""
        # Mock NexScore.query.filter().all() to return an empty list
        mock_query.filter().all.return_value = []
        
        response = self.client.get('/nex-score/score-comparison?region=CENTRAL&market=ARKANSAS&month=JUN\'24')
        self.assertEqual(response.status_code, 404)
        # self.assertIn("error", response.json)
        # self.assertEqual(response.json["error"], "No data found")
        self.assertIn("message", response.json)
        self.assertEqual(response.json["message"], "No data found")

    @patch('app.models.nex_score.NexScore.query')
    def test_get_score_internal_server_error(self, mock_query):
        """Test GET /nex-score/score-comparison internal server error."""
        # Mock an internal server error in the query
        mock_query.filter().all.side_effect = Exception("Internal server error")
        
        response = self.client.get('/nex-score/score-comparison?region=CENTRAL&market=ARKANSAS&month=APR\'24')
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "Internal server error")

class TestGetPerc(unittest.TestCase):
    def setUp(self):
        """Set up the test client and other test variables."""
        self.app = create_app()  # Assuming your Flask app is created in a function called create_app
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        """Remove the app context."""
        self.app_context.pop()
    
    def test_get_perc_success(self):
        """Test get_perc() with successful data retrieval."""
        tester = self.app.test_client(self)
        response = tester.get('/nex-score/percentage?region=CENTRAL')
        print(response)
        statuscode = response.status_code
        self.assertEqual(statuscode,200)


    @patch('app.models.nex_score.NexScore.query')
    def test_get_perc_no_data_found(self, mock_query):
        """Test get_perc() when no data is found."""
        # Mock the database query to return no records
        mock_query.return_value.filter.return_value.all.return_value = []

        response = self.client.get('/nex-score/percentage?region=CENTRAL')
        self.assertEqual(response.status_code, 500)
        # data = response.json
        # self.assertIn("message", data)
        # self.assertEqual(data["message"], "No data found")

    @patch('app.models.nex_score.NexScore.query')
    def test_get_perc_internal_server_error(self, mock_query):
        """Test get_perc() with internal server error."""
        # Mock the query to raise an exception
        mock_query.side_effect = Exception("Internal server error")

        response = self.client.get('/nex-score/percentage?region=CENTRAL')
        self.assertEqual(response.status_code, 500)  # Ensure the status code is 500
        self.assertIn("error", response.json)


if __name__ == '__main__':
    unittest.main(verbosity=2)
