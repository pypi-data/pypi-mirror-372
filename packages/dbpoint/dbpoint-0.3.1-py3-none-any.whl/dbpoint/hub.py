from loguru import logger
from typing import Callable, Any
from types import ModuleType
from datetime import datetime

from .moduleops import prepare_module_fn
from .fileops import read_content_of_package_file
from .textops import yaml_string_to_dict
from .datacolumn import DataColumn
from .textops import substitute_env
from .datacapsule import DataCapsule

INTERNAL_DRIVERS_SUBPACKAGE = "dbpoint.drivers"
INTERNAL_DRIVERS_DIRECTORY_FILE = "drivers.yaml"

class Hub():
    """
    Single access point for all database action. 
    New way is to init with two strings (yaml strings): list of profiles, and name-to-module mapping dict
    """
    def __init__(self, profiles: str = "{}", known_drivers: str = "{}"):
        """
        Init by YAML string that conforms to ProfileSQL structure
        """
        self.module_cache: dict[str, ModuleType] = {} # private, use fn 
        self.profiles: dict[str, dict] = {}
        self.known_drivers: dict[str, dict] = {}

        self.init_sql_drivers_for_app(known_drivers) # may raise Exception (fail fast)
        self.init_sql_profiles_for_app(profiles) # may raise Exception (fail fast)

    def cache_get(self, module_short_name: str) -> ModuleType | None:
        return self.module_cache.get(module_short_name, None)
    
    def cache_set(self, module_short_name: str, the_module: ModuleType) -> None:
        self.module_cache[module_short_name] = the_module

    def cacher(self, module_short_name: str, the_module: ModuleType | None) -> ModuleType | None:
        """
        One fn to manipulate both cache ops, based of existence of value/module
        """
        if the_module: # if module is given then caller wants to set it
            self.cache_set(module_short_name, the_module)
            return the_module
        else:
            return self.cache_get(module_short_name)
    
    def mapper_for_driver_module(self, module_short_name: str) -> dict | None:
        """
        Knowledge how to find python package and module for some short alias
        Knowledge bases on self.know_driver dict
        Returns dict: "package" and "module" (and maybe "relative" = main package -- ??)
        """
        if not module_short_name:
            return None
        library_info: dict | None = self.known_drivers.get(module_short_name, None)
        if not library_info:
            logger.error(f"Module info for {module_short_name} not found")
        #else:
        #    logger.debug(f"Module for {module_short_name} is {library_info}") # package and module
        return library_info # currently our input (known drivers) are same dict structure that is needed

    def init_sql_drivers_for_app(self, known_drivers: str):
        """
        Input is YAML formated text with names to point to package and module where allowed DataDrivers reside
        If app needs just one connection then don't give more/unneeded drivers.

        NB! dict type support is deprecated
        """
        if isinstance(known_drivers, str):
            logger.debug("reading list of drivers from string")
            self.known_drivers = yaml_string_to_dict(known_drivers) or {}
        else:
            logger.debug("reading list of drivers from dictionary")
            self.known_drivers = known_drivers
        if not self.known_drivers: # on empty string lets read all internally known
            logger.debug("reading list of drivers from module")
            self.known_drivers = yaml_string_to_dict(read_content_of_package_file(INTERNAL_DRIVERS_SUBPACKAGE, INTERNAL_DRIVERS_DIRECTORY_FILE)) or {}
        if not self.known_drivers: # still not
            logger.error("No database drivers known!")
            raise Exception("No database drivers known")
    
    def init_sql_profiles_for_app(self, profiles: str):
        """
        Giving app database connection configuration profiles.
        """
        try:
            self.profiles = yaml_string_to_dict(profiles) or {}
            for profile_name, profile_data in self.profiles.items():
                self.profiles[profile_name]["password"] = substitute_env(profile_data.get("password", "")) or ""
        except Exception as e1:
            logger.error(f"Unable to parse config data from yaml-string, string is not correct YAML, {e1}")
            raise e1 # FATAL
        if not self.profiles:
            logger.error("No database profiles!")
            raise Exception("No database profiles")

    def is_profile_exists(self, profile_name) -> bool:
        if not profile_name:
            return False
        profile: dict = self.get_profile(profile_name)
        if not profile:
            return False
        return True

    def get_profile(self, profile_name) -> dict:
        if not self.profiles:
            return {}
        return self.profiles.get(profile_name, {})

    def create_driver(self, driver_alias: str) -> ModuleType | None:
        """
        Result is driver object (corresponding to corrent DBMS) without actual connection
        Called only by get_driver()
        """
        logger.debug(f"Loading module for driver {driver_alias}")
        the_module: ModuleType | None = prepare_module_fn(driver_alias, self.cacher, self.mapper_for_driver_module)
        if the_module is None:
            logger.error(f"Preparation result is None")
            return None
        try:
            driver_module = the_module #.DataDriver() # class with such fixed name
            return driver_module
        except Exception as e1:
            logger.error(f"Problem with driver, {e1}")
            return None

    def get_driver(self, profile_name: str | None) -> ModuleType | None:
        """
        Returns object capable to make actions (don't need to be connected)
        """
        if profile_name is None:
            logger.error("Missing profile name for driver")
            return None
        profile: dict = self.get_profile(profile_name)
        if not profile:
            return None
        if profile.get("driver_module") is None: # if driver object/module not found yet
            driver_name = profile.get("driver", "")
            new_driver_module = self.create_driver(driver_name)
            if not new_driver_module:
                logger.error(f"Couldn't init driver '{driver_name}'")
                return None
            if not hasattr(new_driver_module, "connect"): # or not hasattr(new_driver_module, "class_mapper"):
                logger.error(f"Wrong spec driver '{driver_name}'")
                return None
            profile["driver_module"] = new_driver_module
        return profile["driver_module"]

    def prepare_flags(self, flags: dict | None = None):
        # style: text, number, both # FIXME teha Enum
        defaults = { 
            'on_success_commit' : True
            , 'new_transaction': False
            , 'on_error_rollback' : True
            , 'on_error_disconnect' : False
            , 'verbose' : False
            , 'style' : 'number' # both on liiga ohtlik, kuna meil metasüsteem ja mitmes kohas on iteratsioon üle veergude
            }
        flags = flags or {}
        control = {**defaults, **flags}
        if control['style'] == 'text':
            control['style'] = 'name'
        if control['style'] not in ('name', 'number', 'both', 'dataset'):
            control['style'] = 'number'
        return control

    def find_connection(self, profile_name: str, reconnect: bool = False) -> Any | None:
        """
        return type Any (or just object) is actually DBAPIConnection
        but postgres (psycopg) and lot of others have their own type defined
        """
        #logger.info(f"find connection {profile_name} with {reconnect}")
        profile = self.get_profile(profile_name)
        if profile is None:
            return None
        driver_module: ModuleType | None = self.get_driver(profile_name)
        if driver_module is None:
            logger.error(f"No real driver for profile '{profile_name}'")
            return None
        if not profile.get("connection_object") or reconnect:
            profile["connection_object"] = driver_module.connect(profile)
        return profile["connection_object"] # shortcut
    
    def get_executed_cursor(self, profile_name: str, sql: str | DataCapsule, control: dict | None = None, counter: int = 1) -> None | Any: # Any = cursor from any DBMS package (which may by dynamic)
        """
        Internal function!
        Return new Executed Cursor (or None), so connection issues are mostly solved.
        "Empty command error" should be checked ealier
        """
        if counter < 0: # avoid infinite recursion
            logger.error(f"Loop limit full")
            return None
        if isinstance(sql, str):
            capsule = DataCapsule(sql)
        else:
            capsule = sql
        capsule.set_flags(control or {})

        connection = self.find_connection(profile_name)
        if connection is None:
            logger.error(f"Couldn't find connection {profile_name}")
            return None
        try:
            if capsule.get_flag("verbose"):
                flags: dict = capsule.get_flags()
                for flag_key, flag_value in flags.items():
                    logger.debug(f"Flag {flag_key} = {flag_value}")
            cursor = connection.cursor() # normal guess that connection object will give error if connection is lost, but no...
            if capsule.get_flag("new_transaction"):
            #if control['new_transaction']:
                self.try_and_log(connection.commit, logger.warning, "Failed to start transaction before command, ignoring")
            cursor.execute(capsule.sql_command) # ... error about lost connection becomes visible only after execution of cursor
            # logger.debug(f"cursor executed succesfully, {cursor}")
        except Exception as e1:
            #  (b'Connection was terminated', -308),  (b'Not connected to a database', -101)
            logger.error(e1) # MariaDB annab siia str(e1) lihtsalt stringi "Server has gone away"
            logger.error(e1.args) # Kuidagi peaks kinni püüdma vea staatuskoodi. ASA annab -101 või -308, MariaDB annab tuple, kus esimene/ainuke element on string
            # PG annab string 'connection already closed'
            #if (len(e1.args) > 1 and isinstance(e1.args[1], int) and e1.args[1] in (-101, -308)) or str(e1) == "Server has gone away" or str(e1) == "connection already closed":
            if self.is_connection_error(e1):
                logger.error("Caught connection error")
                connection = self.find_connection(profile_name, reconnect=True)
                if connection is None:
                    logger.error(f"Unable to reconnect {profile_name}")
                    return None
                logger.info(f"Reconnected!")
                try:
                    # new assigments for error case
                    capsule.set_flag("on_error_rollback", False)
                    capsule.set_flag("on_error_disconnect", False)
                    #control['on_error_rollback'] = False
                    #control['on_error_disconnect'] = False
                    cursor = self.get_executed_cursor(profile_name, capsule, None, counter - 1)
                except Exception as e2:
                    logger.error(e2)
                    cursor = None
            else: # all other errors (SQL syntax, priviledges etc)
                logger.error("Other error")
                #if control['on_error_rollback']:
                if capsule.get_flag("on_error_rollback"):
                    self.try_and_log(connection.rollback, logger.warning, "Failed to roll back after error, ignoring")
                #if control['on_error_disconnect']:
                if capsule.get_flag("on_error_disconnect"):
                    self.try_and_log(connection.disconnect, logger.warning, "Failed to disconnect after error, ignoring")
                logger.error(f"Database command error, {e1}")
                return None #raise e1
        # if cursor was meant for only execution of command without result set, we can commit (if wanted) and close, but let these things are inside run()
        return cursor
    
    def is_connection_error(self, e1: Exception) -> bool:
        logger.debug("analyzing error")
        logger.debug(e1)
        text = str(e1)
        if text in ("Server has gone away", "connection already closed"):
            logger.debug("text-based comparision gave us connection problem")
            return True
        if "conn" in text.lower():
            logger.debug("text-based lower inclusion gave us connection problem")
            return True
        if len(e1.args) > 1:
            if isinstance(e1.args[1], int):
                if e1.args[1] in (-101, -308):
                    logger.debug("ASA error codes -101 or -308")
                    return True
            if isinstance(e1.args, str): 
                if "closed" in e1.args[1]:
                    logger.debug("text-based search closed gave us connection problem")
                    return True
        return False


    def fn_stream(self, profile_name: str):
        def dummy(sql):
            return None
        def streamer(sql: str | DataCapsule):
            logger.info(f"streamer is here with SQL: {sql}")
            cursor = None
            capsule: DataCapsule = sql if isinstance(sql, DataCapsule) else DataCapsule(sql)
            try:
                cursor = self.get_executed_cursor(profile_name, capsule)
            except Exception as e1:
                logger.error(f"problem with cursor")
                return None
            if cursor is None:
                logger.error(f"lets take dummy")
                return None
            #cursor.execute(sql)
            #if not self.analyze_column_meta(cursor.description, profile_name):
            #    logger.error(f"problem with analyze meta")
            #    cursor.close()
            #    return None
            while True:
                try:
                    row = cursor.fetchone()
                except Exception as e1:
                    logger.error(e1)
                    break
                if row is None:
                    break
                else:
                    yield row
            cursor.close()
            logger.info("streamer ends")
        return streamer

    def run(self, profile_name: str, sql: str | DataCapsule, do_return: bool = True, **kwargs) -> DataCapsule:
        """
        Runs SQL and returns refreshed datacapsule
        - new_transaction = False -- do we need to start with commit()
        - on_error_rollback = True
        - on_error_disconnect = False
        - on_success_commit = True
        - verbose = False
        - style = 'number' (vs 'name', 'both', 'dataset')
        """
        capsule: DataCapsule = sql if isinstance(sql, DataCapsule) else DataCapsule(sql)
        capsule.result_set = []
        capsule.set_action_data_profile(profile_name)

        if capsule.sql_command is None or len(capsule.sql_command.strip()) < 1:
            logger.warning(f"Empty SQL command")
            capsule.set_action_error("Empty command")
            return capsule
        #if kwargs:
        #    capsule.set_flags(kwargs) # FIXME -- CHECK IT!

        #control: dict = self.prepare_flags(kwargs) # how to behave/act during execution of one command
        time_start: datetime = datetime.now()
        cursor = self.get_executed_cursor(profile_name, capsule)
        if cursor is None:
            if capsule.get_flag("verbose"):
                logger.error("Problematic command")
            capsule.set_action_error("Problematic command")
            return capsule

        #with self.conn.cursor() as cursor: // cannot use this approach, Sybase ASA cursor __enter__() has some bug (AttributeError) in sqlanydb 1.0.14
        try:
            capsule.set_action_success(True)
            capsule.load_data(cursor) # DataCapsule is aware of cursor
            time_spent: float = (datetime.now() - time_start).total_seconds()
            capsule.set_action_consumed_time(time_spent)
        except Exception as e1:
            capsule.set_action_error(str(e1))

        self.try_and_log(cursor.close, logger.warning, "Failed to close cursor, in confusion, ignoring") # close cursor anyway
        if capsule.get_flag('on_success_commit'):
            connection = self.find_connection(profile_name)
            if connection:
                self.try_and_log(connection.commit, logger.error, "Failed to end transaction after success, ignoring")

        if capsule.get_flag("verbose"):
            capsule.debug()
        
        return capsule

    def try_and_log(self, try_action: Callable, problem_logging_action: Callable, logging_message_prefix: str) -> bool:
        """
        Perform simple (database connection) action (function without params) and if failed log it using logging function (logger.error or logger.warning).
        try_action shoold be like commit, rollback, disconnect (from their owner object)
        Just to shorten run() code there are different flags (do commit before, after etc)
        """
        try:
            try_action()
        except Exception as e1:
            problem_logging_action(f"{logging_message_prefix}, {e1}")
            return False
        return True

    def reconnect(self, profile_name, wake_up_select: str | None = None):
        """
        Reconnect (eg. after sudden disconnect) for use by outsiders.
        Tries to disconnect first, ignores disconnection failure.
        Keep in mind -- we have automatic connection (command "run") and dev dont need to worry about connect, so try to avoid reconnect as well.
        We force here new connect by running simple SQL command, but it may not work for all DBMS-s ("SELECT 1") 
        """
        try:
            self.disconnect(profile_name)
        except Exception as e1:
            logger.warning(f"disconnect failed, ignoring, probably disconnected, {e1}")
        wake_up_command = wake_up_select if wake_up_select else "SELECT 1"
        try:
            self.run(profile_name, wake_up_command) # first run for non-connected, tries to connect
        except Exception as e1:
            logger.warning(f"wakeup SQL, {wake_up_command}")
            logger.error(f"still no connection (or incompatible wake-up SQL), {e1}")
            return False
        return True

    def commit(self, profile_name: str):
        profile = self.get_profile(profile_name)
        if profile and "connection_object" in profile and profile["connection_object"]:
            profile["connection_object"].commit()

    def rollback(self, profile_name: str):
        profile = self.get_profile(profile_name)
        if profile and "connection_object" in profile and profile["connection_object"]:
            profile["connection_object"].rollback()

    def disconnect(self, profile_name: str):
        profile = self.get_profile(profile_name)
        if profile and "connection_object" in profile and profile["connection_object"]:
            profile["connection_object"].close()

    def disconnect_all(self):
        for profile_name in self.profiles.keys():
            self.disconnect(profile_name)
            logger.debug(f"{profile_name} disconnected")

    def sql_string_value(self, profile_name: str, value: Any, datacolumn: DataColumn, for_null: str = 'NULL') -> str:
        """
        Knowing value and some info about its general type, return string which will be part of SQL command (eg INSERT) 
        where texts and times are surrounded with apostrophes and empty strings are replaced with nulls for numbers and dates
        and texts are escaped (this one is made using by profile name what is wrong -- taking data from source and saving to target the target rules must be followed)
        """
        if value is None:
            return for_null # NULL (without surronding apostrophes)
        if datacolumn.is_literal_type:
            return str(value) if value > '' else for_null
        if datacolumn.class_name == 'TIME':
            return f"'{value}'" if value > '' else for_null # if value then with surroundings, otherwise NULL without
        driver_module: ModuleType | None = self.get_driver(profile_name)
        if driver_module:
            escaped_value = driver_module.escape(value) or value
            return f"'{escaped_value}'"
        escaped = value.replace("'", "''") # ' -> ''
        return f"'{escaped}'"

    def prepare(self, profile_name, cell_value, data_class, needs_escape):
        if cell_value is None:
            return 'NULL'
        if data_class == 'INT':
            if cell_value == '':
                return 'NULL'
            else:
                return str(cell_value)
        else:
            driver_module: ModuleType | None = self.get_driver(profile_name)
            if driver_module:
                escaped_value = driver_module.escape(cell_value)
                return f"'{escaped_value}'"
            escaped = cell_value.replace("'", "''") # ' -> ''
            return f"'{escaped}'"

    def generate_command_for_create_table(self, target_table: str, create_as_temp: bool = False, cols_def: list | dict | None = None, map_columns: dict | None = None) -> str:
        as_temp = ' TEMP' if create_as_temp else ''
        if cols_def is None:
            return ""
        if isinstance(cols_def, list): # list of DataColumn's
            create_columns = ', '.join([column.get_ddl_declaration() for column in cols_def])
        else: # vana dict variant
            if map_columns is None:
                create_columns = ', '.join([col_def['name'] + ' ' + col_def['type'] for col_def in cols_def])
            else:
                create_columns = ', '.join([map_columns[col_def['name']] + ' ' + col_def['type'] for col_def in cols_def if col_def['name'] in map_columns and map_columns[col_def['name']] != ''])
        
        create_table = f"CREATE{as_temp} TABLE {target_table} ({create_columns})"
        print(f"{create_table=}")
        return create_table
        


def tests():
    content = """ 
    dapu: 
        driver: pg
        host: 192.168.0.220
        port: 5431
        engine: ~
        database: dapu_dev1
        username: dapu_dev1_admin
        password: abc
    """
    hub = Hub(content, "pg: \n  package: dbpoint.drivers\n  module: pg")
    dc = hub.run("dapu", "select current_timestamp")
    print(str(dc)) # sql
    print(str(dc[0][0])) # time
    


if __name__ == "__main__":
    tests()

