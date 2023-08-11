import os
from config import settings
from playhouse.db_url import connect, PooledMySQLDatabase
from peewee_async import Manager, MySQLDatabase

url = connect(settings.DATABASE_URL)
pool = PooledMySQLDatabase(
    url.database,
    max_connections=8,
    stale_timeout=300,
    timeout=200000,
    **url.connect_params
)
