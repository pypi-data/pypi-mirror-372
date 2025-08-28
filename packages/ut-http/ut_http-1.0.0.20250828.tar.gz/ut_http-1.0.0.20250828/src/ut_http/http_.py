from typing import Any

import warnings
from http.client import HTTPSConnection
import socket

from ut_log.log import Log, LogEq
from ut_obj.str import Str
from ut_dic.douri import DoUri

TyDic = dict[Any, Any]
TyDoUri = dict[Any, str]
TyHeaders = dict[str, Any | str | int]
TyStr = str
TyUri = str

TnAny = None | Any
TnDic = None | TyDic
TnDoUri = None | TyDoUri
TnHeaders = None | TyHeaders
TnStr = None | TyStr
TnUri = None | TyUri

warnings.filterwarnings("ignore")


class Client:

    @staticmethod
    def get(**kwargs) -> TnDic:
        m_data: TnDic = None
        d_uri: TnDoUri = kwargs.get('d_uri')
        if not d_uri:
            return m_data
        headers: TnHeaders = kwargs.get('headers')
        if headers is None:
            return m_data
        authority: TnStr = d_uri.get('authority')
        if authority is None:
            return m_data
        params = kwargs.get('params')
        _uri: TyUri = DoUri.sh_uri_for_get(d_uri, params)
        data = kwargs.get('data')
        try:
            connection = HTTPSConnection(authority, timeout=10)
            LogEq.debug("data", data)
            LogEq.debug("headers", headers)
            LogEq.debug("d_uri", d_uri)
            connection.request("GET", _uri, data, headers)
            response = connection.getresponse()
            _data = response.read()
            d_data: TyDic = Str.sh_dic(_data)
            m_data = d_data
            connection.close()
            LogEq.debug("d_data", d_data)
        except socket.timeout:
            Log.error("connection's timeout: 10 expired")
            raise
        except Exception:
            raise
        return m_data
