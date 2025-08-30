from loguru import logger
from pydantic import BaseModel, RootModel
from typing import Any, List
from types import ModuleType

class ProfileSqlExtra(BaseModel):
    """
    Add here any needed keys for extended connection creation
    """
    connect_timeout: int | None = None # 10 sek
    keepalives_idle: int | None = None # 120 sek
    application_name: str | None = None # mingi nimi

    driver: str | None = None # for ODBC (inside connectstring)
    product: str  | None = None # custom -- to make differencies ('mssql', 'progress')
    autocommit: bool | None = None # ODBC
    timeout: int | None = None # ODBC
    readonly: bool | None = None # ODBC
    encoding: str | None = None # ODBC ?? 'utf-8'
    ansi: bool | None = None # ODBC
    attrs_before: str | None = None # ODBC -- pole kindel, kas see on string

    tcp_connect_timeout: int | None = None # for Oracle (actually float, 20.0 is default)
    expire_time: int | None = None # for Oracle
    retry_count: int | None = None # for Oracle

    truncate_too_large: str | None = None # use ="output" for OpenEdge Progress where SQL API is broken (actual col length is bigger then SQL API knows)



class ProfileSql(BaseModel, arbitrary_types_allowed=True):
    """
    Profile for RDBMS (SQL)
    """
    name: str # reference name to use this profile
    driver: str # pg -- this is string code to find driver module
    driver_module: ModuleType | None = None # this is object of type DataDriverGeneric
    connection_object: Any | None = None
    
    host: str | None = None # 192.168.0.220
    port: int | None = None # 5432
    engine: str | None = None # Sybase ASA thing
    database: str # dapu_dev1
    username: str | None = None # dapu_dev1_admin
    password: str | None = None # abc
    debug: bool | None = False 
    extra: ProfileSqlExtra | None = None
    class Config: 
        arbitrary_types_allowed=True # for AnyDataDriver/Any to not give runtime error

    def get_extras(self) -> dict:
        if self.extra:
            return self.extra.__dict__
        return {}


class ProfileSqlCollection(RootModel):
    """
    List of profiles for RDBMS connections
    """
    root: List[ProfileSql]

    def __iter__(self): # type: ignore (Pydantic deklareerib, et väljastataks TupleGenerator, aga töötab ka iteratoriga)
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]
    
    def find_by_name(self, name: str) -> ProfileSql | None:
        for item in self.root:
            if item.name == name:
                return item
        return None

