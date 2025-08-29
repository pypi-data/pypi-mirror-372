import datetime
import time

from .uuIO import save_json

import json
import base64
from enum import Enum
from typing import Dict, List
from types import SimpleNamespace
import math


class uuRestMethod(Enum):
    """

    """
    GET = "GET"
    POST = "POST"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"
    PUT = "PUT"
    DELETE = "DELETE"

    def __str__(self):
        if self == uuRestMethod.GET:
            return "GET"
        elif self == uuRestMethod.POST:
            return "POST"
        elif self == uuRestMethod.OPTIONS:
            return "OPTIONS"
        elif self == uuRestMethod.HEAD:
            return "HEAD"
        elif self == uuRestMethod.PUT:
            return "PUT"
        elif self == uuRestMethod.DELETE:
            return "DELETE"
        else:
            return "UNKNOWN"


class uuJsonObject(SimpleNamespace):
    def __init__(self, dictionary, **kwargs):
        super().__init__(**kwargs)
        for key, value in dictionary.items():
            if isinstance(value, dict):
                self.__setattr__(key, uuJsonObject(value))
            elif isinstance(value, list):
                for i in range(0, len(value)):
                    if isinstance(value[i], dict):
                        value[i] = uuJsonObject(value[i])
                self.__setattr__(key, value)
            else:
                self.__setattr__(key, value)


class uuDict(dict):
    def __init__(self, *args, **kwargs):
        super(uuDict, self).__init__(*args, **kwargs)

    def parse(self) -> uuJsonObject:
        return uuJsonObject(self)

    def save(self, filename: str, encoding: str = 'utf-8'):
        save_json(self, filename, encoding=encoding)


def repeat_letter(value: str = "", letter: str = "#"):
    delta = len(value) % 2
    half_len_of_value = math.floor(len(value) / 2)
    result_left_len = 32 - half_len_of_value - delta
    result_right_len = 32 - half_len_of_value
    result = ""
    result += letter * result_left_len
    result += f'{value}'
    result += letter * result_right_len
    return "# " + result + "\n"


def raise_exception(message: Dict, setup: Dict):
    if setup["raise_exception_on_error"]:
        raise Exception(str(message))
    return message


def dict_to_str(value: dict, formatted: bool = False) -> str:
    if formatted:
        return json.dumps(value, indent=4, ensure_ascii=False)
    return json.dumps(value)


def str_to_dict(value: str) -> dict:
    return json.loads(value)


def _safe_str_to_dict(value: str, encoding: str = 'utf-8') -> uuDict:
    """
    Converts str to dict. First tries to convert str to json.
    If it fails it returns dict with plain text
    :param value:
    :return:
    """
    try:
        result = json.loads(value)
        # if result is instance of list
        # replaces list with object containing itemList
        # ["item1", "item2] is replace by {"itemList": ["item1", "item2]}
        if isinstance(result, list):
            result = uuDict({"itemList": result})
        # result is dict
        else:
            result = uuDict(result)
        return result
    except:
        return uuDict({"__text__": value})


def _safe_bytes_to_dict(value: bytes, encoding: str = 'utf-8') -> uuDict:
    """
    Converts bytes to dict. First tries to convert bytes to json.
    If it fails it tries to convert bytes to string.
    If it fails it tries to convert bytes to base64.
    :param value:
    :param encoding:
    :return:
    """
    try:
        result = value.decode(encoding=encoding)
        return _safe_str_to_dict(result)
    except:
        return uuDict({"__base64__": base64.b64encode(value).decode()})


def convert_to_dict(value, encoding: str = 'utf:8') -> uuDict or None:
    if value is None:
        return None
    if isinstance(value, dict):
        return uuDict(value)
    if isinstance(value, str):
        return _safe_str_to_dict(value, encoding=encoding)
    elif isinstance(value, bytes):
        return _safe_bytes_to_dict(value, encoding=encoding)
    return json.loads(value)


def convert_to_str(value: dict or json or str or None, formatted: bool = False) -> str or None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return dict_to_str(value, formatted=formatted)
    raise Exception("Unexpected type of value. Value must be either dict or json or str")


def duplicate_dict(value: dict) -> dict:
    result = convert_to_str(value)
    result = convert_to_dict(result)
    return result


