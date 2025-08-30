import pyodbc # https://github.com/mkleehammer/pyodbc/wiki/The-pyodbc-Module#connect
#from dbpoint.profile_sql import ProfileSql

def connect(profile) -> pyodbc.Connection | None:
    """
    ODBC connection has ONE string and some other parameters
    connect(*connstring, autocommit=False, timeout=0, readonly=False,
        attrs_before=None, encoding='utf-16le', ansi=False, **kwargs)
    
    So, we use two functions to put them separatelly together
    """
    
    conn_str = profile_to_string(profile) # https://www.connectionstrings.com/
    conn_dict = profile_to_dict(profile) 
    conn = pyodbc.connect(conn_str, **conn_dict)
    return conn

def profile_to_dict(profile) -> dict:
    # only additonal stuff
    conn_args = {}
    extras = profile.get("extras",{})
    for key, value in extras.items():
        if driver_accepted_connection_parameter(key):
            conn_args[key] = value
    return conn_args

def profile_to_string(profile) -> str:
    # main stuff (some good knowledge is https://github.com/mkleehammer/pyodbc/wiki about different vendors)
    conn_str = ''
    extras = profile.get("extras",{})
    odbc_driver_name = extras.get("driver")
    product = extras.get("dialect") or extras.get("product") or "general"
    if extras.get("trusted", False):
        creds = "Trusted_Connection=yes;Uid=auth_window"
    else:
        creds = f"UID={profile["username"]};PWD={profile["password"]}"

    """
    If extra.driver is installed odbc driver name then use it with host and database and port
    If not then use database name as DSN and ignore host & port
    """
    if odbc_driver_name: # triple "{" in next!!
        conn_str = f"Driver={{{odbc_driver_name}}};Host={profile["host"]};Database={profile["database"]};Port={profile["port"]};"
    else:
        conn_str = f"DSN={profile.database};"
    conn_str += creds

    if product == 'progress':
        # võimalus lülitada Progressi fataalsena mõjuv hoiatus välja (parem oleks algandmed korda teha)
        # SQL ja APL veeru definitsioonid pole süngis
        # conn_str = conn_str + ';truncateTooLarge=output'
        if extras.get("truncate_too_large"):
            conn_str += ';truncateTooLarge={extras.get("truncate_too_large")}'
    return conn_str


def driver_accepted_connection_parameter(param_key: str) -> bool:
    # keep in mind that default encoding is 'utf-16le'
    allowed_extras = ['autocommit', 'timeout', 'readonly', 'encoding', 'ansi', 'attrs_before']
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
