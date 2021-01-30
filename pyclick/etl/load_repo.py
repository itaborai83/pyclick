import io
import json
import lmdb

from fastavro import writer, reader, parse_schema, schemaless_writer, schemaless_reader
from fastavro.schema import load_schema

import pyclick.etl.config as etl_config

def save_avro(schema_file, data_file, row_generator):
    schema = load_schema(schema_file)
    with open(data_file, 'wb') as fh:
        writer(fh, schema, row_generator, codec='deflate')
        
class LoadRepo:

    DB_MAP_SIZE = 10 * 1024 * 1024 * 1024
    DB_MAX_DBS = 100
    
    def __init__(self, dbpath):
        self.dbpath = dbpath
    
    def open_db(self, reader_check=True):
        env = lmdb.open(self.dbpath, max_dbs=self.DB_MAX_DBS, map_size=self.DB_MAP_SIZE)
        if reader_check:
            env.reader_check()
        return env
                
    def save_assyst_users(self, row_generator):
        self.save_rows(etl_config.ASSYST_USERS_SCHEMA, row_generator, int_key=True)

    def save_users(self, row_generator):
        self.save_rows(etl_config.USERS_SCHEMA, row_generator, int_key=True)                
        
    def save_items(self, row_generator):
        self.save_rows(etl_config.ITEMS_SCHEMA, row_generator, int_key=True)

    def save_schedules(self, row_generator):
        self.save_rows(etl_config.SCHEDULES_SCHEMA, row_generator, int_key=True)
    
    def save_offerings(self, row_generator):
        self.save_rows(etl_config.OFFERINGS_SCHEMA, row_generator, int_key=True)

    def save_suppliers(self, row_generator):
        self.save_rows(etl_config.SUPPLIERS_SCHEMA, row_generator, int_key=True)

    def get_assyst_users(self, assyst_user_ids):
        self.save_rows(etl_config.ASSYST_USERS_SCHEMA, row_generator, int_key=True)

    def get_user(self, user_id):
        self.save_rows(etl_config.USERS_SCHEMA, row_generator, int_key=True)                
        
    def get_item(self, item_id):
        self.save_rows(etl_config.ITEMS_SCHEMA, row_generator, int_key=True)

    def get_schedules(self, serv_dept_id):
        self.save_rows(etl_config.SCHEDULES_SCHEMA, row_generator, int_key=True)
    
    def get_offerings(self, serv_off_id):
        self.save_rows(etl_config.OFFERINGS_SCHEMA, row_generator, int_key=True)

    def get_suppliers(self, supplier_id):
        self.save_rows(etl_config.SUPPLIERS_SCHEMA, row_generator, int_key=True)
  
    def list_keys(self, db_name=None, int_key=False):
        env = self.open_db()
        with env.begin(write=False) as txn:
            if db_name:
                db = env.open_db(key=db_name.encode(), txn=txn, dupsort=False, create=False)
            else:
                db = env.open_db(key=None, txn=txn, dupsort=False, create=False)
            with txn.cursor(db=db) as cursor:
                if not cursor.first():
                    return
                while True:
                    key = cursor.key()
                    if not key:
                        return
                    if int_key:
                        parsed_key = self._decode_int(key)
                    else:
                        parsed_key = self._decode_string(key)
                    yield (parsed_key, key)
                    cursor.next()
        
    def save_rows(self, schema, row_generator, int_key=True, drop_first=True):
        buffer = io.BytesIO()
        env = self.open_db()
        db_name = schema[ 'name' ].encode()
        # drop db first
        if drop_first:
            with env.begin(write=True) as txn:
                db_data = env.open_db(key=db_name, txn=txn, dupsort=False, create=True)
                txn.drop(db_data, delete=False) # delete=False deletes all entries but keep the database itself
        
        with env.begin(write=True) as txn:            
            db_name = schema[ 'name' ].encode()
            db_data = env.open_db(key=db_name, txn=txn, dupsort=False, create=True)
            #txn.drop(db_data, delete=False) # delete=False deletes all entries but keep the database itself
            with txn.cursor(db=db_data) as data_cursor:
                for key, dict_data in row_generator:
                    schemaless_writer(buffer, schema, dict_data)
                    if int_key:
                        key  = self._encode_int(key)
                    else:
                        key  = self._encode_string(key)
                    buffer.seek(0)
                    data = buffer.read()
                    assert data_cursor.put(key, data)
                    buffer.seek(0)
                    buffer.truncate()

    def get_rows(self, schema, keys, int_key=True):
        buffer = io.BytesIO()
        result = {}
        env = self.open_db()
        db_name = schema[ 'name' ].encode()
        
        with env.begin(write=False) as txn:
            db_name = schema[ 'name' ].encode()
            db_data = env.open_db(key=db_name, txn=txn, dupsort=False, create=True)
            with txn.cursor(db=db_data) as data_cursor:
                for unencoded_key in keys:
                    if int_key:
                        key  = self._encode_int(key)
                    else:
                        key  = self._encode_string(key)
                    data = data_cursor.get(key)
                    if data:                        
                        buffer.seek(0)
                        buffer.truncate()
                        buffer.write(data)
                        buffer.seek(0)
                        data = schemaless_reader(buffer, schema)
                    else:
                        data = None
                    result[ unencoded_key ] = data
            return result
        
    ##############################################################################
    ##############################################################################
    ##
    ## Private API
    ##
    ##############################################################################
    ##############################################################################
    
    def _encode_string(self, value):
        return value.encode()
    
    def _decode_string(self, data):
        return data.decode()

    def _encode_int(self, value, signed=False):
        return value.to_bytes(8, "big", signed=signed)
    
    def _decode_int(self, data, signed=False):
        return int.from_bytes(data, "big", signed=signed)