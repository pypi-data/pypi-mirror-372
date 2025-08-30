from loguru import logger
from typing import Iterable, Any
import json
from pydantic_yaml import parse_yaml_raw_as  #, to_yaml_str
from datetime import datetime
import copy


class Datacell():
    """
    Cell is something with has simple value (str, int, ...). So, no dict nor list (but by definition Any)
        Only Q is: does datacell or/an datarow may own sub dataset (or even more datasets)?
        Cell may have one link and multiple buttons
            Button action is actually defined by navi framework (hopefully open enough to support any other framework?)
    Additionally cell may have some properties eg link (and browser related "newtab", defaults to False)
    Conclusion: Datacell is all about data (not HTML representation), all subvalues are pure data (eg label is plain text)
    """

    def __init__(self, init_value: Any | dict):
        """
        Initialization can be done in simple way -- only cell value
        Or by dict that represents to internal structure of datacell (usually output of datacell)
        """
        self.empty_label: str = ""
        self.value: Any = None
        self.link: str | None = None # web-based knowledge (http pointer to resource)
        self.newtab: bool = False # browser-related feature (in this context should link opened in new tab of viewer/browser)
        self.label: str = self.empty_label
        self.style_class: str = ""

        if isinstance(init_value, dict):
            self.set_value(init_value.get("value", None))
            self.set_link(init_value.get("link", None), init_value.get("newtab", False))
            self.set_label(init_value.get("label", None))
            self.set_style(init_value.get("style_class", None))
        else:
            if isinstance(init_value, Datacell): # init by other cell, new cell will be without buttons of old cell!!!
                self.set_value(init_value.value)
                self.set_link(init_value.link, init_value.newtab)
                self.set_label(init_value.label)
                self.set_style(init_value.style_class)
            else:
                self.set_value(init_value) # simple value
        # cell buttons are inside cell (even on fictional cell without data)
        # instead of fictional cell, better use row level buttons
        self.buttons = [] # navigational framework based and business-oriented knowledge (what can be done with what cell)
    
    def set_value(self, value: Any) -> None:
        self.value = value
        self.text = f"{self.value}" if self.value is not None else ""
    
    def set_label(self, label: str) -> None:
        self.label = label or self.empty_label

    def set_link(self, url: str, newtab: bool = False) -> None:
        self.link = url
        self.newtab = newtab

    def set_style(self, style_class: str) -> None:
        self.style_class = style_class or ""
    
    def add_button(self, label: str, onclick: str, style_class: str = ""):
        """
        Attaches to cell labeled and styled command which can be used as button on UI
        Parameter onclick is JS expression what can be used onclick=""
        """
        self.buttons.append({"label": label, "start": onclick, "style_class": style_class})

    def html_link(self) -> str: # deprecated 
        """
        Returns string value for HTML output. Just value or HTML A-element with href and target attributes.
        NB!!! this is not esential part of datacell, so don't use (deprecated)
        """
        if self.link:
            if self.newtab:
                target_newtab = " target=\"_blank\""
            else:
                target_newtab = ""
            return f"<a href=\"{self.link}\"{target_newtab}>{self['str']}</a>"
        else:
            return f"{self.value}" if self.value is not None else "" # Just value (empty string in case of None)
    
    def __str__(self):
        return self.text # if assignment of value is always via set_value() then text is correct

    def __getitem__(self, pointer: str|int|None = None):
        if pointer is None:
            return self.value
        if isinstance(pointer, str):
            if pointer == "value" or pointer == "":
                return self.value
            if pointer == "str" or pointer == "text":
                return self.text
            if pointer == "link":
                return self.link
            if pointer == "inner" or pointer == "html":
                return self.html_link()
            if pointer == "label":
                return self.label
            if pointer == "style_class":
                return self.style_class
            if pointer == "buttons":
                return self.buttons
            if pointer == "dict":
                return self.__dict__()
                #return {"value": self.value, "label": self.label, "link": self.link, "newtab": self.newtab, "style_class": self.style_class} 
        return ""
    
    def __dict__(self) -> dict:
        return {"value": self.value, "label": self.label, "link": self.link, "newtab": self.newtab, "style_class": self.style_class} 
    

