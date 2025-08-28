def stuctured_fetch_index(self, cursor, profile_name: str) -> list[tuple] | None:
        """
        The simpliest variant from cursor to list, list item (row) is number-indexed (tuple)
        """
        try:
            return cursor.fetchall()
        except Exception as e1:
            return None
    
    def stuctured_fetch_label(self, cursor, profile_name: str) -> list:
        """
        Labeled variant from cursor to list, list item (row) is string-labeled (access: rs[0].colname)
        """
        # cur.description: tuple[str, DBAPITypeCode, int | None, int | None, int | None, int | None, bool | None]
        if not self.analyze_column_meta(cursor.description, profile_name):
            logger.error("During analyze of columns the emptyness happenes")
            return None
        columns_named_spaced = self.extract_name_string(' ')
        if columns_named_spaced is None:
            logger.error(f"No metadata present")
            raise Exception('no metadata grabbed')
        record_type = namedtuple('NamedTupleRecord', columns_named_spaced, rename=True)
        try:
            return list(map(record_type._make, cursor.fetchall()))
        except Exception as e1:
            return None

    def stuctured_fetch_both(self, cursor, profile_name: str) -> list[dict]:
        """
        Duplicated variant from cursor to list, list item (row) is bot string-labeled and int-labeled (dict) 
        """
        # cur.description: tuple[str, DBAPITypeCode, int | None, int | None, int | None, int | None, bool | None]
        if not self.analyze_column_meta(cursor.description, profile_name):
            logger.error("During analyze of columns the emptyness happenes")
            return None
        columns_named_spaced = self.extract_name_string(' ')
        record_type = namedtuple('DictRecord', columns_named_spaced, rename=True)
        result_set = []
        row: tuple
        for row in cursor.fetchall():
            # row on numbrilise indeksiga (list): row[0], row[1] jne
            new_row : dict = {}
            for pos, cell in enumerate(row): # kordame datat
                new_row[record_type._fields[pos]] = cell # str key
                new_row[pos] = cell # int key
            result_set.append(new_row) # list[dict[int|str, any]]
        return result_set

    def structured_fetch_dataset(self, cursor, profile_name: str) -> Dataset:
        """
        Our custom class/structure
        """
        rowset = cursor.fetchall()
        full_data: Dataset = Dataset()
        if rowset:
            for row in rowset:
                datarow = Datarow()
                for col in row:
                    datarow.add_cell(col)
                full_data.append(datarow)
        return full_data


        
            fetch_switch: dict = { # maps result set access style name to function with executed cursor as argument
                'number' : self.stuctured_fetch_index
                , 'name': self.stuctured_fetch_label
                , 'both': self.stuctured_fetch_both
                , 'dataset': self.structured_fetch_dataset
            }
