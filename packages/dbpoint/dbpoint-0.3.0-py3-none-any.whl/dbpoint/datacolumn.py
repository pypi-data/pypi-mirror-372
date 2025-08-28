from loguru import logger
from enum import Enum
from typing import Any, Callable

class DataTypeClass(Enum):
    Boolean = 1
    Number = 2
    Text = 3
    Binary = 4


class DataColumn():

    def __init__(self, input: str | None, mapper: Callable|None):
        self.colname: str = ''
        self.typename: str = ''
        self.class_name: str = '' # TEXT, NUMBER, BOOL, BINARY
        self.display_size: int = None
        self.internal_size: int = None
        self.precision: int = None # full length
        self.scale: int = None # length inside prev, length of decimal part)
        self.not_null: bool = False
        
        if isinstance(input, tuple):
            self.parse_cursor_description(input, mapper)
        else:
            self.colname: str = str(input)
            logger.warning("veidi paha initsialiseerimine, anna parem 7-ne tuple ette")
    
    def __str__(self):
        return f" + {self.colname} + {self.typename} + {self.class_name} + {self.internal_size} + {self.precision} + {self.scale} " + str(self.is_literal_type())
    
    def get_name(self) -> str:
        if not self.colname:
            logger.warning(f"Empty name because of no data")
            return ""
        return self.colname
    
    def get_ddl_declaration(self) -> str:
        """
        colname text
        colname numeric(15,2)
        colname numeric(8)
        RESULT for Postgre (not for source database)
        """
        if not self.class_name:
            logger.warning(f"No declaration possible because of no data, returning None")
            return None
        if not self.typename: # we have bad general data about data class (eg NUMBER for INT, BIGINT, DECIMAL, MONEY, FLOAT and NUMERIC)
            if self.class_name == 'NUMBER':
                if self.internal_size == 8 and self.scale == 0:
                    self.typename = 'BIGINT'
                if self.internal_size < 8 and self.scale == 0: # 4 int, 2 smallint
                    self.typename = 'INT'
                if self.scale > 0:
                    self.typename = 'NUMERIC'
            if self.class_name == 'TEXT':
                if self.precision < 51:
                    self.typename = 'VARCHAR'
                else:
                    self.typename = 'TEXT'
            if self.class_name == 'BINARY':
                self.typename = 'BYTEA'
            if self.class_name == 'BOOL':
                self.typename = 'BOOLEAN'
        if not self.typename:
            logger.error(f"Unable to put together needed data, {self}")
            return None
        precise = ""
        if self.type_name == 'NUMERIC':
            precise = f"({self.precision},{self.scale})"
            if precise == "(,)":
                precise = ""
            if precise.endswith(",)"):
                precise = f"({self.precision})"
        if self.type_name == 'VARCHAR':
            ... # possible idea to make short text as varchar(short)
            if self.precision < 21:
                precise = 25
            else:
                precise = max(self.precision, 250)
        return f"{self.typename}{precise}"

    def is_literal_type(self) -> bool:
        """
        Is current datacolumn data written as-is (literal), opposite means to be surrounded by apostrophes
        """
        if not self.class_name:
            logger.warning(f"No declaration possible because of no data, returning False for column {self.colname}")
            return False # => for that (unknown type) column apostrophes must be used
        if self.class_name in ('NUMBER', 'BOOL'):
            return True # use value as-is 
        return False # use apostrophes and escaping
    
    def parse_cursor_description(self, descriptor_tuple: tuple, mapper: Callable|None) -> bool:
        """
        Parses dblib cursor description tuple to our structure.
        tuple: (name, type_code, display_size, internal_size, precision, scale, null_ok) https://peps.python.org/pep-0249/
               ('id', DBAPISet({480, 482, 484, 496, 500, 604}), None, 4, 0, 0, 0)
               type_code can be string and frozenset (non-trustable, eg ASA driver for col int gives set(decimal, float, int, tinyint), PG has normal strings)
        """
        name, type_code, display_size, internal_size, precision, scale, null_ok = descriptor_tuple # unpack 7 items
        self.colname = name
        self.display_size = display_size
        self.internal_size = internal_size
        self.precision = precision
        self.scale = scale
        self.not_null = (null_ok == 0)

        if isinstance(type_code, str): # most cases
            self.typename = type_code.upper()
            if mapper:
                self.class_name = mapper(self.typename) # upprecase text -> classname mapper
            else:
                self.class_name = self.general_mapper(self.typename) # uppercase text -> classname mapper
            return True
        
        if isinstance(type_code, frozenset): # Sybase ASA some strange idea (what data type is not used by devs for storage nor presentation)
            if mapper:
                self.class_name = mapper(list(type_code)) # number -> classname mapper
                return True
            else:
                logger.error(f"Cannot find class, no mapper function given for DBMS, assume TEXT")
                self.class_name = 'TEXT'
                return False
        logger.error(f"cannot handle this {type(type_code)}, {type_code}")
        return False

    def general_mapper(self, type_name):
        """
        Maps datatype to data class/category: TEXT, INT, TIME, BINARY
        If not found uses input datatype as class
        Main purpose to know if value must be surroundd (by apostrophes), so JSONB, ARRAY, GEOMETRY should result TEXT
        """
        # AGA ARRAY jm
        very_ambitious_mapping: dict = {
                'CHAR' : 'TEXT'
                , 'NCHAR' : 'TEXT'
                , 'NVARCHAR' : 'TEXT'
                , 'VARCHAR' : 'TEXT'
                , 'LONG VARCHAR' : 'TEXT'
                , 'LONG NVARCHAR' : 'TEXT'
                , 'TEXT': 'TEXT'
                , 'MEDIUMTEXT' : 'TEXT'
                , 'LONGTEXT' : 'TEXT'
                , 'GEOMETRY': 'TEXT'
                , 'JSON': 'TEXT'
                , 'JSONB': 'TEXT'
                , 'XML': 'TEXT'
                , 'ARRAY': 'TEXT'
                , 'DATETIME' : 'TIME'
                , 'TIME' : 'TIME'
                , 'TIMESTAMP' : 'TIME'
                , 'DATE' : 'TIME'
                , 'TINYINT': 'INT'
                , 'BLOB' : 'BINARY'
                , 'LONG BINARY' : 'BINARY'
                , 'INT' : 'INT'
                , 'BIGINT': 'INT'
                , 'SERIAl': 'INT'
                , 'BIGSERIAL': 'INT'
                , 'DOUBLE': 'INT'
                , 'FLOAT': 'INT'
                , 'NUMERIC': 'INT'
                , 'MONEY': 'INT'
                , 'BIGMONEY': 'INT'
                , 'SMALLINT' : 'INT'
            }
        
        possible_result = very_ambitious_mapping.get(type_name.upper(), None)
        if possible_result is None:
            logger.error(f"Original type_name is {type_name}, cannot find class")
            possible_result = type_name.upper()
        return possible_result
    