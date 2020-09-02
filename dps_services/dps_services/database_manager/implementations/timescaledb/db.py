from config import CONNECTION
import psycopg2 as pg

dataset_cache = []
signal_cache = []

class TimeCache:
    def __init__(self, duration):
        self.value = value
        self.duration = duration
        self.cache_time

    def get_or_cache(self, cache):
        
        
def connect():
    return pg.connect(CONNECTION)

def select_all(cur, table):
    query = pg.sql.SQL('SELECT * FROM {table};').format(table=pg.sql.Identifier(table))
    cur.execute(query)
    results = cur.fetchall()
    return [] if results is None else results

def select_where(cur, table, key, value):
    query = pg.sql.SQL('SELECT * FROM {table} where {key} = {value};').format(
        table=pg.sql.Identifier(table),
        key=key,
        value=value,
    )
    cur.execute(query)
    return cur.fetchall()

def exists(cur, table, id_name, key, value):
    query = pg.sql.SQL('SELECT {id_name} FROM {table} where {key} = {value};').format(
        id_name=pg.sql.Identifier(id_name),
        table=pg.sql.Identifier(table),
        key=pg.sql.Identifier(key),
        value=value,
    )
    cur.execute(query)
    return bool(cur.fetchone())

def insert_data(cur, table, name, check_exists=True):
    if not check_exists or not dataset_exists(cur, name):
        query = pg.sql.SQL('INSERT INTO {table} ({name}) VALUES ({name});').format(
            table=pg.sql.Identifier(table),
            name=name,
        )
        cur.execute(query)
