import warnings

import xmltodict
from urllib3 import PoolManager

from ut_log.log import LogEq
from ut_obj.str import Str

warnings.filterwarnings("ignore")


class Content:

    @staticmethod
    def sh(resp):
        data_decoded = resp.data.decode('utf-8')
        LogEq.debug("data_decoded", data_decoded)
        if data_decoded.startswith("<"):
            data = xmltodict.parse(data_decoded)
        elif data_decoded.startswith(("{", "[")):
            data = Str.sh_dic(data_decoded)
        else:
            data = data_decoded
        LogEq.debug("data", data)
        return data


class Request:

    @staticmethod
    def get(**kwargs):
        data = None
        uri = kwargs.get('uri')
        try:
            data = None
            poolmanager = PoolManager()
            resp = poolmanager.request('GET', uri)
            LogEq.debug("resp", resp)
            data = Content.sh(resp)
            LogEq.debug("data", data)
        except Exception:
            # Log.error(e, exc_info=True)
            raise
        return data
