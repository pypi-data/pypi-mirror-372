from loguru import logger
from jinja2 import Environment #Template, select_autoescape, 
from jinja2.loaders import FileSystemLoader, BaseLoader
from typing import Any
import os
import yaml

def generate_html(template_dir: str, template_file: str, template_data: dict):
    return generate_from_file(template_dir, template_file, template_data)

def generate_from_string(template_string: str, template_data: dict, ouch: dict= {}):
    env = Environment(loader=BaseLoader())
    if ouch:
        #env.globals['sodi'] = sodi
        env.globals = env.globals | ouch
    template = env.from_string(template_string)
    return template.render(template_data)

def generate_from_file(template_dir: str, template_file: str, template_data: dict):
    template_dir = os.path.realpath(template_dir)
    loader = FileSystemLoader(template_dir, encoding="utf-8")
    env = Environment(loader=loader)
    template = env.get_template(template_file)
    return template.render(template_data)

def yaml_string_to_dict(yaml_content_string: str, make_to_dict: str | None ='root') -> dict | None:
    structure: object = interpret_string_as_yaml(yaml_content_string, make_to_dict=make_to_dict)
    if isinstance(structure, dict):
        return structure
    return None

def yaml_string_to_list(yaml_content_string: str | None) -> list | None:
    structure: object = interpret_string_as_yaml(yaml_content_string or "", make_to_dict=None)
    if isinstance(structure, list):
        return structure # list
    return None

def yaml_string_to_structure(yaml_content_string: str) -> object | None:
    return interpret_string_as_yaml(yaml_content_string, make_to_dict=None)


def interpret_string_as_yaml(yaml_content_string: str, make_to_dict: str | None ='root') -> object | None:
    """
    Transform yaml string content as dict (or list??)
        (can we avoid yaml files with arrays at the highest level?)
    Param make_to_dict if not empty then non-dict is transformed to dict using that key
    """
    if yaml_content_string is None:
        return None
    structure = yaml.load(yaml_content_string, Loader = yaml.Loader) or None
    if structure is None or isinstance(structure, dict):
        return structure
    # if not dict:
    if make_to_dict:
        new_dict: dict = {make_to_dict : structure}
        return new_dict
    return structure # as is (whatever yaml.load gives to us)


def substitute_env(text: str | None) -> str | None:
    if text is None:
        return None
    if text.startswith("%") and text.endswith("%"):
        env_key = text[1:-1]
        substed = os.getenv(env_key, "")
    else: # as-is
        substed = text
    return substed
