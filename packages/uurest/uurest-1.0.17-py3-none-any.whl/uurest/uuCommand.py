"""

uuRest
===================================

Implementation of the Command structure used in rest API
by most Unicorn applications

"""

from .uuCommon import (uuRestMethod, escape_text, convert_to_str, convert_to_dict,
                       repeat_letter, uuDict, raise_exception, timestamp)
from .uuIO import save_json, save_textfile, save_binary
from .multipartEncoder import MultipartEncoder

import math
from enum import Enum
from typing import List, Dict
import base64
import requests
import urllib3
import json
from pathlib import Path


class uuDataType(Enum):
    __error__ = "__error__"
    __text__ = "__text__"
    __base64__ = "__base64__"
    __json__ = "__json__"

    def __str__(self):
        if self == uuDataType.__json__:
            return "__json__"
        elif self == uuDataType.__error__:
            return "__error__"
        elif self == uuDataType.__text__:
            return "__text__"
        elif self == uuDataType.__base64__:
            return "__base64__"
        else:
            return "UNKNOWN"


# class uuContentType(Enum):
#     TEXT_PLAIN = "text/plain"
#     APPLICATION_JSON = "application/json"
#     APPLICATION_ZIP = "application/zip"
#     APPLICATION_OCTET_STREAM = "application/octet-stream"
#     MULTIPART_FORM_DATA = "multipart/form-data"
#
#     def __str__(self):
#         if self == uuContentType.APPLICATION_JSON:
#             return "application/json"
#         elif self == uuContentType.APPLICATION_ZIP:
#             return "application/zip"
#         elif self == uuContentType.APPLICATION_OCTET_STREAM:
#             return "application/octet-stream"
#         elif self == uuContentType.MULTIPART_FORM_DATA:
#             return "multipart/form-data"
#         else:
#             return "UNKNOWN"


# class uuCharset(Enum):
#     UTF8 = "utf-8"
#     CP1250 = "cp1250"
#
#     def __str__(self):
#         if self == uuCharset.UTF8:
#             return "utf-8"
#         elif self == uuCharset.CP1250:
#             return "cp1250"
#         else:
#             return "UNKNOWN"

    # def is_error(self) -> bool:
    #     return self == uuDataType.__error__
    #
    # def is_text(self) -> bool:
    #     return self == uuDataType.__text__
    #
    # def is_base64(self) -> bool:
    #     return self == uuDataType.__base64__
    #
    # def is_json(self) -> bool:
    #     return self == uuDataType.__json__

class uuRequest:
    """
    class containing all important http, https request properties
    """
    def __init__(self, command, url: str, method: str, body: dict or str or None, setup: Dict):
        self._command: uuCommand = command
        self.url: str = url
        self._body = body
        self.method = method
        self._setup = setup

    def create_copy(self):
        return uuRequest(command=self._command, url=self.url, method=self.method, body=self._body, setup=self._setup)

    @property
    def body(self) -> uuDict:
        return self._body

    @body.setter
    def body(self, value):
        self._body = convert_to_dict(value)


class uuResponse:
    """
    class containing all important http, https response properties
    """
    def __init__(self, command):
        self._command: uuCommand = command
        self._payload = None
        self.http_status_code = 0
        self.content_type: str = ""

    @property
    def payload_json(self) -> uuDict:
        return self._payload

    @payload_json.setter
    def payload_json(self, value):
        self._payload = convert_to_dict(value)


def _get_response_payload(self, r: requests.Response, charset: str):
    """
    delete
    :param r:
    :param charset:
    :return:
    """
    # try to get response content
    try:
        result = r.content.decode(charset)
    except Exception as err:
        result = {"__error__": f'JSON CONTENT WAS NOT OBTAINED\nException "{type(err)}" was triggered.\n\n{escape_text(str(err))}'}
    return result


def _parse_charset_from_content_type(content_type_value: str) -> str or None:
    content_type_value_lower = content_type_value.lower()
    charset_position = content_type_value_lower.find(f'charset=')
    if charset_position > -1:
        charset_value = content_type_value_lower[charset_position + 8:]
        charset_value += " "
        charset_value = charset_value.split(";")[0]
        charset_value = charset_value.split(",")[0]
        charset_value = charset_value.split(" ")[0]
        return charset_value
    return None


def _get_response_content_type_and_charset(r):
    # sets default response content type
    content_type_value = "application/octet-stream"
    # get content type
    content_type_key = detect_header('Content-Type', r.headers)
    if content_type_key is not None:
        content_type_value = r.headers[content_type_key]
    # get charset
    charset_value = _parse_charset_from_content_type(content_type_value)
    if charset_value is None:
        charset_value = "utf-8"
    return content_type_value, charset_value


