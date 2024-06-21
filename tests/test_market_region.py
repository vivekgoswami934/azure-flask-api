import unittest
from flask import Flask, Blueprint
from flask.testing import FlaskClient
from unittest.mock import patch, MagicMock

# Import your app and blueprint
from app import create_app
from app.models.nex_score import NexScore

class TestMarketRegionRoutes(unittest.TestCase):
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
    def test_get_dropdown_values_success(self, mock_query):
        """Test GET /market-region/ success scenario."""
        # Mock the distinct values
        mock_query.with_entities().distinct().all.return_value = [
            ('market1', 'region1'),
            ('market2', 'region2'),
        ]

        response = self.client.get('/market-region/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {
            'data': [
                {'market': 'market1', 'region': 'region1'},
                {'market': 'market2', 'region': 'region2'}
            ]
        })

    @patch('app.models.nex_score.NexScore.query')
    def test_get_dropdown_values_internal_error(self, mock_query):
        """Test GET /market-region/ error scenario."""
        # Simulate an exception
        mock_query.with_entities().distinct().all.side_effect = Exception("Database Error")

        response = self.client.get('/market-region/')
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "Database Error")

if __name__ == '__main__':
    unittest.main(verbosity=10)  
