from loguru import logger
import oracledb
import platform, os
#from dbpoint.profile_sql import ProfileSql

def connect(profile) -> oracledb.Connection | None:
    conn_dict = profile_to_dict(profile)
    logger.debug(f"Dealing with Oracle. For old Oracle (up to 11.2) is needed thick client and that is somehow platform dependent")
    op_system = platform.system()
    logger.debug(f"System is {op_system}") # Linux, Darwin, Windows
    logger.debug(f"Machine is {platform.machine()}") # x86_64, ...

    # Oracle 11.2 vs newer
    extras = profile.get("extras",{})
    if extras.get('mode', 'thin') == 'thick': # FAT CLIENT INITIALIZATION NEEDED
        logger.debug(f"Going to thick/fat client")
        oracle_instantclient_subdir = 'instantclient_11_2' # näib, et see võib olla ka suvaline uuem?!
        # On Linux and related platforms, enable Thick mode by calling init_oracle_client() without passing a lib_dir parameter.
        # oracledb.init_oracle_client() # samaväärne lib_dir=None, järgmine kood tegeleb (tervikluse mõttes) kõigega (aga testimata)
        
        oracle_instantclient_dir = None  # default suitable for Linux
        # macOS: /<home>/Downloads/instantclient_11_2
        # windows: c:\oracle\instantclient_11_2
        if op_system == "Darwin" and platform.machine() == "x86_64": 
            oracle_instantclient_dir = "/".join([str(os.environ.get('HOME')), 'Downloads', oracle_instantclient_subdir])
        elif op_system == "Windows": 
            oracle_instantclient_dir = "C:\\" + "\\".join(['oracle', oracle_instantclient_subdir])
        logger.debug(f"Assuming subdir {oracle_instantclient_subdir} ()")
        if op_system != 'Linux' or not os.path.exists(oracle_instantclient_subdir):
            logger.error(f"folder {oracle_instantclient_dir} don't exists (Windows/MacOS)")
            raise Exception(f"Paksu Oracle jaoks pole InstantClient asukohas {oracle_instantclient_dir}, midagi on vaja muuta")
        
        oracledb.init_oracle_client(lib_dir=oracle_instantclient_dir) # Init for Oracle thick client

    conn = oracledb.connect(**conn_dict)
    return conn

def profile_to_dict(profile) -> dict:
    conn_args = {}
    conn_args['user'] = profile["username"]
    conn_args['password'] = profile["password"]
    conn_args['eng'] = profile["engine"]
    conn_args['service_name'] = profile["database"] # default 'xe' ?
    conn_args['port'] = profile["port"] # 1521
    conn_args['host'] = profile["host"]
    conn_args['tcp_connect_timeout'] = 8 # default is 20 sek (huge time to wait on simple errors) but one can restore it using extras

    extras = profile.get("extras",{})
    for key, value in extras.items():
        if driver_accepted_connection_parameter(key):
            conn_args[key] = value
    return conn_args

def driver_accepted_connection_parameter(param_key: str) -> bool:
    allowed_extras = [
        'tcp_connect_timeout', 'expire_time', 'retry_count'
    ]
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
    return text.replace("'", "\\'") # ' -> \' ?????

'''
https://python-oracledb.readthedocs.io/en/latest/api_manual/module.html

oracledb.connect(dsn=None, pool=None, conn_class=None, params=None, user=None, proxy_user=None, password=None, newpassword=None, wallet_password=None
, access_token=None, host=None, port=1521, protocol='tcp', https_proxy=None, https_proxy_port=0
, service_name=None, sid=None, server_type=None, cclass=None, purity=oracledb.PURITY_DEFAULT, expire_time=0, retry_count=0, retry_delay=1
, tcp_connect_timeout=20.0, ssl_server_dn_match=True, ssl_server_cert_dn=None, wallet_location=None, events=False, externalauth=False
, mode=oracledb.AUTH_MODE_DEFAULT, disable_oob=False, stmtcachesize=oracledb.defaults.stmtcachesize, edition=None, tag=None, matchanytag=False
, config_dir=oracledb.defaults.config_dir, appcontext=[], shardingkey=[], supershardingkey=[], debug_jdwp=None, connection_id_prefix=None
, ssl_context=None, sdu=8192, pool_boundary=None, use_tcp_fast_open=False, ssl_version=None, handle=0)

'''