def _request_contains_files(request_body: dict or str) -> bool:
    result = False
    if request_body is not None and isinstance(request_body, dict):
        for key, value in request_body.items():
            if str(value).lower().startswith(f'file:///'):
                result = True
                break
    return result


def _get_content_type_of_file(filename: Path) -> str:
    result = 'application/octet-stream'
    extension = filename.resolve().suffix.lower().strip()
    if extension == ".zip":
        result = 'application/zip'
    if extension == ".pdf":
        result = 'application/pdf'
    if extension == ".json":
        result = 'application/json'
    if extension == ".xml":
        result = 'application/xml'
    if extension == ".png":
        result = 'image/png'
    if extension == ".jpg" or extension == ".jpeg":
        result = 'image/jpg'
    return result


def detect_header(key: str, headers: dict) -> str or None:
    """
    Try to find key in headers using case-insensitive way.
    Returns key name if the key is found otherwise returns None
    :param key:
    :param headers:
    :return:
    """
    if key in headers.keys():
        return key
    key = key.lower()
    if key in headers.keys():
        return key
    key = key.upper()
    if key in headers.keys():
        return key
    return None


def update_header(key: str, value: str, headers: dict) -> dict:
    """
    Update headers dictionary adds or updates specific header
    :param key:
    :param value:
    :param headers:
    :return:
    """
    key_name = detect_header(key, headers)
    key = key_name if key_name is not None else key
    headers.update({key: value})
    return headers


def update_multiple_headers(headers_to_be_inserted_or_updated: dict, original_headers: dict) -> dict:
    for key in headers_to_be_inserted_or_updated.keys():
        value = headers_to_be_inserted_or_updated[key]
        update_header(key=key, value=value, headers=original_headers)
    return original_headers


def _http_call_including_files(url: str, method: str, request_body: Dict or json or str or None, setup: Dict):
    # http method must be post
    if method != "POST":
        raise Exception(f'The upload_file_raw function must be called with method parameter set to POST, but it is set to "{str(method)}".')
    # update content-type header
    headers: dict = setup["http_headers"]
    update_header(key="Content-Type", value="multipart/form-data; boundary=X-XXXX-BOUNDARY", headers=headers)
    # get body of the request
    request_body = convert_to_dict(request_body)
    # create form fields
    fields = {}
    for key, value in request_body.items():
        key_str = str(key)
        value_str = str(value)
        # if value is file then load file
        if value_str.lower().startswith(f'file:///'):
            value_str = value_str[len(f'file:///'):]
            # open file
            filename = Path(value_str)
            if not filename.exists():
                raise Exception(f'Cannot load file from "{str(filename)}"')
            pure_filename = filename.stem + ''.join(filename.suffixes)
            f = open(str(filename.resolve()), 'rb')
            file_content_type = _get_content_type_of_file(filename)
            # add new field containing the file
            fields.update({key_str: (pure_filename, f, file_content_type)})
        # else the value must be a string
        else:
            # add new field containing a string
            fields.update({key_str: value_str})
    # upload files
    m = MultipartEncoder(fields)
    data = m.to_string()
    # if verbose then print header
    if setup["verbose"]:
        verbose_message = ""
        arguments = {"url": url, "body": str(data) if data is not None else None, "headers": headers}
        verbose_message += repeat_letter(value=f' HTTP_REQUEST_{method} ', letter='-')
        verbose_message += repeat_letter(value=f' {timestamp()} ', letter='-')
        verbose_message += convert_to_str(arguments, formatted=True) + "\n"
        print(verbose_message)
    # call the server and return the response
    r = requests.post(url, headers=headers, data=data, verify=False, auth=None, timeout=setup["timeout"])
    return r


