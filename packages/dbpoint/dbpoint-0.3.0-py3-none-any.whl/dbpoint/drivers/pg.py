from typing import Any
import psycopg2

def connect(profile) -> Any:
    bad_keys = [199, 114, 3802, 3807, 16, 1114, 1184, 1083, 1266, 1082, 704, 1186]
    for bad_key in bad_keys:
        if bad_key in psycopg2.extensions.string_types: # teisel sama draiveriga ühendusel
            del psycopg2.extensions.string_types[bad_key]
    conn_url = profile_to_url(profile)
    conn: psycopg2.extensions.connection = psycopg2.connect(conn_url) # on error return -1?
    return conn

def profile_to_url(profile) -> str:
    params = [] # elenents in connection URL after ?-char
    extras = profile.get("extras",{})
    for key, value in extras.items():
        if driver_accepted_connection_parameter(key):
            params.append(f"{key}={value}")
    
    parts = [] # maksimaalselt 2 osa
    parts.append(f"postgresql://{profile["username"]}:{profile["password"]}@{profile["host"]}:{profile["port"]}/{profile["database"]}")
    if(params):
        parts.append('&'.join(params))
    connection_url = '?'.join(parts)
    if "debug" in profile and profile["debug"]:
        print(connection_url) # dont do that!
    return connection_url

def driver_accepted_connection_parameter(param_key: str) -> bool:
    # postgres allows next dynamic params in connect string/url
    allowed_extras = [
        'connect_timeout'
        , 'keepalives_idle'
        , 'application_name'
    ]
    return param_key in allowed_extras

def class_mapper() -> dict:
    # see siin on tegelt ASA -> PG mäpper
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
    return str(text).replace("'", "''") # ' -> ''
