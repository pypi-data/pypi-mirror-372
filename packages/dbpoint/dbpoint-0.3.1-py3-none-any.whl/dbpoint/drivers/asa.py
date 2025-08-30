import sqlanydb # https://github.com/sqlanywhere/sqlanydb/blob/master/sqlanydb.py
#from dbpoint.profile_sql import ProfileSql

def connect(profile) -> sqlanydb.Connection | None:
    conn_dict = profile_to_dict(profile)
    conn = sqlanydb.connect(**conn_dict)
    return conn

def profile_to_dict(profile) -> dict:
    conn_args = {}
    conn_args['uid'] = profile["username"]
    conn_args['pwd'] = profile["password"]
    conn_args['eng'] = profile["engine"]
    conn_args['dbn'] = profile["database"]
    
    # ja eraldi võti ASA TCP ühenduste spetsiifika jaoks
    port = profile["port"] # 2638)
    host = profile["host"]
    conn_args['links'] = f"tcpip(host={host};port={port})"
    return conn_args

def driver_accepted_connection_parameter(param_key: str) -> bool:
    # ASA don't allow anything extra (actually: cs, but it is nowadays utf-8 always)
    allowed_extras = []
    return param_key in allowed_extras

def class_mapper() -> dict: 
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



def type_mapper(ref_code: list[int]) -> str:
    """
    Probleem: tüüpiks on DBAPISet (frozenset), kus on julmalt loetletud kõik enam-vähem sobivad
    seega on INT välja korral antud (doudle, float, tinyint, int, ) ja sama on ka numeric välja korral
    mis tähendab, et siinset into saab ainult üldistades kasutada (nt kas on vaja apostroofe või mitte)
    """
    asa_codes: dict = {
        384 : 'DATE', 
        388 : 'TIME', 
        392 : 'TIMESTAMP',
        396 : 'TIMESTAMP',
        448 : 'TEXT',
        452 : 'TEXT',
        456 : 'TEXT',
        460 : 'TEXT',
        480 : 'NUMBER',
        482 : 'NUMBER',
        484 : 'NUMBER',
        496 : 'NUMBER',
        500 : 'NUMBER',
        524 : 'BYTEA',
        528 : 'BYTEA',
        604 : 'NUMBER',
        608 : 'NUMBER',
        612 : 'NUMBER',
        616 : 'NUMBER',
        620 : 'NUMBER',
        624 : 'NUMBER',
        640 : 'TEXT',
    }
    class_name = asa_codes.get(ref_code[0] if isinstance(ref_code, list) else int(ref_code), "TEXT")
    return class_name

def escape(text: str) -> str:
    return str(text).replace("'", "\\'") # ' -> \'
