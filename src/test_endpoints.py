import json
import os
import requests
import sys
import unittest

sys.path.insert(0, os.environ.get('PROJECT_ROOT_PATH'))

from src.basics import DATABASE_PARAMS, TITULO_TESOURO_CATEGORIES, TITULO_TESOURO_ACTIONS
from src.system_loader import drop_database, create_database, read_xlsx, populate_database


class TestRequestHandler(unittest.TestCase):

    BASE_URL = 'http://localhost:8000/titulo_tesouro'

    def setUp(self):
        drop_database(verbose=False)
        create_database(verbose=False)

    def tearDownClass():
        drop_database(verbose=False)
 

class TestTituloTesouroRefinedRequestHandler(TestRequestHandler):

    def setUp(self):
        super(TestTituloTesouroRefinedRequestHandler, self).setUp()

        values = read_xlsx('input-data.xlsx', verbose=False)
        populate_database(values, verbose=False)

    def test_get_by_action_with_with_non_existing_titulo_id(self):
        resp = requests.get('{}/venda/99999'.format(TestRequestHandler.BASE_URL))

        self.assertEqual(resp.status_code, 404)
        self.assertIn('err', resp.json())
        self.assertEqual(resp.json()['err'], '"titulo_id" has no register for action "venda".')

    def test_get_by_action_with_non_positive_integer_in_data_inicio(self):
        resp = requests.get('{}/venda/1'.format(TestRequestHandler.BASE_URL), params={
            'data_inicio': '-2015-05'
        })

        self.assertEqual(resp.status_code, 400)
        self.assertIn('err', resp.json())
        self.assertEqual(resp.json()['err'], 'date not in format "YYYY-mm"')

    def test_get_by_action_with_non_integer_in_data_inicio(self):
        resp = requests.get('{}/venda/1'.format(TestRequestHandler.BASE_URL), params={
            'data_inicio': '2015-May'
        })

        self.assertEqual(resp.status_code, 400)
        self.assertIn('err', resp.json())
        self.assertEqual(resp.json()['err'], 'month must be a positive int.')

    

    def test_compare_without_ids(self):
        resp = requests.get('{}/comparar'.format(TestRequestHandler.BASE_URL))

        self.assertEqual(resp.status_code, 400)
        self.assertIn('err', resp.json())
        self.assertEqual(resp.json()['err'], 'Missing mandatory parameter "ids".')

    def test_compare_with_non_list_ids(self):
        resp = requests.get('{}/comparar'.format(TestRequestHandler.BASE_URL), params={
            'ids': '[1, 33, 643]'
        })

        self.assertEqual(resp.status_code, 400)
        self.assertIn('err', resp.json())
        self.assertEqual(resp.json()['err'], 'Parameter "ids" must be a list.')

    def test_compare_with_list_of_non_integer_ids(self):
        resp = requests.get('{}/comparar'.format(TestRequestHandler.BASE_URL), params={
            'ids': ['one', 33, 643]
        })

        self.assertEqual(resp.status_code, 400)
        self.assertIn('err', resp.json())
        self.assertEqual(resp.json()['err'], '"titulo_id" must be an int.')

    def test_compare_with_list_containing_not_found_ids(self):
        resp = requests.get('{}/comparar'.format(TestRequestHandler.BASE_URL), params={
            'ids': [6666, 6666666,666666666666]
        })

        self.assertEqual(resp.status_code, 404)
        self.assertIn('err', resp.json())
        self.assertEqual(resp.json()['err'], 'One of the ids was not found.')

        resp = requests.get('{}/comparar'.format(TestRequestHandler.BASE_URL), params={
            'ids': [1, 33, 999999]
        })

        self.assertEqual(resp.status_code, 404)
        self.assertIn('err', resp.json())
        self.assertEqual(resp.json()['err'], 'One of the ids was not found.')


