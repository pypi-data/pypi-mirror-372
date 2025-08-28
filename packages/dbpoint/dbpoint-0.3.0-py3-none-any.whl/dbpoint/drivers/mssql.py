import pymssql
#from dbpoint.profile_sql import ProfileSql

def connect(profile) -> pymssql.connection | None:
    conn_dict = profile_to_dict(profile)
    conn = pymssql.connect(**conn_dict)
    return conn

def profile_to_dict(profile) -> dict:
    conn_args = {}

    # Trusted_Connection=yes jaoks anname ilma kasutajanimeta-paroolita (ei toimi linuxis)
    # trusted connection tähendab, et baasi kasutajaks on windowsi kasutaja
    extras = profile.get("extras",{})
    if extras.get("trusted", False):
        ... # for trusted connection (windows username) don't specify username/password
    else:
        conn_args['user'] = profile["username"]
        conn_args['password'] = profile["password"]
    port = profile["port"] # 1433
    host = profile["host"]
    conn_args['host'] = f"{host}:{port}" # koos pordiga!
    conn_args['database'] = (profile["database"]).strip("/") # striping is redundant?
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
