import io
import json
import lmdb
from fastavro import writer, reader, parse_schema, schemaless_writer
from fastavro.schema import load_schema


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

    def parse_schema(self, schema_file):
        return parse_schema(schema_file)
                
    """
    def save_assyst_users(self, schema_file, assyst_users_gen):
        buffer = io.BytesIO()
        schema = load_schema(schema_file)
        env = self.open_db()
        with env.begin(write=True) as txn:
            db_schema = env.open_db(key=b'SCHEMAS', txn=txn, dupsort=False, create=True)
            self._save_schema(txn, db_schema, schema)
            schema_cursor.close()
            
            db_data = env.open_db(key=b'ASSYST_USERS', txn=txn, dupsort=False, create=True, integerkey=True)
            txn.drop(db_data, delete=False) # delete=False deletes all entries but keep the database itself            
            data_cursor = txn.cursor(db=db_data)
            
            for key, dict_data in assyst_users_gen:
                schemaless_writer(buffer, schema, dict_data)
                key  = self._encode_int(key)
                data = buffer.read()
                txn.put(key, data)
                buffer.seek(0)
                buffer.truncate()

    
    def save_items(self, schema_file, items_gen):
        buffer = io.BytesIO()
        schema = load_schema(schema_file)
        env = self.open_db()
        with env.begin(write=True) as txn:
            db_schema = env.open_db(key=b'SCHEMAS', txn=txn, dupsort=False, create=True)
            schema_cursor = txn.cursor(db=db_schema)
            self._save_schema(schema_cursor, 'ITEMS', schema)
            schema_cursor.close()
            
            db_data = env.open_db(key=b'ASSYST_USERS', txn=txn, dupsort=False, create=True, integerkey=True)
            txn.drop(db_data, delete=False) # delete=False deletes all entries but keep the database itself            
            data_cursor = txn.cursor(db=db_data)
            
            for key, dict_data in assyst_users_gen:
                schemaless_writer(buffer, schema, dict_data)
                key  = self._encode_int(key)
                data = buffer.read()
                txn.put(key, data)
                buffer.seek(0)
                buffer.truncate()
    """
    def save_assyst_users(self, schema_file, row_generator):
        self.save_rows(schema_file, row_generator, int_key=True)

    def save_users(self, schema_file, row_generator):
        self.save_rows(schema_file, row_generator, int_key=True)                
        
    def save_items(self, schema_file, row_generator):
        self.save_rows(schema_file, row_generator, int_key=True)

    def save_schedules(self, schema_file, row_generator):
        self.save_rows(schema_file, row_generator, int_key=True)
    
    def save_offerings(self, schema_file, row_generator):
        self.save_rows(schema_file, row_generator, int_key=True)

    def save_suppliers(self, schema_file, row_generator):
        self.save_rows(schema_file, row_generator, int_key=True)
        
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
        
    def save_rows(self, schema_file, row_generator, int_key=True, drop_first=True):
        buffer = io.BytesIO()
        schema = load_schema(schema_file)
        env = self.open_db()
        db_name = schema[ 'name' ].encode()
        # drop db first
        if drop_first:
            with env.begin(write=True) as txn:
                db_data = env.open_db(key=db_name, txn=txn, dupsort=False, create=True)
                txn.drop(db_data, delete=False) # delete=False deletes all entries but keep the database itself
        
        with env.begin(write=True) as txn:
            db_schema = env.open_db(key=b'SCHEMAS', txn=txn, dupsort=False, create=True)
            self._save_schema(txn, db_schema, schema)
            
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
    
    def _save_schema(self, txn, db_schema, schema):
        with txn.cursor(db=db_schema) as schema_cursor:
            schema_name = schema[ 'name' ]
            key = self._encode_string(schema_name)
            schema_json = json.dumps(schema)
            schema_data = self._encode_string(schema_json)
            schema_cursor.put(key, schema_data)