class TestTituloTesouroRequestHandler(TestRequestHandler):

    def test_create_with_no_post_body(self):
        resp = requests.post(TestRequestHandler.BASE_URL)

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {
            'err': 'No request body.'
        })

    def test_create_with_incomplete_post_body(self):
        resp = requests.post(TestRequestHandler.BASE_URL,
            data=json.dumps({
            'categoria_titulo': 'NTN-B'
        }))

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {
            'err': "Mandatory fields ['mês', 'ano', 'ação', 'valor'] missing."
        })

    def test_create_with_non_string_categoria_titulo(self):
        resp = requests.post(TestRequestHandler.BASE_URL,
            data=json.dumps({
            'categoria_titulo': 1,
            'mês': 4,
            'ano': 2017,
            'ação': 'venda',
            'valor': 15000
        }))

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {
            'err': '"category" must be a string.'
        })

    def test_create_with_not_allowed_categoria_titulo(self):
        resp = requests.post(TestRequestHandler.BASE_URL,
            data=json.dumps({
            'categoria_titulo': 'something',
            'mês': 4,
            'ano': 2017,
            'ação': 'venda',
            'valor': 15000
        }))

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {
            'err': '"category" must be one of {}.'.format(TITULO_TESOURO_CATEGORIES)
        })

    def test_create_with_non_integer_mes(self):
        resp = requests.post(TestRequestHandler.BASE_URL,
            data=json.dumps({
            'categoria_titulo': 'NTN-B',
            'mês': 'January',
            'ano': 2017,
            'ação': 'venda',
            'valor': 15000
        }))

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {
            'err': '"month" must be an integer.'
        })

    def test_create_with_invalid_mes(self):
        resp = requests.post(TestRequestHandler.BASE_URL,
            data=json.dumps({
            'categoria_titulo': 'NTN-B',
            'mês': 0,
            'ano': 2017,
            'ação': 'venda',
            'valor': 15000
        }))

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {
            'err': '"month" must be in interval [1, 12].'
        })

    def test_create_with_non_integer_ano(self):
        resp = requests.post(TestRequestHandler.BASE_URL,
            data=json.dumps({
            'categoria_titulo': 'NTN-B',
            'mês': 1,
            'ano': '2017',
            'ação': 'venda',
            'valor': 15000
        }))

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {
            'err': '"year" must be an integer.'
        })

    def test_create_with_invalid_ano(self):
        resp = requests.post(TestRequestHandler.BASE_URL,
            data=json.dumps({
            'categoria_titulo': 'NTN-B',
            'mês': 1,
            'ano': 2000,
            'ação': 'venda',
            'valor': 15000
        }))

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {
            'err': '"year" must be greater than or equal to 2002.'
        })

    def test_create_with_non_string_acao(self):
        resp = requests.post(TestRequestHandler.BASE_URL,
            data=json.dumps({
            'categoria_titulo': 'NTN-B',
            'mês': 4,
            'ano': 2017,
            'ação': 1,
            'valor': 15000
        }))

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {
            'err': '"action" must be a string.'
        })

    def test_create_with_not_allowed_acao(self):
        resp = requests.post(TestRequestHandler.BASE_URL,
            data=json.dumps({
            'categoria_titulo': 'NTN-B',
            'mês': 4,
            'ano': 2017,
            'ação': 'aluguel',
            'valor': 15000
        }))

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {
            'err': '"action" must be one of {}.'.format(TITULO_TESOURO_ACTIONS)
        })

    def test_create_with_non_numeric_valor(self):
        resp = requests.post(TestRequestHandler.BASE_URL,
            data=json.dumps({
            'categoria_titulo': 'NTN-B',
            'mês': 4,
            'ano': 2017,
            'ação': 'venda',
            'valor': '15000'
        }))

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {
            'err': '"amount" must be a float or a int.'
        })

    def test_create_with_non_positive_valor(self):
        resp = requests.post(TestRequestHandler.BASE_URL,
            data=json.dumps({
            'categoria_titulo': 'NTN-B',
            'mês': 4,
            'ano': 2017,
            'ação': 'venda',
            'valor': 0
        }))

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {
            'err': '"amount" must be greater than zero.'
        })

    def test_create_with_valid_post_body(self):
        resp = requests.post(TestRequestHandler.BASE_URL,
            data=json.dumps({
            'categoria_titulo': 'NTN-B',
            'mês': 4,
            'ano': 2017,
            'ação': 'venda',
            'valor': 15000
        }))

        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json(), {
            'success': {
                'id': 1,
                'categoria_titulo': 'NTN-B',
                'mês': 4,
                'ano': 2017,
                'ação': 'VENDA',
                'valor': 15000.00
            }
        })

    def test_create_with_duplicated_post_body(self):
        resp = requests.post(TestRequestHandler.BASE_URL,
            data=json.dumps({
            'categoria_titulo': 'NTN-B',
            'mês': 5,
            'ano': 2017,
            'ação': 'venda',
            'valor': 25000
        }))

        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json(), {
            'success': {
                'id': 1,
                'categoria_titulo': 'NTN-B',
                'mês': 5,
                'ano': 2017,
                'ação': 'VENDA',
                'valor': 25000.00
            }
        })

        resp = requests.post(TestRequestHandler.BASE_URL,
            data=json.dumps({
            'categoria_titulo': 'NTN-B',
            'mês': 5,
            'ano': 2017,
            'ação': 'venda',
            'valor': 25000
        }))

        self.assertEqual(resp.status_code, 400)
        self.assertIn('err', resp.json())
        self.assertIn('duplicate key value violates unique constraint "tesouro_direto_series_category_action_expire_at_key"',
            resp.json()['err'])

    def test_delete_with_non_integer_id(self):
        resp = requests.delete('{}/three'.format(TestRequestHandler.BASE_URL))

        self.assertEqual(resp.status_code, 400)
        self.assertIn('err', resp.json())
        self.assertEqual('"titulo_id" must be an int.', resp.json()['err'])

    def test_delete_with_non_positive_id(self):
        resp = requests.delete('{}/0'.format(TestRequestHandler.BASE_URL))

        self.assertEqual(resp.status_code, 400)
        self.assertIn('err', resp.json())
        self.assertEqual('"titulo_id" must be greater than zero.', resp.json()['err'])

    def test_delete_with_non_existing_id(self):
        resp = requests.delete('{}/7'.format(TestRequestHandler.BASE_URL))

        self.assertEqual(resp.status_code, 404)
        self.assertIn('err', resp.json())
        self.assertEqual('"titulo_id" has no register.', resp.json()['err'])

    def test_delete_with_existing_id(self):
        resp = requests.post(TestRequestHandler.BASE_URL,
            data=json.dumps({
            'categoria_titulo': 'NTN-B',
            'mês': 5,
            'ano': 2017,
            'ação': 'venda',
            'valor': 666
        }))

        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json(), {
            'success': {
                'id': 1,
                'categoria_titulo': 'NTN-B',
                'mês': 5,
                'ano': 2017,
                'ação': 'VENDA',
                'valor': 666.00
            }
        })

        resp = requests.delete('{}/1'.format(TestRequestHandler.BASE_URL))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {
            'success': 'Deleted.'
        })

    def test_update_with_no_body(self):
        resp = requests.put('{}/1'.format(TestRequestHandler.BASE_URL))

        self.assertEqual(resp.status_code, 400)
        self.assertIn('err', resp.json())
        self.assertEqual(resp.json()['err'], 'No request body.')

    def test_update_with_empty_body(self):
        resp = requests.put('{}/1'.format(TestRequestHandler.BASE_URL),
            data=json.dumps({}))

        self.assertEqual(resp.status_code, 400)
        self.assertIn('err', resp.json())
        self.assertEqual(resp.json()['err'], 'Empty request body.')

    def test_update_with_non_integer_id(self):
        resp = requests.put('{}/three'.format(TestRequestHandler.BASE_URL),
            data=json.dumps({
            'categoria_titulo': 'NTN-B Principal'
        }))

        self.assertEqual(resp.status_code, 400)
        self.assertIn('err', resp.json())
        self.assertEqual('"titulo_id" must be an int.', resp.json()['err'])

    def test_update_with_non_positive_id(self):
        resp = requests.put('{}/0'.format(TestRequestHandler.BASE_URL),
            data=json.dumps({
            'categoria_titulo': 'NTN-B Principal'
        }))

        self.assertEqual(resp.status_code, 400)
        self.assertIn('err', resp.json())
        self.assertEqual('"titulo_id" must be greater than zero.', resp.json()['err'])

    def test_update_with_non_existing_id(self):
        resp = requests.put('{}/1'.format(TestRequestHandler.BASE_URL),
            data=json.dumps({
            'categoria_titulo': 'NTN-B Principal'
        }))

        self.assertEqual(resp.status_code, 404)
        self.assertIn('err', resp.json())
        self.assertEqual(resp.json()['err'], '"titulo_id" has no register.')

    def test_update_with_existing_id(self):
        resp = requests.post(TestRequestHandler.BASE_URL,
            data=json.dumps({
            'categoria_titulo': 'NTN-B',
            'mês': 5,
            'ano': 2017,
            'ação': 'venda',
            'valor': 666
        }))

        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json(), {
            'success': {
                'id': 1,
                'categoria_titulo': 'NTN-B',
                'mês': 5,
                'ano': 2017,
                'ação': 'VENDA',
                'valor': 666.00
            }
        })

        resp = requests.put('{}/1'.format(TestRequestHandler.BASE_URL),
            data=json.dumps({
            'ação': 'resgate'
        }))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {
            'success': {
                'id': 1,
                'ação': 'resgate'
            }
        })

    def test_update_categoria_titulo(self):
        resp = requests.post(TestRequestHandler.BASE_URL,
            data=json.dumps({
            'categoria_titulo': 'NTN-B',
            'mês': 5,
            'ano': 2017,
            'ação': 'venda',
            'valor': 666
        }))

        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json(), {
            'success': {
                'id': 1,
                'categoria_titulo': 'NTN-B',
                'mês': 5,
                'ano': 2017,
                'ação': 'VENDA',
                'valor': 666.00
            }
        })

        resp = requests.put('{}/1'.format(TestRequestHandler.BASE_URL),
            data=json.dumps({
            'categoria_titulo': 'NTN-B Principal'
        }))

        self.assertEqual(resp.status_code, 400)
        self.assertIn('err', resp.json())
        self.assertEqual(resp.json()['err'], 'Field "categoria_titulo" cannot be updated')


    def test_read_history_with_non_positive_integer_in_data_inicio(self):
        resp = requests.get('{}/1'.format(TestRequestHandler.BASE_URL), params={
            'data_inicio': '-2015-05'
        })

        self.assertEqual(resp.status_code, 400)
        self.assertIn('err', resp.json())
        self.assertEqual(resp.json()['err'], 'date not in format "YYYY-mm"')

    def test_read_history_with_non_integer_in_data_inicio(self):
        resp = requests.get('{}/1'.format(TestRequestHandler.BASE_URL), params={
            'data_inicio': '2015-May'
        })

        self.assertEqual(resp.status_code, 400)
        self.assertIn('err', resp.json())
        self.assertEqual(resp.json()['err'], 'month must be a positive int.')


if __name__ == '__main__':
    unittest.main()
