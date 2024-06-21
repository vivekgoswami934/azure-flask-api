# tests/test_app.py
import unittest
from flask import Flask
from unittest.mock import patch, MagicMock
from app import create_app, db
from app.models.nex_score import NexScore

class TestNexScoreAPI(unittest.TestCase):

    def setUp(self):
        """Set up the test client and other test variables."""
        self.app = create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        """Remove the app context."""
        self.app_context.pop()

    @patch('app.models.nex_score.NexScore.query')
    def test_get_nex_score_default(self, mock_query):
        """Test GET /nex-score/ success scenario with default type (influencer)."""
        nex_score1 = NexScore(market='Market1', region='Region1', update_date='2023-06-10',
                              influencer_count=10, influencer_perc=0.5,
                              detractor_count=5, detractor_perc=0.25,
                              neutral_count=5, neutral_perc=0.25)
        nex_score2 = NexScore(market='Market2', region='Region2', update_date='2023-06-11',
                              influencer_count=20, influencer_perc=0.7,
                              detractor_count=3, detractor_perc=0.1,
                              neutral_count=7, neutral_perc=0.2)
        # Mock the query result
        mock_query.join().filter().all.return_value = [nex_score1, nex_score2]

        response = self.client.get('/nex-score/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['type'], 'influencer')
        self.assertTrue('data' in response.json)

    @patch('app.models.nex_score.NexScore.query')
    def test_get_nex_score_influencer(self, mock_query):
        """Test GET /nex-score/?type=influencer."""
        # Mock the query result
        mock_query.join().filter().all.return_value = [
            MagicMock(
                market='market1',
                region='region1',
                update_date='2023-06-10',
                influencer_count=10,
                influencer_perc=0.5
            )
        ]

        response = self.client.get('/nex-score/?type=influencer')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['type'], 'influencer')
        self.assertTrue('data' in response.json)

    @patch('app.models.nex_score.NexScore.query')
    def test_get_nex_score_detractor(self, mock_query):
        """Test GET /nex-score/?type=detractor."""
        # Mock the query result
        # mock_query.join().filter().all.return_value = [
        #     MagicMock(
        #         market='market1',
        #         region='region1',
        #         update_date='2023-06-10',
        #         detractor_count=5,
        #         detractor_perc=0.25
        #     )
        # ]

        nex_score1 = NexScore(market='Market1', region='Region1', update_date='2023-06-10',
                              influencer_count=10, influencer_perc=0.5,
                              detractor_count=5, detractor_perc=0.25,
                              neutral_count=5, neutral_perc=0.25)
        nex_score2 = NexScore(market='Market2', region='Region2', update_date='2023-06-11',
                              influencer_count=20, influencer_perc=0.7,
                              detractor_count=3, detractor_perc=0.1,
                              neutral_count=7, neutral_perc=0.2)
        # Mock the query result
        mock_query.join().filter().all.return_value = [nex_score1, nex_score2]

        response = self.client.get('/nex-score/?type=detractor')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['type'], 'detractor')
        self.assertTrue('data' in response.json)

    @patch('app.models.nex_score.NexScore.query')
    def test_get_nex_score_neutral(self, mock_query):
        """Test GET /nex-score/?type=neutral."""
        # Mock the query result
        mock_query.join().filter().all.return_value = [
            MagicMock(
                market='market1',
                region='region1',
                update_date='2023-06-10',
                neutral_count=5,
                neutral_perc=0.25
            )
        ]

        response = self.client.get('/nex-score/?type=neutral')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['type'], 'neutral')
        self.assertTrue('data' in response.json)

    @patch('app.models.nex_score.NexScore.query')      #################################
    def test_get_nex_score_with_region(self, mock_query):
        """Test GET /nex-score/?region=Region1."""
        # Mock the query result
        mock_query.join().filter().all.return_value = [
            MagicMock(
                market='market1',
                region='region1',
                update_date='2023-06-10',
                influencer_count=10,
                influencer_perc=0.5
            )
        ]

        response = self.client.get('/nex-score/?region=Region1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['type'], 'influencer')
        self.assertTrue('data' in response.json)
        self.assertTrue(any(d['region'] == 'Region1' for d in response.json['data']))

    # @patch('app.models.nex_score.NexScore.query')
    # def test_get_nex_score_exception(self, mock_query):  #################################
    #     """Test GET /nex-score/ with exception handling."""
    #     # Simulate an exception
    #     mock_query.join().filter().all.side_effect = Exception("Database Error")

    #     response = self.client.get('/nex-score/')
    #     self.assertEqual(response.status_code, 500)
    #     self.assertIn("error", response.json)
    #     self.assertEqual(response.json["error"], "Database Error")

if __name__ == '__main__':
    unittest.main(verbosity=2)
