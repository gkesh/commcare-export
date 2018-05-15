# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import, division, generators, nested_scopes

import logging
import uuid

import pytest
import sqlalchemy
from sqlalchemy.exc import DBAPIError

TEST_DB = 'test_commcare_export_%s' % uuid.uuid4().hex

logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler())


@pytest.fixture(scope="class", params=[
    {
        'url': "postgresql://postgres@localhost/%s",
        'admin_db': 'postgres'
    },
    {
        'url': 'mysql+pymysql://travis@/%s?charset=utf8',
    },
    {
        'url': 'mssql+pyodbc://SA:Password@123@localhost/%s?driver=ODBC+Driver+17+for+SQL+Server',
        'admin_db': 'master'
    }
], ids=['postgres', 'mysql', 'mssql'])
def db_params(request):
    db_url = request.param['url']
    sudo_engine = sqlalchemy.create_engine(db_url % request.param.get('admin_db', ''), poolclass=sqlalchemy.pool.NullPool)
    db_connection_url = db_url % TEST_DB

    def tear_down():
        with sudo_engine.connect() as conn:
            conn.execute('rollback')
            if 'mssql' in db_url:
                conn.connection.connection.autocommit = True
            conn.execute('drop database if exists %s' % TEST_DB)

    try:
        with sqlalchemy.create_engine(db_connection_url).connect():
            pass
    except (sqlalchemy.exc.OperationalError, sqlalchemy.exc.InternalError, DBAPIError):
        with sudo_engine.connect() as conn:
            conn.execute('rollback')
            if 'mssql' in db_url:
                conn.connection.connection.autocommit = True
            conn.execute('create database %s' % TEST_DB)
    else:
        raise Exception('Database %s already exists; refusing to overwrite' % TEST_DB)

    request.addfinalizer(tear_down)

    params = request.param.copy()
    params['url'] = db_connection_url
    return params