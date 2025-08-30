from types import ModuleType
from typing import Callable
import importlib # for using Actors package dynamically
from loguru import logger

def prepare_function(module_short_alias: str, function_name: str, modules_cache: dict | None = None, modules_defs: dict | None = None) -> Callable | None:
    """
    Returns object of type function/Callable
    """
    the_module: ModuleType | None = prepare_module(module_short_alias, modules_cache, modules_defs) # see mäping annab teada õige mooduli
    if the_module is None:
        logger.error(f"No module for {module_short_alias}")
        return None
    if not hasattr(the_module, function_name):
        logger.error(f"No function ({function_name}) in module ({the_module.__name__}) for {module_short_alias}")
        logger.error(the_module)
        return None
    the_function = getattr(the_module, function_name)
    return the_function # returns the function from module
    

def prepare_module(module_short_alias: str, modules_cache: dict | None, modules_defs: dict | None = None) -> ModuleType | None:
    """
    Imports module where some functionality resides, if not already loaded
    Parameter module_short_alias is reference string kept in database or file (sort of safeguard)
    Returns module
    Read https://docs.python.org/3/library/importlib.html
    """
    # if cache dict is given try cache
    if modules_cache and module_short_alias in modules_cache:
        logger.debug(f"Module for command {module_short_alias} is returned from cache")
        return modules_cache[module_short_alias]
    module_long_name = find_module_name(module_short_alias, modules_defs)
    the_module: ModuleType | None = None
    if module_long_name is None or module_long_name.startswith('.') or module_long_name.endswith('.'):
        logger.error(f"Module for {module_short_alias} is not defined or is not allowed")
        return None
    try: # lets try to import module
        the_module = importlib.import_module(module_long_name)
        #logger.debug(f"Module {module_long_name} is loaded")
        if modules_cache:
            modules_cache[module_short_alias] = the_module # changes input dict (python, here we actually need this feature)
            #logger.debug(f"Module {module_long_name} is cached as {module_short_alias}")
    except Exception as e1:
        logger.error(f"Cannot import module '{module_long_name}', {e1}")
        return None
    return the_module


def prepare_module_fn(module_short_name: str, cacher: Callable, mapper: Callable) -> ModuleType | None:
    the_module: ModuleType | None = None
    if cacher:
        the_module = cacher(module_short_name, None) # asking from cache
    if the_module: 
        return the_module
    module_info: dict | None = mapper(module_short_name)
    if module_info:
        module_long_name = f"{module_info['package']}.{module_info['module']}"
        the_module = importlib.import_module(module_long_name)
    if the_module and cacher:
        cacher(module_short_name, the_module) # write to cache
    return the_module


def find_module_name(action_alias: str, modules_defs: dict | None = None) -> str | None:
    """
    From action alias calculates somehow module full name.
    """
    #siin on nii page-de asjad, kui slottide asjad:
    #actors: dict = yaml_string_to_dict(read_content_of_file(os.path.realpath('actors.yaml')))
    #trusted_agent: dict = self.context.get_agent_definition(action_alias)
    #actors = modules_defs
    trusted_agent: dict | None = modules_defs.get(action_alias) if modules_defs is not None else None
    if not trusted_agent:
        return None
    #if warning := trusted_agent.get('warning', ''): # eg. deprecation warning
    #    warning = clean_log_message(warning) # cleaning because it comes to us from custom file
    #    logger.warning(f"{action_alias} says {warning}")
    #logger.debug(trusted_agent)
    return f"{trusted_agent['package']}.{trusted_agent['module']}"

