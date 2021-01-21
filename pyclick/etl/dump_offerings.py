import os
import argparse
import pandas as pd
import logging

from avro.schema import parse
from avro.codecs import DeflateCodec
from avro.datafile import DataFileWriter
from avro.io import DatumWriter

import pyclick.util as util
import pyclick.config as config
import pyclick.assyst.config as click_config

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('dump_offerings')

SQL_OFFERINGS = util.get_query("ASSYST__OFERTAS")

class App(object):
    
    VERSION = (1, 0, 0)
    
    def __init__(self, schema_file, output):
        self.schema_file = schema_file
        self.output = output
    
    def parse_schema(self):
        logger.info('parsing avro schema')
        with open(self.schema_file, "rb") as fh:
            schema_txt = fh.read()
            return parse(schema_txt)
        
    def connect_db(self):
        logger.info('connecting to db')
        return click_config.SQLALCHEMY_ENGINE.connect()    
    
    def fetch_offerings(self, conn):
        logger.info('fetching offerings')
        df = pd.read_sql(SQL_OFFERINGS, conn, index_col=None)
        return df
    
    def save_offerings(self, schema, items_df):        
        fh = open(self.output, "wb")
        writer = DataFileWriter(fh, DatumWriter(), schema, 'deflate')
        for row in items_df.itertuples():
            assert row.STAT_FLAG in ('y', 'n')
            assert row.SOLIC_SERVICO in ('y', 'n')
            assert row.SERV_NEGOCIO in ('y', 'n')
            writer.append({
                "SERV_OFF_ID"		: row.SERV_OFF_ID       
            ,   "SERV_OFF_SC"		: row.SERV_OFF_SC        
            ,   "SERV_OFF_N"		: row.SERV_OFF_N         
            ,   "BUSINESS_REMARKS"	: row.BUSINESS_REMARKS   
            ,   "REMARKS"			: row.REMARKS            
            ,   "STAT_FLAG"			: row.STAT_FLAG          == 'y'
            ,   "SOLIC_SERVICO"		: row.SOLIC_SERVICO      == 'y'
            ,   "SERV_SC"			: row.SERV_SC            
            ,   "SERV_N"			: row.SERV_N             
            ,   "SERV_CSG"			: row.SERV_CSG           
            ,   "SERV_DEPT_SC"		: row.SERV_DEPT_SC       
            ,   "SERV_DEPT_N"		: row.SERV_DEPT_N        
            ,   "SERV_NEGOCIO"		: row.SERV_NEGOCIO       == 'y'
            ,   "FORMULARIO"		: row.FORMULARIO         
            ,   "PROCESSO"			: row.PROCESSO           
            ,   "PROCESSO_CSG"		: row.PROCESSO_CSG       
            ,   "PRODUCT_SC"		: row.PRODUCT_SC         
            ,   "PRODUCT_N"			: row.PRODUCT_N          
            ,   "ITEM_ID"			: row.ITEM_ID            
            ,   "ITEM_SC"			: row.ITEM_SC            
            ,   "ITEM_N"			: row.ITEM_N             
            ,   "CATEGORIA"			: row.CATEGORIA          
            ,   "IMPACTO_SC"		: row.IMPACTO_SC         
            ,   "IMPACTO_N"			: row.IMPACTO_N          
            ,   "IMPACTO_CSG"		: row.IMPACTO_CSG        
            ,   "URGENCIA_SC"		: row.URGENCIA_SC        
            ,   "URGENCIA_N"		: row.URGENCIA_N         
            ,   "URGENCIA_CSG"		: row.URGENCIA_CSG       
            ,   "SLA_SC"			: row.SLA_SC             
            ,   "SLA_N"				: row.SLA_N              
            ,   "PRAZO_M"			: row.PRAZO_M            
            })
        writer.close()
            
    def run(self):
        conn = None
        try:
            logger.info('starting offerings dumper - version %d.%d.%d', *self.VERSION)
            schema      = self.parse_schema()
            conn        = self.connect_db()
            items_df    = self.fetch_offerings(conn)
            self.save_offerings(schema, items_df)
            logger.info('finished')
        finally:
            if conn:
                conn = None
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('schema', type=str, help='schema file')
    parser.add_argument('output', type=str, help='output file')
    args = parser.parse_args()
    app = App(args.schema, args.output)
    app.run()
    