def escape_text(value: str) -> str:
    """
    Escapes text in error message
    :param value:
    :return:
    """
    result = ""
    allowed_letters = '0123456789/*-+.,<>?`´\'"~!@#$%^&*()_-=[]{}:\\|abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ \t\n\r'
    result = ''
    for letter in value:
        if letter in allowed_letters:
            result += letter
        else:
            result += "~"
    return result


def timestamp() -> str:
    local_time = datetime.datetime.now()
    utc_time = datetime.datetime.utcnow()
    delta = int(round((local_time-utc_time).seconds / 3600, 0))
    #microsecond = round(round(local_time.microsecond / 1000000, 1) * 100000, 1)
    local_time = datetime.datetime(local_time.year, local_time.month, local_time.day,
                                   local_time.hour, local_time.minute, local_time.second)
    result = f"[{local_time.isoformat()} local, +{delta:02}H utc]"
    return result



def linearize_dictionary(dictionary: dict, parent_path: str = "") -> dict:
    """
    From dict structure of {"level1": {"level2": {"variable1": "value1", "variable2": "value2"}}} creates dictionary
    {"level1.level2.variable1": "value1", "level1.level2.variable2": "value2"}
    :param dictionary:
    :param parent_path:
    :return:
    """
    result = {}
    for key, value in dictionary.items():
        if isinstance(value, str) or isinstance(value, int):
            result.update({f'{parent_path}{key}': value})
        else:
            sub_dictionary = linearize_dictionary(value, f'{parent_path}{key}.')
            for skey, svalue in sub_dictionary.items():
                result.update({skey: svalue})
    return result


def dict_path_exists(item: dict, path: str, is_null_value_allowed: bool = True) -> bool:
    """
    Test if dictionary contains specific path. For example if html is written like a JSON
    the user can test if json contains element h1 like this dict_path_exists(json, "html.body.h1")
    :param item:
    :param path:
    :param is_null_value_allowed:
    :return:
    """
    stop_pos = path.find(f'.')
    # if this is the last element and there are no more dots
    # then test if the element is not None (if required) and return True
    if stop_pos < 0:
        if path in item.keys():
            if is_null_value_allowed:
                return True
            else:
                return item[path] is not None
        return path in item.keys()
    # if this is not the last element
    else:
        key = path[:stop_pos]
        remaining_path = path[stop_pos+1:]
        if key not in item.keys():
            return False
        else:
            return dict_path_exists(item[key], remaining_path)


def dict_multiple_path_exists(item: dict, paths: List[str], is_null_value_allowed: bool = True) -> bool:
    """
    Test if dictionary contains multiple paths. If all paths exists the result value is True.
    Otherwise the result value is False.
    :param item:
    :param paths:
    :param is_null_value_allowed:
    :return:
    """
    for path in paths:
        if not dict_path_exists(item, path, is_null_value_allowed):
            return False
    return True


def dict_get_item_by_path(item: dict, path: str) -> dict or object:
    stop_pos = path.find(f'.')
    if stop_pos < 0:
        if path not in item.keys():
            raise Exception(f'Item does not exist at path "{path}" in given ditionary.')
        return item[path]
    else:
        key = path[:stop_pos]
        remaining_path = path[stop_pos+1:]
        if key not in item.keys():
            return None
        else:
            return dict_get_item_by_path(item[key], remaining_path)


def substitute_variables(value: str, variables_dict: dict, var_begin: str = "${", var_end: str = "}") -> str:
    """
    Substitutes variables in string from dictionary
    For example 'This ${value1} is ${value2}' where variables_dict is {'value1': 'code', 'value2': 'quite long'}
    :param value:
    :param variables_dict:
    :param var_begin:
    :param var_end:
    :return:
    """
    if not isinstance(value, str):
        return value
    result = ""
    remaining = value
    len_begin = len(var_begin)
    len_end = len(var_end)
    pos_begin = value.find(var_begin)
    while pos_begin >= 0:
        result += remaining[:pos_begin]
        remaining = remaining[pos_begin + len_begin:]
        pos_end = remaining.find(var_end)
        if pos_end <= 0:
            raise Exception(f"Cannot find \"{var_end}\" in string: {remaining}")
        variable_name = remaining[:pos_end]
        if variable_name not in variables_dict.keys():
            raise Exception(f'Variable with name "{variable_name}" in string "{value}" cannot be substituted because it  is not in dictionary {variables_dict}')
        result += variables_dict[variable_name]
        remaining = remaining[pos_end + len_end:]
        pos_begin = remaining.find(var_begin)
    result += remaining
    return result