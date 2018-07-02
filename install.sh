#!/bin/bash

# Dependencias Python
sudo apt-get install -y libpq-dev postgresql-client postgresql-client-common gunicorn3
pip3 install --upgrade -r resources/requirements.txt

# base de dados
sudo apt-get install -y postgresql postgresql-contrib

# Criar a base de dados
sudo postgres -D /usr/local/pgsql/data >logs/pgsql-server 2>&1
sudo -u postgres createuser --superuser cvccorp
sudo -u postgres createdb -O cvccorp cvccorp
sudo -u postgres psql -c "alter user cvccorp with encrypted password '12345';"


