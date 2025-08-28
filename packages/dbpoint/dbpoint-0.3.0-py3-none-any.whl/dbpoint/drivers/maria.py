import mariadb
#from dbpoint.profile_sql import ProfileSql

def connect(profile) -> mariadb.Connection | None:
    conn_dict = profile_to_dict(profile)
    conn = mariadb.connect(**conn_dict)
    conn.autocommit = False
    return conn

def profile_to_dict(profile) -> dict:
    conn_args = {}
    conn_args['user'] = profile["username"]
    conn_args['password'] = profile["password"]
    conn_args['host'] = profile["host"]
    conn_args['port'] = profile["port"] # 3306
    conn_args['database'] = profile["database"]
    return conn_args

def driver_accepted_connection_parameter(param_key: str) -> bool:
    # nothing extra
    allowed_extras = []
    return param_key in allowed_extras

def class_mapper() -> dict: 
    # fixme
    return {
                'CHAR' : 'VARCHAR'
                , 'NCHAR' : 'VARCHAR'
                , 'NVARCHAR' : 'TEXT'
                , 'VARCHAR' : 'TEXT'
                , 'DATETIME' : 'TIMESTAMP'
                , 'TINYINT': 'SMALLINT'
                , 'BLOB' : 'BYTEA'
                , 'LONG VARCHAR' : 'TEXT'
                , 'LONG BINARY' : 'BYTEA'
            }

def escape(text: str) -> str:
    return text.replace("'", "''") # ' -> ''
    # if profile.get('version', 10) < 10: # vaikeversioonina eeldame uuemat, nt 8. aga kuni mysql ver 5-ni oli varjestaja kaldkriips (mitte ülakoma)
    #         self.apostrophe_escape = '\\'