#            result_set = (fetch_switch[control['style']])(cursor, profile_name) # if control['style'] == 'number': result_set = self.stuctured_fetch_index(cur)



    def copy_to(self, sql : str, profile_name : str, first_row_grab : Callable, side_effects : Callable | None, prepare_row_command : Callable, save_command : Callable, info_step: int = 1000):
        """
        
        """
        # FIXME , REVIEW ME
        #permanent_info = {}
        pos = 0
        logger.info(f"copy_to.. {profile_name}")
        logger.info(f"side by (not used): {side_effects.__qualname__}")
        logger.info(f"prep by: {prepare_row_command.__qualname__}, {type(prepare_row_command)}")
        logger.info(f"save by: {save_command.__qualname__}, {type(save_command)}")
        flower = self.fn_stream(profile_name)
        if flower is None:
            logger.error("Flow is None?!")
            return -1
        logger.info(f"flow by: {flower.__qualname__}, {type(flower)}")

        permanent_info = None
        
        for pos, row in enumerate(flower(sql), 1):
            if pos == 1:
                logger.info(row)
                permanent_info = self.last_command.query_cols
                logger.info(permanent_info)
                #pass
                #permanent_info : dict = first_row_grab()
                #if permanent_info is None:
                #    logger.error("Problem with GRAB")
                #    return -1
                #logger.debug(f"pos=1 start side effect")
                #side_quest = side_effects() if side_effects is not None else True
                #logger.debug(f"pos=1 end side effect")
            logger.info(row)
            
            command = prepare_row_command(row, permanent_info)
            logger.warning(command)
            if not save_command(command, pos):
                logger.error(f"Problem with SAVE, made {pos}")
                return -pos # if 1st row failes, return -1, if second returns -2
            # if pos % info_step == 0:
            #     mem_free = mem_free_now()
            #     logger.info(f"Pulled up to here {pos} rows, free memory {mem_free:.2f} MB")
            #     if mem_free < 1:
            #         logger.error(f"Out of memory very soon, so lets quit as we can it do now")
            #         return -pos
            
        logger.info(f"copy_to END {pos} rows")
        return pos




    def analyze_column_meta(self, cursor_description: list[tuple] | None, profile_name: str) -> bool:
        """
        This (columns_definition) belongs to ONE profile (channel), but **currently** we interpret is as LAST in any channel
        """
        #self.columns_definition.clear()
        self.last_command.query_cols = []
        if cursor_description is None:
            return False
        
        driver_module: ModuleType = self.get_driver(profile_name)
        mapper = None 
        if hasattr(driver_module, "class_mapper"):
            mapper = driver_module.class_mapper()
        if hasattr(driver_module, "type_mapper"):
            mapper = driver_module.type_mapper

        for column_description in cursor_description:
            dcol = DataColumn(column_description, mapper)
            self.last_command.query_cols.append(dcol)
            #dcol.get_ddl_declaration()
            #col_def = {'name': dcol.get_name(), 'name_original': dcol.get_name(), "class": dcol.class_name, "type": dcol.typename, "needs_escape": not dcol.is_literal_type()}
            #logger.warning(col_def)
            #self.columns_definition.append(col_def)
        return True


        for desc in cursor_description: # https://peps.python.org/pep-0249/#description
            logger.warning(desc) #  ('id', DBAPISet({480, 482, 484, 496, 500, 604}), None, 4, 0, 0, 0)
            if isinstance(desc[1], frozenset):
                logger.error('jah, on frozenset')
                dbapiset_mapper: dict = driver_module.type_mapper()
                dataclass = dbapiset_mapper.get(list(desc[1])[0], 'TEXT')

            else:
                logger.warning(type(desc[1]))
                dataclass = mapper.get(desc[1], desc[1]) # here logic: if not mentioned in mapper then itself (ALT: if not mentioned then TEXT)
            
            if dataclass in ('BIGINT', 'INT', 'NUMERIC', 'BOOLEAN', 'INTEGER', 'DECIMAL', 'FLOAT'):
                needs_escape = False
            else:
                needs_escape = True
            
            if dataclass not in ('TEXT') and desc[3] > 1 and desc[4] is not None: # and desc[4] != 65535:
                details = []
                details.append(f"{desc[4]}")
                if desc[5] is not None and desc[5] != 65535:
                    details.append(f"{desc[5]}")
                datatype_details = ",".join(details)
                datatype_details = f"({datatype_details})" # sulud ümber
            else:
                datatype_details = ''
            datatype = dataclass + datatype_details
            temp_name = desc[0] # vaja oleks korduvust ja nime olemasolu kontrollida (aga need võivad ka feilida ja las arendaja teeb korda)
            col_def = {'name' : temp_name, 'name_original' : desc[0], "class" : dataclass, "type" : datatype, "needs_escape" : needs_escape}
            logger.warning(col_def)
            self.columns_definition.append(col_def)
        return True


    def get_columns_def(self, profile_name) -> list[DataColumn]:
        return self.last_command.query_cols
    
    def get_columns_definition(self, profile_name)-> list[dict]:
        """
        Last connection last SQL
        """
        return self.last_command.query_cols

    def __repr__(self):
        # kõik profiilid ühendusinfoga (parool on varjestatud) ja profiilide metainfoga (millal, palju)
        str_lines = []
        profile: ProfileSql
        for jrk, (name, profile) in enumerate(self.profiles.items(), 1):
            str_lines.append(f"{jrk}) {name}")
            safe_profile: ProfileSql = profile.model_copy(deep=True)
            safe_profile.password = "******"
            str_lines.append(str(safe_profile.model_dump_json()))
            str_lines.append("")
        str_lines.append("")
        return "\n".join(str_lines)

    def extract_name_string(self, separator: str=', ') -> str:
        if not self.get_columns_def('suva'):
            return ''
        return separator.join([col.colname for col in self.last_command.query_cols])
        return separator.join([col['name'] for col in self.columns_definition])


def reconf_logging(solution_name, level=logging.DEBUG):
    """
    Once you can redefine logging globally -- before first use!
    Let's add timestamp in begginning (if no time is displayed by default (you cannot tell the bees))
    And let's print out everything, incl debug-level
    FIXME: make these adaptions controlled by some env.var (not by Conf class, which may itself already use logging)
    
    https://docs.python.org/3/library/logging.html#logrecord-attributes
    %(message)s
    %(asctime)s
    %(lineno)d
    %(module)s
    %(name)s
    %(levelname)s
    """
    frm = "%(asctime)s:%(levelname)8s:%(lineno)5d:%(module)-15s:%(name)-6s:%(message)s"
    
    if '%(module)' not in frm:
        frm = ' %(module)-12s:' + frm
    if '%(lineno)' not in frm:
        frm = '%(lineno)4d:' + frm
    if '%(asctime)' not in frm:
        frm = '%(asctime)s:' + frm
    logging.basicConfig(format=frm, level=level, force=True)

def get_custom_logger(solution_name):
    reconf_logging(solution_name, logging.INFO)
    return logging.getLogger(solution_name)

### PURE FUNCTIONS ###

# def mem_free_now() -> float: 
#     """
#     Returns free memory in megabytes as float
# add: try
#     """
#     return psutil.virtual_memory().available / (1024 * 1024)