def _http_call_without_files(url: str, method: str, request_body: Dict or str or None, setup: Dict):
    """

    :param url:
    :param method:
    :param request_headers:
    :param request_body:
    :param setup:
    :return:
    """
    urllib3.disable_warnings()
    # update headers
    headers: dict = setup["http_headers"]
    # detect content type
    content_type_key = detect_header(key="Content-Type", headers=headers)
    # if there is a body and content type is not set then try to determine the content type
    if request_body is not None and content_type_key is None:
        content_type_key = "Content-Type"
        if isinstance(request_body, dict):
            update_header(key=content_type_key, value="application/json", headers=headers)
        elif isinstance(request_body, str):
            update_header(key=content_type_key, value="application/x-www-form-urlencoded", headers=headers)
        else:
            raise_exception("Unknown Content-Type of the request_body. Content-Type header is not set and Fetch is not able to detect the Content-Type automatically")
    # get data
    data = convert_to_str(request_body)
    # check if data are not a part of multipart message if true then encode data
    try:
        content_type_value = headers[content_type_key].lower() if content_type_key is not None else ""
        if content_type_value.find("multipart/form-data") > -1 and content_type_value.find("boundary=") > -1:
            data = data.encode()
    except Exception as err:
        return raise_exception({"__error__": f'Error when encoding data before sending it to the server. '
                                             f'Content-Type header was set to the multipart/form-data '
                                             f'therefore system tries to encode data to binary format '
                                             f'but unfortunatelly something went wrong.'}, setup)
    try:
        # if verbose then print header
        if setup["verbose"]:
            verbose_message = ""
            arguments = {"url": url, "body": str(data) if data is not None else None, "headers": headers}
            verbose_message += repeat_letter(value=f' HTTP_REQUEST_{method} ', letter='-')
            verbose_message += repeat_letter(value=f' {timestamp()} ', letter='-')
            verbose_message += convert_to_str(arguments, formatted=True) + "\n"
            print(verbose_message)
        # call the server and return response
        if method == str(uuRestMethod.POST):
            result = requests.post(url, data=data, verify=False, auth=None, headers=headers, timeout=setup["timeout"])
        elif method == str(uuRestMethod.GET):
            result = requests.get(url, data=data, verify=False, auth=None, headers=headers, timeout=setup["timeout"])
        elif method == str(uuRestMethod.OPTIONS):
            result = requests.options(url, data=data, verify=False, auth=None, headers=headers, timeout=setup["timeout"])
        elif method == str(uuRestMethod.HEAD):
            result = requests.head(url, data=data, verify=False, auth=None, headers=headers, timeout=setup["timeout"])
        elif method == str(uuRestMethod.PUT):
            result = requests.put(url, data=data, verify=False, auth=None, headers=headers, timeout=setup["timeout"])
        elif method == str(uuRestMethod.DELETE):
            result = requests.delete(url, data=data, verify=False, auth=None, headers=headers, timeout=setup["timeout"])
        else:
            return raise_exception({"__error__": f'Unknown method in uuRest._http_call. Currently only GET, POST, '
                                                 f'OPTIONS, HEAD, PUT and DELETE methods are supported.'}, setup)
        return result
    except Exception as err:
        return raise_exception({"__error__": f'Error when calling "{str(url)}" with body "{str(request_body)}" using method "{str(method)}". '
                                             f'Exception "{str(type(err))}" was triggered.\n\n{escape_text(str(err))}'}, setup)


def _http_call(url: str, method: str, request_body: Dict or str or None, setup: Dict) -> dict or None:
    """
    Calls rest api endpoint
    :param url: URL of the REST api endpoint
    :param method: POST or GET
    :param request_headers:
    :param request_body: json body of the request
    :param setup:
    :return:
    """
    if _request_contains_files(request_body):
        r = _http_call_including_files(url=url, method=method, request_body=request_body, setup=setup)
    else:
        r = _http_call_without_files(url=url, method=method, request_body=request_body, setup=setup)
    # test if r is a valid Response
    if type(r) is not requests.Response:
        error_message = {
            "http_code": 504,
            "content_type": None,
            "payload": {"__error__": f'Unknown response type received when calling "{str(url)}" using method "{str(method)}". Server is unreachable.'}
        }
        return raise_exception(error_message, setup)
    # get response content type and charset
    response_content_type, response_charset = _get_response_content_type_and_charset(r)

    # if there was an error then return error message
    if r.status_code < 200 or r.status_code >= 300:
        error_message = {
            "__error__": f'Http/Https error code "{str(r.status_code)}" occured. '
                         f'Cannot process text data when calling "{str(url)}" with body "{convert_to_str(request_body)}" using method "{str(method)}".'
        }
        response_payload = convert_to_dict(r.content, str(response_charset))
        response_payload = {} if response_payload is None else response_payload
        response_payload = {**error_message, **response_payload}
        error_message = {
            "http_code": r.status_code,
            "content_type": response_content_type,
            "payload": response_payload
        }
        return raise_exception(error_message, setup)

    # get payload
    response_payload = convert_to_dict(r.content, str(response_charset))
    # return result
    result = {
        "http_code": r.status_code,
        "content_type": response_content_type,
        "payload": response_payload
    }
    return result


