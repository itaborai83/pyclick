import sqlalchemy
import urllib.parse

PYODBC_DBSTRING = (
    r'Driver=SQL Server;'
    r'Server=NPAA7319\I2017SQL06P;'
    r'Database=DBASSY;'
    r'Trusted_Connection=yes;'
)
_QUOTED_PYODBC_DBSTRING  = urllib.parse.quote_plus(PYODBC_DBSTRING)
SQLALCHEMY_DBSTRING     = 'mssql+pyodbc:///?odbc_connect={}'.format(_QUOTED_PYODBC_DBSTRING)
SQLALCHEMY_ENGINE       = sqlalchemy.create_engine(SQLALCHEMY_DBSTRING)
