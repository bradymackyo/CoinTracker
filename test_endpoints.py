import unittest
import json
import logging
from unittest.mock import patch
import main
from db import Database
import db_functions as dbf


class TestAPIEndpoints(unittest.TestCase):

    def setUp(self):
        # disable logging 
        logging.disable(logging.CRITICAL)

        # use in memory db
        main.db_file = ':memory:'
        main.db = Database(':memory:')
        dbf.initialize_empty_tables(main.db)

        # flask instance
        main.app.config['TESTING'] = True
        self.client = main.app.test_client()

    def tearDown(self):
        # Re-enable logging after tests
        logging.disable(logging.NOTSET)
        main.db.close()

    # USER MANAGEMENT TESTS

    def test_add_user_success(self):
        with patch('blockchain.get_address_data_blockchain_com') as mock_bc:
            mock_bc.return_value = {'success': True}

            response = self.client.post('/add_user',
                json={'name': 'TestUser', 'addresses': ['addr1', 'addr2']})

            self.assertEqual(response.status_code, 201)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['name'], 'TestUser')
            self.assertEqual(len(data['addresses']), 2)

    def test_add_user_missing_name(self):
        # check missing name
        response = self.client.post('/add_user', json={})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_generate_random_user(self):
        with patch('blockchain.get_address_data_blockchain_com') as mock_bc:
            mock_bc.return_value = {'success': True}

            response = self.client.post('/generate_random_user')

            self.assertEqual(response.status_code, 201)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertIn('user_id', data)
            self.assertIn('name', data)

    def test_retrieve_user_data_success(self):
        with patch('blockchain.get_address_data_blockchain_com') as mock_bc:
            mock_bc.return_value = {'success': True}

            response = self.client.post('/add_user',
                json={'name': 'TestUser', 'addresses': ['addr1']})
            user_id = json.loads(response.data)['user_id']

            response = self.client.get(f'/retrieve_user_data?user_id={user_id}')

            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['name'], 'TestUser')

    def test_retrieve_user_data_not_found(self):
        response = self.client.get('/retrieve_user_data?user_id=9999')
        self.assertEqual(response.status_code, 404)

    def test_get_all_users(self):
        with patch('blockchain.get_address_data_blockchain_com') as mock_bc:
            mock_bc.return_value = {'success': True}

            self.client.post('/add_user', json={'name': 'User1', 'addresses': []})
            self.client.post('/add_user', json={'name': 'User2', 'addresses': []})

            response = self.client.get('/get_all_users')

            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIsInstance(data, list)
            self.assertEqual(len(data), 2)

    # ADDRESS MANAGEMENT TESTS

    def test_add_addresses_success(self):
        with patch('blockchain.get_address_data_blockchain_com') as mock_bc:
            mock_bc.return_value = {'success': True}

            response = self.client.post('/add_user',
                json={'name': 'TestUser', 'addresses': ['addr1']})
            user_id = json.loads(response.data)['user_id']

            response = self.client.post('/add_addresses',
                json={'user_id': user_id, 'addresses': ['addr2', 'addr3']})

            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(len(data['addresses']), 3)

    def test_add_addresses_user_not_found(self):
        response = self.client.post('/add_addresses',
            json={'user_id': 9999, 'addresses': ['addr1']})
        self.assertEqual(response.status_code, 404)

    def test_remove_addresses_success(self):
        with patch('blockchain.get_address_data_blockchain_com') as mock_bc:
            mock_bc.return_value = {'success': True}

            response = self.client.post('/add_user',
                json={'name': 'TestUser', 'addresses': ['addr1', 'addr2', 'addr3']})
            user_id = json.loads(response.data)['user_id']

            response = self.client.post('/remove_addresses',
                json={'user_id': user_id, 'addresses': ['addr2']})

            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(len(data['addresses']), 2)
            self.assertEqual(data['removed_count'], 1)

    # BLOCKCHAIN DATA TESTS

    def test_get_address_data_success(self):
        mock_data = {
            'success': True,
            'address': 'test_addr',
            'final_balance': 50000,
            'n_tx': 10
        }

        with patch('blockchain.get_address_data_blockchain_com') as mock_bc:
            mock_bc.return_value = mock_data

            response = self.client.post('/get_address_data',
                json={'addresses': ['test_addr']})

            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertIn('results', data)
            self.assertIn('test_addr', data['results'])

    def test_get_address_data_empty_list(self):
        response = self.client.post('/get_address_data',
            json={'addresses': []})
        self.assertEqual(response.status_code, 400)

    def test_get_raw_address_data_success(self):
        mock_data = {
            'address': 'test_addr',
            'final_balance': 50000,
            'txs': []
        }

        with patch('blockchain.get_address_data_blockchain_com') as mock_bc:
            mock_bc.return_value = mock_data

            response = self.client.get('/get_raw_address_data?address=test_addr')

            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['address'], 'test_addr')

    def test_get_raw_address_data_missing_address(self):
        response = self.client.get('/get_raw_address_data')
        self.assertEqual(response.status_code, 400)

    # TRANSACTION TESTS

    def test_get_txns_by_user_success(self):
        with patch('blockchain.get_address_data_blockchain_com') as mock_bc:
            mock_bc.return_value = {'success': True}

            # Create user with addresses
            response = self.client.post('/add_user',
                json={'name': 'TestUser', 'addresses': ['addr1']})
            user_id = json.loads(response.data)['user_id']

            # Get transactions
            response = self.client.get(f'/get_txns_by_user?user_id={user_id}')

            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['user_id'], user_id)
            self.assertIn('addresses', data)

    def test_get_txns_by_user_not_found(self):
        response = self.client.get('/get_txns_by_user?user_id=9999')
        self.assertEqual(response.status_code, 404)

    def test_get_txns_by_address_success(self):
        with patch('blockchain.get_address_data_blockchain_com') as mock_bc:
            mock_bc.return_value = {'success': True}

            response = self.client.get('/get_txns_by_address?address=test_addr')

            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['address'], 'test_addr')
            self.assertIn('transactions', data)

    def test_get_txns_by_address_missing_address(self):
        response = self.client.get('/get_txns_by_address')
        self.assertEqual(response.status_code, 400)

    def test_get_all_txns(self):
        response = self.client.get('/get_all_txns')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)


if __name__ == '__main__':
    unittest.main(verbosity=2)
