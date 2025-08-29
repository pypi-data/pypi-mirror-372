"""
uuRest
===================================

Implementation of the main REST handler

import pip
from pip._internal import main as run_pip
from pip import main as run_pip
run_pip("install --upgrade pip".split(" "))
run_pip("install openpyxl".split(" "))

powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

pip install wheel
in conda prompt change directory to c:/git/cams/toolkit/pypi/uurest
python setup.py sdist bdist_wheel
python -m pip install .
python setup.py sdist bdist_wheel && python -m pip install .

"""

from .uuCommon import (uuRestMethod, repeat_letter, convert_to_str, convert_to_dict, timestamp,
                       dict_path_exists, dict_get_item_by_path, raise_exception, duplicate_dict)
from .uuCommand import uuCommand, uuDataType, get_data_type
from typing import List, Dict


def _get_example_str() -> str:
    return "https://pypi.org/project/uurest/"


def _is_valid_method(method: str) -> bool:
    method = method.upper()
    if method == "GET":
        return True
    if method == "POST":
        return True
    if method == "OPTIONS":
        return True
    if method == "PUT":
        return True
    if method == "DELETE":
        return True
    return False


def _fetch_prepare_params(url: str, request_body: str or Dict or None = None, setup: dict = None):
    """
    Returns url, method, body and setup from chrome fetch
    :return:
    """
    # check url
    if url is None or not isinstance(url, str):
        raise Exception(f'url must be string')

    # get setup
    if setup is None:
        setup = fetch_setup(duplicate=True)

    # solve the case when only url is specified
    if request_body is None:
        return url, "GET", None, setup

    # solve the case when only url is specified
    if isinstance(request_body, str):
        return url, "GET", request_body, setup

    if isinstance(request_body, dict):
        request = convert_to_dict(request_body)
        if "body" not in request.keys():
            raise Exception(f'Parameter "body" must exist in the request_body but it is not.\n{str(request)}. '
                            f'If the first argument of the "fetch" fuction is a string (which is the case) '
                            f'the second argument must be either null or a dictionary containing "body" element '
                            f'for example "body": null, or "body": "some json".\n\nIt is assumed the "fetch" function was copied'
                            f'from chrome browser using "copy as fetch" item in the network popup menu. See {_get_example_str()}')
        else:
            # now request body is either json or str
            request_body = request["body"]
        # process body from chrome fetch
        if request_body is not None:
            temp_body = convert_to_dict(request_body)
            temp_body_data_type = get_data_type(temp_body)
            # if body is json then set body as dict
            if temp_body_data_type == uuDataType.__json__:
                request_body = temp_body
            # otherwise if body is not a str then raise exception
            elif temp_body_data_type !=uuDataType.__text__:
                raise Exception(f'Unknown data type of "body" element in "request_body" parameter.')
        # get method
        if "method" not in request.keys():
            raise Exception(f'Parameter "method" must exist in the request_body but it is not.\n{str(request)}. '
                            f'If the first argument of the "fetch" fuction is a string (which is the case) '
                            f'the second argument must be either null or a dictionary containing "method" element '
                            f'for example "method": "GET", or "method": "POST".\n\nIt is assumed the "fetch" function was copied'
                            f'from chrome browser using "copy as fetch" item in the network popup menu. See {_get_example_str()}')
        method = request["method"]
        if not _is_valid_method(method):
            raise_exception(f'Method "{method}" is not a valid http method. Try to use "GET" or "POST".')
        # switch headers
        if "headers" in request.keys():
            setup["http_headers"] = request["headers"]
        # else:
        #     headers = {}
        # setup["http_headers"].update(headers)
        return url, method, request_body, setup
    raise Exception(f"fetch was called using invalid combination of arguments. See {_get_example_str()}")


# null is typically used in the fetch export
null = None


globals()["fetch_setup_global_vars"] = {
    # Will raise exception if error occurs. Default value is True. Default value can be modified using fetch_global_setup(...)
    "raise_exception_on_error": True,
    # timeout: How long to wait for the http, https response. Default value is 120. Default value can be modified using fetch_global_setup(...)
    "timeout": 120,
    # if verbose is true then fetch will automatically print out result into the console output
    "verbose": True,
    # following http headers will be sent during fetch request
    "http_headers": {
        "accept": "*/*;q=0.9",
        "accept-language": "*;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "priority": "u=1",
        "sec-ch-ua-mobile": "?0"
    }
}


# def fetch_setup(raise_exception_on_error: bool or None = None, timeout: int or None = None, verbose: bool or None = None):
def fetch_setup(duplicate: bool = False):
    """
    Gets a copy of fetch setup dictionary
    :return:
    """
    result = globals()["fetch_setup_global_vars"]
    if duplicate:
        result = duplicate_dict(result)
    return result