def get_data_type(value: dict) -> uuDataType:
    if isinstance(value, dict):
        keys = list(value.keys())
        if len(keys) < 1:
            return uuDataType.__json__
        elif keys[0] == "__error__":
            return uuDataType.__error__
        elif keys[0] == "__text__":
            return uuDataType.__text__
        elif keys[0] == "__base64__":
            return uuDataType.__base64__
        else:
            return uuDataType.__json__
    return uuDataType.__error__


class uuCommand:
    """

    """
    def __init__(self, url: str, method: str, request_body: dict or str, setup: Dict):
        # create a request
        self._initial_request = uuRequest(command=self, url=url, method=method, body=request_body, setup=setup)
        self.requests: List[uuRequest] = []
        self.responses: List[uuResponse] = []
        self._http_code: int = 0
        self._url: str = url
        self._method: str = method
        self._setup = setup
        self._call()

    @property
    def http_status_code(self) -> int:
        if len(self.responses) > 0:
            return self.responses[-1].http_status_code
        return 0

    @property
    def content_type(self) -> str:
        if len(self.responses) > 0:
            return self.responses[-1].content_type
        return ""

    @property
    def data_type(self) -> uuDataType:
        value = self.json
        return get_data_type(value)

    @property
    def json(self) -> dict:
        result = None
        if len(self.responses) > 0:
            result = self.responses[-1].payload_json
        if result is None:
            result = {"__error__": "Fatal error. Response was not correctly received."}
        return result

    @property
    def text(self) -> str:
        data_type = self.data_type
        if data_type == uuDataType.__text__:
            return self.json["__text__"]
        raise Exception(f'Response data type is not {str(uuDataType.__text__)}, it is {str(data_type)}. '
                        f'Please check property "data_type"')

    @property
    def binary(self) -> bytes:
        data_type = self.data_type
        if data_type == uuDataType.__base64__:
            return base64.b64decode(self.json["__base64__"])
        raise Exception(f'Response data type is not {str(uuDataType.__base64__)}, it is {str(data_type)}. '
                        f'Please check property "data_type"')

    # @property
    # def raw_content(self):
    #     value = self.json
    #     data_type = self.data_type
    #     # return json
    #     if data_type == uuDataType.__json__:
    #         return value
    #     # return plain text
    #     elif data_type == uuDataType.__text__:
    #         return value["__text__"]
    #     # return bytes
    #     elif data_type == uuDataType.__base64__:
    #         return base64.b64decode(value["__base64__"])
    #     # return json with error
    #     else:
    #         return value

    # def save_raw_content(self, filename: str, encoding="utf-8"):
    #     value = self.json
    #     status = self.data_type
    #     # save json
    #     if status == uuDataType.__json__:
    #         save_json(value, filename, encoding=encoding, formatted=False)
    #     # save plain text
    #     elif status == uuDataType.__text__:
    #         save_textfile(value, filename, encoding=encoding)
    #     # save bytes to file
    #     elif status == uuDataType.__base64__:
    #         return save_binary(value, filename)
    #     # save json with error
    #     else:
    #         return save_json(value, filename, encoding=encoding, formatted=False)

    def save_json(self, filename: str, encoding="utf-8"):
        save_json(value=self.json, filename=filename, encoding=encoding)

    def save_text(self, filename: str, encoding="utf-8"):
        save_textfile(value=self.text, filename=filename, encoding=encoding)

    def save_binary(self, filename: str):
        save_binary(value=self.binary, filename=filename)

    def _call(self, new_page_info: dict or None = None):
        # get initial request
        request = self._initial_request.create_copy()
        # if this is a paged call then update request and jump to a proper page
        if new_page_info is not None:
            request.body.update({f'pageInfo': new_page_info})
        # append request to requests
        self.requests.append(request)
        # call the server
        result = _http_call(url=request.url, method=request.method, request_body=request.body, setup=self._setup)
        # process the result
        response = uuResponse(self)
        response.http_status_code = result[f'http_code']
        response.content_type = result[f'content_type']
        response.payload_json = result[f'payload']
        self.responses.append(response)

    def _page_info_list_items_on_a_page(self, list_name) -> int:
        result = 0
        # take the very last response
        if len(self.responses) > 0:
            payload = self.responses[-1].payload_json
            # check if element exists in the response payload
            if list_name in payload.keys():
                if isinstance(payload[list_name], list):
                    # get count of elements on currently displayed page
                    result = len(payload[list_name])
        return result

    def _page_info(self, list_name) -> dict or None:
        """
        Gets a page infor from the response
        :return:
        """
        result = None
        # take the very last response
        if len(self.responses) > 0:
            payload = self.responses[-1].payload_json
            # test if pageInfo exists
            if "pageInfo" in payload.keys():
                result = payload["pageInfo"]
                # check pageSize
                if "pageSize" not in result.keys():
                    raise Exception(f'PageInfo should contain "pageSize". Received following pageInfo: {result}')
                if not isinstance(result["pageSize"], int):
                    raise Exception(f'pageSize located in the pageInfo element must be integer, but it is type of {str(type(result["pageSize"]))}.')
                if result["pageSize"] < 1:
                    raise Exception(f'pageSize located in the pageInfo element must be must be higher than 0. Received following pageInfo: {result}')
                # if there are more items on a page then pageSize - update pageSize
                list_items_count = self._page_info_list_items_on_a_page(list_name)
                # if there is no item with list_name then return none
                if list_items_count < 1:
                    return None
                if result["pageSize"] < list_items_count:
                    result["pageSize"] = list_items_count
                # setup pageIndex
                if "pageIndex" not in result.keys():
                    result.update({"pageIndex": 0})
                # create total if it does not exist
                if "total" not in result.keys():
                    result.update({"total": min(result["pageSize"]-1, list_items_count)})
        return result

    def _items_on_page(self, page_index, start_index_on_page, stop_index_on_page, list_name):
        page_info = self._page_info(list_name=list_name)
        # check if already loaded page is the requested one
        current_page_index = page_info["pageIndex"]
        current_page_size = page_info["pageSize"]
        # if it is not, call the api and download requested page
        if page_index != current_page_index:
            new_page_info = {
                f'pageIndex': page_index,
                f'pageSize': current_page_size
            }
            self._call(new_page_info=new_page_info)
            # verify that requested page was downloaded
            page_info = self._page_info(list_name=list_name)
            current_page_index = page_info["pageIndex"]
            if current_page_index != page_index:
                raise Exception(f'Cannot download page "{page_index}" in _items_on_page.')
        # check that item list is not empty
        if list_name not in self.json:
            return None
        item_list = self.json[list_name]
        # check that start and stop index is in the boundaries
        stop_index_on_page = min(stop_index_on_page, len(item_list))
        if start_index_on_page < 0 or stop_index_on_page < 0 or start_index_on_page >= len(item_list) or start_index_on_page > stop_index_on_page:
            return None
        # yield items
        for i in range(start_index_on_page, stop_index_on_page):
            yield item_list[i]

    def items(self, start_index: int or None = None, stop_index: int or None = None, list_name: str = "itemList"):
        # get page info
        page_info = self._page_info(list_name=list_name)
        # if there are no items on the page then exit immediately
        if page_info is None:
            return
        # get pageSize and total
        page_size = page_info["pageSize"]
        total = page_info["total"]
        # setup start index and stop index
        start_index = 0 if start_index is None else start_index
        stop_index = total if stop_index is None else stop_index
        start_index = total - (-start_index % total) if start_index < 0 else start_index
        stop_index = total - (-stop_index % total) if stop_index < 0 else stop_index
        if start_index > stop_index:
            raise Exception(f'Cannot iterate through items. Start index "{start_index}" is higher than stop index "{stop_index}".')
        # setup start page and stop page
        start_page = math.floor(start_index / page_size)
        stop_page = math.floor(stop_index / page_size)
        # yield values
        for page_index in range(start_page, stop_page + 1):
            start_index_on_page = 0 if page_index != start_page else start_index % page_size
            stop_index_on_page = page_size if page_index != stop_page else stop_index % page_size
            # get items
            items = self._items_on_page(page_index, start_index_on_page, stop_index_on_page, list_name=list_name)
            if items is None:
                return
            # return item
            for item in self._items_on_page(page_index, start_index_on_page, stop_index_on_page, list_name=list_name):
                yield item

    def items_count(self, list_name="itemList") -> int:
        page_info = self._page_info(list_name=list_name)
        if page_info is None:
            return -1
            # raise Exception(f'Cannot resolve items_count. This is not a paged call.')
        total = page_info["total"]
        return total

    def __str__(self):
        result = self.json
        if result is not None:
            result = convert_to_dict(result)
            return json.dumps(result, indent=4, ensure_ascii=False)
        return result
