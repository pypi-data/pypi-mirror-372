
from typing import Any, TypeAlias

import warnings
import requests
import requests.models
import xmltodict

from ut_com.com import Com
from ut_com.log import Log
from ut_dic.douri import DoUri

import ut_http.utils as ut

warnings.filterwarnings("ignore")

TyResponse: TypeAlias = requests.models.Response
TyContent = str
TnContent = None | TyContent
TyArr = list[Any]
TyDoS = dict[Any, str]
TyDic = dict[Any, Any]
TyUri = str
TyDoUri = dict[Any, TyUri]
TyStr = str

TnDic = None | TyDic
TnStr = None | TyStr


class Response:

    @staticmethod
    def sh_d_content_type(response: TyResponse) -> TyDic:
        content = response.headers['Content-Type']
        a_content: TyArr = content.split(';')
        d_content_type: TyDoS = {}
        if len(a_content) > 0:
            d_content_type['content_type'] = a_content[0].strip()
        if len(a_content) > 1:
            d_content_type['charset'] = a_content[1].strip()
        Log.Eq.debug("resp.headers", response.headers)
        Log.Eq.debug("d_content_type", d_content_type)
        return d_content_type

    @classmethod
    def sh_content(cls, response: TyResponse) -> Any | TnStr:
        d_content_type: TyDic = cls.sh_d_content_type(response)
        Log.Eq.debug("d_content_type", d_content_type)
        match d_content_type['content_type']:
            case 'application/json':
                return response.json()
            case 'text/plain':
                return response.text
            case 'text/xml':
                return xmltodict.parse(response.text)
            case 'text/html':
                return response.text
            case _:
                return None


class Uri:

    @staticmethod
    def sh(uri: TnStr, **kwargs) -> TyStr:
        if uri is None:
            d_uri: TyDoUri = kwargs.get('d_uri', {})
            Log.Eq.debug("d_uri", d_uri)
            uri = DoUri.sh_uri(d_uri)
            Log.Eq.debug("uri", uri)
        return uri


class Kw:

    @staticmethod
    def sh(**kwargs) -> TyDic:
        params: TnDic = kwargs.get('params')
        data = kwargs.get('data')
        headers: TnDic = kwargs.get('headers')
        auth = kwargs.get('auth')

        Log.Eq.debug("auth", auth)
        Log.Eq.debug("params", params)
        Log.Eq.debug("data", data)
        Log.Eq.debug("headers", headers)

        kw = {}
        if data is not None:
            kw['data'] = data
        if params is not None:
            kw['params'] = params
        if headers is not None:
            kw['headers'] = headers
        if auth is not None:
            kw['auth'] = auth
        Log.Eq.debug("kw", kw)
        return kw


class Session:

    @staticmethod
    def get(uri: TnStr = None, **kwargs) -> TnContent:
        _uri: TyStr = ut.sh_uri(uri, **kwargs)
        content: TnContent = None
        kw: TyDic = Kw.sh(**kwargs)
        try:
            if 'session' not in Com.App.reqs:
                Com.App.reqs['session'] = requests.Session()
            _session = Com.App.reqs['session']
            response: TyResponse = _session.get(_uri, **kw)
            response.raise_for_status()
            Log.Eq.debug("resp", response)
            Log.Eq.debug("resp.headers", response.headers)
            content = Response.sh_content(response)
        except requests.exceptions.HTTPError as exc:
            content = None
            # Need to check its an 404, 503, 500, 403 etc.
            status_code = exc.response.status_code
            Log.Eq.debug("exc.response.status_code", status_code)
            Log.warning(exc, exc_info=True)
        except Exception:
            # Log.error(e, exc_info=True)
            raise
        Log.Eq.debug("content", content)
        return content


class Request:

    @staticmethod
    def get(uri: TnStr = None, **kwargs) -> TnContent:
        _uri: TyStr = ut.sh_uri(uri, **kwargs)
        kw: TyDic = Kw.sh(**kwargs)
        try:
            response: TyResponse = requests.get(_uri, **kw)
            Log.Eq.debug("kw", kw)
            Log.Eq.debug("response", response)
            Log.Eq.debug("response.headers", response.headers)
            response.raise_for_status()
            content = Response.sh_content(response)
        except requests.exceptions.HTTPError as exc:
            content = None
            # Need to check its an 404, 503, 500, 403 etc.
            status_code = exc.response.status_code
            Log.Eq.debug("exc.response.status_code", status_code)
            Log.warning(exc, exc_info=True)
        except Exception:
            # Log.error(e, exc_info=True)
            raise
        Log.Eq.debug("Request content", content)
        return content