def call(url: Dict or str, method: str or None = None, body: Dict or str or None = None, setup: Dict = None) -> uuCommand:
    # check parameters
    if method is None and body is None:
        method = "GET"
    if method is None and body is not None:
        method = "POST"
    if not isinstance(method, str):
        raise Exception(f'argument "method" must be a string but it is type of "{str(type(method))}"')
    if body is not None and not isinstance(body, dict) and not isinstance(body, str):
        raise Exception(f'argument "body" must be a dict or str or None but it is type of "{str(type(body))}"')
    if setup is None:
        setup = fetch_setup(duplicate=True)
    if not isinstance(setup, dict):
        raise Exception(f'argument "setup" must be a dict but it is type of "{str(type(body))}"')
    # if verbose then print header
    if setup["verbose"]:
        verbose_message = ""
        arguments = {"url": url, "method": method, "body": body, "setup": setup}
        verbose_message += repeat_letter(value=f' call ')
        verbose_message += repeat_letter(value=f' INPUTS ', letter='-')
        verbose_message += repeat_letter(value=f' {timestamp()} ', letter='-')
        verbose_message += convert_to_str(arguments, formatted=True) + "\n"
        print(verbose_message)
    # call command
    result = uuCommand(url=url, method=method, request_body=body, setup=setup)
    # if verbose then print result
    if setup["verbose"]:
        verbose_message = ""
        verbose_message += repeat_letter(value=f' HTTP_RESPONSE_STATUS ', letter='-')
        verbose_message += repeat_letter(value=f' {timestamp()} ', letter='-')
        http_response_status = {
            "http_status_code": result.http_status_code,
            "content_type": result.content_type,
            "data_type": result.data_type
        }
        verbose_message += convert_to_str(http_response_status, formatted=True) + "\n"
        verbose_message += repeat_letter(value=f' HTTP_RESPONSE_CONTENT ', letter='-')
        verbose_message += repeat_letter(value=f' {timestamp()} ', letter='-')
        verbose_message += str(result) + "\n"
        verbose_message += repeat_letter(f' HINT ', "-")
        verbose_message += f'# Use "fetch_setup()[\'verbose\'] = False" to stop console output\n'
        print(verbose_message)
    return result


def fetch(url: Dict or str, body: Dict or None = None, setup: Dict = None) -> uuCommand:
    """
    Calls rest api url and returns response.
    Fetch command is typically copied directly from the Chrome browser
    :param url: Contains url string or dictionary (json) containing url, method and optionally a token for example {"url": "...", "method": "POST", "token": "..."}
    :param method: "GET" or "POST"
    :param body:
    :param setup:
    :return:
    """
    new_url, new_method, new_body, new_setup = _fetch_prepare_params(url=url, request_body=body, setup=setup)
    # if verbose then print info
    if new_setup["verbose"]:
        verbose_message = ""
        arguments = {"url": url, "body": body, "setup": setup}
        verbose_message += repeat_letter(value=f' fetch ')
        verbose_message += repeat_letter(value=f' INPUTS ', letter='-')
        verbose_message += repeat_letter(value=f' {timestamp()} ', letter='-')
        verbose_message += convert_to_str(arguments, formatted=True) + "\n"
        verbose_message += repeat_letter(value=' TRIGGERING CALL(...) ', letter='-')
        verbose_message += f"Triggering \"call\" function. fetch() is always translated to call()\n"
        print(verbose_message)
    result = call(url=new_url, method=new_method, body=new_body, setup=new_setup)
    return result


def translate_fetch(url: str, body: Dict or None) -> str:
    """
    Translate fetch command into call command and print generated source code
    :param url:
    :param body:
    :return:
    """
    url, method, body, setup = _fetch_prepare_params(url=url, request_body=body)
    result = ""
    result += f'url = "{url}"\n'
    result += f'method = "{method}"\n'
    result += f'body = {convert_to_str(body, formatted=True)}\n'
    result += f'setup = {convert_to_str(setup, formatted=True)}\n'
    result += f'response = call(url, method, body, setup)\n'
    return result


# def smart_translate_fetch(url: str, request_body: Dict or None):
#     """
#     Translate fetch command into call command and print generated source code
#     :param url:
#     :param request_body:
#     :param raise_exception_on_error:
#     :param timeout:
#     :return:
#     """
#     url, method, body, setup = _fetch_prepare_params(url=url, request_body=request_body)
#     # setup authorization_required
#     authorization = None
#     if "Authorization" in setup["http_headers"].keys():
#         authorization = setup["http_headers"]["Authorization"]
#     result = ""
#     if payload is None and method == "GET" and authorization is None:
#         result += f'response = fetch(url="{url}")\n'
#     elif payload is None and method == "GET" and authorization is not None:
#         result += f'setup = fetch_setup(duplicate=True)\n'
#         result += f'setup["http_headers"].update({convert_to_str(authorization)})\n'
#         result += f'response = fetch(url="{url}", setup=setup)\n'
#     elif payload is None and method != "GET" and authorization is None:
#         result += f'response = fetch(url="{url}", method="{method}")'
#     elif payload is None and method != "GET" and authorization is not None:
#         result += f'setup = fetch_setup(duplicate=True)\n'
#         result += f'setup["http_headers"].update({convert_to_str(authorization)})\n'
#         result += f'response = fetch(url="{url}", method="{method}", setup=setup)\n'
#     elif payload is not None and authorization is None:
#         result += f'payload = {convert_to_str(payload, formatted=True)}\n'
#         result += f'response = fetch(url="{url}", method="{method}", payload=payload)\n'
#     elif payload is not None and authorization is not None:
#         result += f'setup = fetch_setup(duplicate=True)\n'
#         result += f'setup["http_headers"].update({convert_to_str(authorization)})\n'
#         result += f'payload = {convert_to_str(payload, formatted=True)}\n'
#         result += f'response = fetch(url="{url}", method="{method}", payload=payload, setup=setup)\n'
#     else:
#         result += f'url = "{url}"\n'
#         result += f'method = "{method}"\n'
#         result += f'payload = {convert_to_str(payload, formatted=True)}\n'
#         result += f'setup = {convert_to_str(setup, formatted=True)}\n'
#         result += f'response = fetch(url, method, payload, setup)\n'
#     if fetch_setup()["verbose"]:
#         print(f'# ----------------------------------------')
#         print(f'# ------------ beautify_fetch ------------')
#         print(result)
#         print(f'# ----------------------------------------')
#     return result