class Datarow():
    
    def __init__(self, row: Iterable | dict | None = None):
        self.cells = [] # data
        self.columns = [] # headers (labels)
        if row is None:
            return
        if isinstance(row, dict):
            for key, value in dict.items():
                self.add_cell(value)
                self.columns.append(key)
        else:
            if isinstance(row, Iterable): # list, tuple
                for pos, item in enumerate(row, 0):
                    self.add_cell(item)
                    self.columns.append(str(pos)) # "0", "1", "2" etc
    
    def __setitem__(self, pointer: int | str, cell: Datacell | Any):
        """
        Setting value for one cell in datarow (by index or by key) 
        """
        if not isinstance(cell, Datacell): # if not cell then try to make
            cell = Datacell(cell) # nb! if "strange type" then it stays strange (this feature may change in future)
        if isinstance(pointer, int):
            if pointer >= 0 and pointer < len(self.cells):
                self.cells[pointer] = cell
            else:
                if pointer == len(self.cells): # intention was to add new at end to last+1 position
                    self.add_cell(cell)
                else:
                    logger.error(f"Wrong pointer for datacell, {pointer}, there are {len(self.cells)} items")
            return # this line done
        else:
            if isinstance(pointer, str):
                # find column position by name
                for pos, col in enumerate(self.columns, 0):
                    if col == pointer:
                        self.cells[pos] = cell
                        return # found, done
                logger.error(f"Key '{pointer}' not found amoungts the cell columns")
                return
        logger.error(f"Problem with pointer, type is {type(pointer)}")

    def add_cell(self, cell: Datacell | Any) -> Datacell:
        if not isinstance(cell, Datacell):
            cell = Datacell(cell) # make it as datacell
        self.cells.append(cell)
        return cell # may differ fom input if wasn't datacell
        

    def __getitem__(self, pointer) -> Datacell:
        if isinstance(pointer, int):
            if pointer >= 0 and pointer < len(self.cells):
                return self.cells[pointer]
            else:
                logger.error(f"Wrong pointer to get datacell, {pointer}, there are {len(self.cells)} items")
                return None # this line done
        if isinstance(pointer, str):
            # find column position by name
            for pos, col in enumerate(self.columns, 0):
                if col == pointer:
                    return self.cells[pos]
            logger.error(f"Key '{pointer}' not found amoungts the cell headers")
            return None
        logger.error(f"Problem with pointer, type is {type(pointer)}")
        #if type(pointer) is slice:
        #    ds: Dataset = Dataset()
        #    ds.rows = [ self.rows[n] for n in range(pointer.start or 0, pointer.stop or len(self) - 1, pointer.step or 1) ]
        #    return ds
        return None
    
    def __iter__(self):
        for cell in self.cells:
            yield cell
    
    def __len__(self):
        return len(self.cells)
        
    def __str__(self):
        return ", ".join([str(cell) for cell in self.cells])
    
    def to_list(self):
        return [cell["dict"] for cell in self]
    
    def copy(self):
        
        return copy.copy(self)


class Dataset():

    def __init__(self):
        self.rows: list[Datarow] = []
    
    def __iter__(self):
        for row in self.rows:
            yield row
    
    def __len__(self):
        return len(self.rows)

    def __getitem__(self, pointer):
        if type(pointer) is slice:
            ds: Dataset = Dataset()
            ds.rows = [ self.rows[n] for n in range(pointer.start or 0, pointer.stop or len(self) - 1, pointer.step or 1) ]
            return ds
        else: # FIXME lisada võimekus lubada str tüüpi sisendit kui on lubatud stringid kui headerid (pealkirjad) eelnevalt deklareeritud
            return self.rows[pointer]
    
    def __setitem__(self, pos: int, value: Datarow):
        self.rows[pos] = value

    def append(self, row: Datarow):
        self.rows.append(row)
    
    def to_json(self):
        data = [row.to_list() for row in self.rows]
        return json.dumps(data, indent=4)
    
    def from_json(self, json_string: str):
        row_list: list = json.loads(json_string)
        for row in row_list:
            self.rows.append(Datarow(row))
    
    def __str__(self):
        return str(self.rows)

