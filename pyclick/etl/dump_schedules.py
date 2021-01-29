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
import pyclick.etl.config as etl_config

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('dump_schedules')

SQL_SCHEDULES = util.get_query("ASSYST__MESA_SCHEDULES")

class App(object):
    
    VERSION = (1, 0, 0)
    
    def __init__(self, output):
        self.schema_file = etl_config.SCHEDULES_SCHEMA_FILE
        self.output = output
    
    def parse_schema(self):
        logger.info('parsing avro schema')
        with open(self.schema_file, "rb") as fh:
            schema_txt = fh.read()
            return parse(schema_txt)
        
    def connect_db(self):
        logger.info('connecting to db')
        return click_config.SQLALCHEMY_ENGINE.connect()    
    
    def fetch_schedules(self, conn):
        logger.info('fetching schedules')
        df = pd.read_sql(SQL_SCHEDULES, conn, index_col=None)
        return df
    """
    def save_schedules(self, schema, schedules_df):
        fh = open(self.output, "wb")
        writer = DataFileWriter(fh, DatumWriter(), schema, 'deflate')
        for row in schedules_df.itertuples():
            writer.append({
                "MESA_ID"			: row.MESA_ID
            ,    "MESA_SC"			: row.MESA_SC
            ,    "MESA_N"			: row.MESA_N
            ,    "FORNECEDOR_ID"	: row.FORNECEDOR_ID
            ,    "FORNECEDOR_SC"	: row.FORNECEDOR_SC
            ,    "FORNECEDOR_N"		: row.FORNECEDOR_N
            ,    "SLA_ID"			: row.SLA_ID
            ,    "SLA_SC"			: row.SLA_SC
            ,    "SLA_N"			: row.SLA_N
            ,    "MON_BEGIN"		: row.MON_BEGIN		
            ,    "MON_END"			: row.MON_END
            ,    "TUE_BEGIN"		: row.TUE_BEGIN		
            ,    "TUE_END"			: row.TUE_END
            ,    "WED_BEGIN"		: row.WED_BEGIN		
            ,    "WED_END"			: row.WED_END
            ,    "THR_BEGIN"		: row.THR_BEGIN		
            ,    "THR_END"			: row.THR_END
            ,    "FRI_BEGIN"		: row.FRI_BEGIN		
            ,    "FRI_END"			: row.FRI_END	
            ,    "SAT_BEGIN"		: row.SAT_BEGIN		
            ,    "SAT_END"			: row.SAT_END	
            ,    "SUN_BEGIN"		: row.SUN_BEGIN		
            ,    "SUN_END"			: row.SUN_END		
            ,    "FERIADO_01"		: row.FERIADO_01	
            ,    "FERIADO_02"		: row.FERIADO_02	
            ,    "FERIADO_03"		: row.FERIADO_03	
            ,    "FERIADO_04"		: row.FERIADO_04	
            ,    "FERIADO_05"		: row.FERIADO_05	
            ,    "FERIADO_06"		: row.FERIADO_06	
            ,    "FERIADO_07"		: row.FERIADO_07	
            ,    "FERIADO_08"		: row.FERIADO_08	
            ,    "FERIADO_09"		: row.FERIADO_09	
            ,    "FERIADO_10"		: row.FERIADO_10	
            ,    "FERIADO_11"		: row.FERIADO_11	
            ,    "FERIADO_12"		: row.FERIADO_12	
            ,    "FERIADO_13"		: row.FERIADO_13	
            ,    "FERIADO_14"		: row.FERIADO_14	
            ,    "FERIADO_15"		: row.FERIADO_15	
            ,    "FERIADO_16"		: row.FERIADO_16	
            ,    "FERIADO_17"		: row.FERIADO_17	
            ,    "FERIADO_18"		: row.FERIADO_18	
            ,    "FERIADO_19"		: row.FERIADO_19	
            ,    "FERIADO_20"		: row.FERIADO_20	
            })
        writer.close()
    """
    
    def save_schedules(self, schedules_df):
        def generator(df):
            for row in df.itertuples():
                yield (
                    row.MESA_ID, 
                    {
                        "MESA_ID"			: row.MESA_ID
                    ,   "MESA_SC"			: row.MESA_SC
                    ,   "MESA_N"			: row.MESA_N
                    ,   "FORNECEDOR_ID"	    : row.FORNECEDOR_ID
                    ,   "FORNECEDOR_SC"	    : row.FORNECEDOR_SC
                    ,   "FORNECEDOR_N"		: row.FORNECEDOR_N
                    ,   "SLA_ID"			: row.SLA_ID
                    ,   "SLA_SC"			: row.SLA_SC
                    ,   "SLA_N"			    : row.SLA_N
                    ,   "MON_BEGIN"		    : row.MON_BEGIN		
                    ,   "MON_END"			: row.MON_END
                    ,   "TUE_BEGIN"		    : row.TUE_BEGIN		
                    ,   "TUE_END"			: row.TUE_END
                    ,   "WED_BEGIN"		    : row.WED_BEGIN		
                    ,   "WED_END"			: row.WED_END
                    ,   "THR_BEGIN"		    : row.THR_BEGIN		
                    ,   "THR_END"			: row.THR_END
                    ,   "FRI_BEGIN"		    : row.FRI_BEGIN		
                    ,   "FRI_END"			: row.FRI_END	
                    ,   "SAT_BEGIN"		    : row.SAT_BEGIN		
                    ,   "SAT_END"			: row.SAT_END	
                    ,   "SUN_BEGIN"		    : row.SUN_BEGIN		
                    ,   "SUN_END"			: row.SUN_END		
                    ,   "FERIADO_01"		: row.FERIADO_01	
                    ,   "FERIADO_02"		: row.FERIADO_02	
                    ,   "FERIADO_03"		: row.FERIADO_03	
                    ,   "FERIADO_04"		: row.FERIADO_04	
                    ,   "FERIADO_05"		: row.FERIADO_05	
                    ,   "FERIADO_06"		: row.FERIADO_06	
                    ,   "FERIADO_07"		: row.FERIADO_07	
                    ,   "FERIADO_08"		: row.FERIADO_08	
                    ,   "FERIADO_09"		: row.FERIADO_09	
                    ,   "FERIADO_10"		: row.FERIADO_10	
                    ,   "FERIADO_11"		: row.FERIADO_11	
                    ,   "FERIADO_12"		: row.FERIADO_12	
                    ,   "FERIADO_13"		: row.FERIADO_13	
                    ,   "FERIADO_14"		: row.FERIADO_14	
                    ,   "FERIADO_15"		: row.FERIADO_15	
                    ,   "FERIADO_16"		: row.FERIADO_16	
                    ,   "FERIADO_17"		: row.FERIADO_17	
                    ,   "FERIADO_18"		: row.FERIADO_18	
                    ,   "FERIADO_19"		: row.FERIADO_19	
                    ,   "FERIADO_20"		: row.FERIADO_20	
                    }
                )
        import pyclick.etl.load_repo as r
        repo = r.LoadRepo(self.output)
        repo.save_schedules(self.schema_file, generator(schedules_df))
        
    def run(self):
        conn = None
        try:
            logger.info('starting schedules dumper - version %d.%d.%d', *self.VERSION)
            conn = self.connect_db()
            schedules_df = self.fetch_schedules(conn)
            self.save_schedules(schedules_df)
            logger.info('finished')
        finally:
            if conn:
                conn = None
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('output', type=str, help='output file')
    args = parser.parse_args()
    app = App(args.output)
    app.run()
    