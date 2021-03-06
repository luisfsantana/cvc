# -*- coding: utf-8 -*-
import logging
import openpyxl
import psycopg2

try:
    from basics import SCHEMAS_PATH, DATABASE_PARAMS, RESOURCES_PATH, TRANSACTIONS_PATH
except ImportError:
    from src.basics import SCHEMAS_PATH, DATABASE_PARAMS, RESOURCES_PATH, TRANSACTIONS_PATH


logging.basicConfig(format='[%(asctime)s] [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S %Z',
                    level=getattr(logging, 'INFO', 'DEBUG'))


def drop_database(filename='drop-all.sql', verbose=True):
    schemas_filepath = '{}/{}'.format(SCHEMAS_PATH, filename)
    with open(schemas_filepath) as f:
        sql = f.read()

    conn = psycopg2.connect(**DATABASE_PARAMS)
    cur = conn.cursor()

    if verbose:
        logging.info('Attempting to drop schemas.')
    cur.execute(sql)
    if verbose:
        logging.info('Schemas droppped.\n')

    cur.close()
    conn.close()


def create_database(filename='create-all.sql', verbose=True):
    schemas_filepath = '{}/{}'.format(SCHEMAS_PATH, filename)
    with open(schemas_filepath) as f:
        sql = f.read()

    conn = psycopg2.connect(**DATABASE_PARAMS)
    cur = conn.cursor()

    if verbose:
        logging.info('Attempting to create schemas.')
    cur.execute(sql)
    if verbose:
        logging.info('Schemas created.\n')

    cur.close()
    conn.close()


def get_action(raw):
    if raw == 'Vendas':
        return 'VENDA'
    if raw == 'Resgates':
        return 'RESGATE'
    return None

def get_multiplier(raw):
    if raw == 'R$ (milhões)':
        return 1000*1000
    return 1

def read_xlsx(filename, verbose=True):
    xlsx_filepath = '{}/{}'.format(RESOURCES_PATH, filename)
    if verbose:
        logging.info('Reading data from file "{}".'.format(xlsx_filepath))
    workbook = openpyxl.load_workbook(xlsx_filepath)
    worksheet = workbook['Planilha1']

    values = list()

    if verbose:
        logging.info('Reading values.')
    for j in range(ord('C'), ord('O')):
        column = chr(j)

        value_splitted = worksheet['{}7'.format(column)].value.split('- Tesouro Direto - ')
        category = value_splitted[1]
        action = get_action(value_splitted[0][15 : ].strip())

        value_splitted = worksheet['{}10'.format(column)].value.split('\xa0')
        multiplier = get_multiplier(value_splitted[1])

        for i in range(12, 136):
            date = worksheet['B{}'.format(i)].value
            amount = worksheet['{}{}'.format(column, i)].value
            amount = float(amount) * multiplier

            value = "('{}', '{}', '{}', {})".format(category, action, date, amount)
            values.append(value)

    if verbose:
        logging.info('All values read.\n')

    return values


def populate_database(values, verbose=True):
    with open('{}/load-input-data.sql'.format(TRANSACTIONS_PATH)) as f:
        sql = f.read()
    sql = sql.format(',\n    '.join(values))
    conn = psycopg2.connect(**DATABASE_PARAMS)
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()


if __name__ == '__main__':
    logging.info('Preparing to load system.\n')

    drop_database()
    create_database()
    values = read_xlsx('input-data.xlsx')
    populate_database(values)

    logging.info('System loaded.\n')
