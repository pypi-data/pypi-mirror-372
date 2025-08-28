import warnings

from ut_com.com import Com
from ut_log.log import LogEq

from ut_http.http_ import Client as Http_Client
from ut_http.requests_ import Request as Request_Request
from ut_http.requests_ import Session as Request_Session
from ut_http.urllib3_ import Request as Urllib3_Request

warnings.filterwarnings("ignore")


class Uri:
    """ Manage uri's
    """
    @staticmethod
    def dispatch_get(httpmod):
        match Com.App.httpmod:
            case "H_C":
                return Http_Client.get
            case "U3_R":
                return Urllib3_Request.get
            case "R_R":
                return Request_Request.get
            case "R_S":
                return Request_Session.get
            case _:
                return Request_Session.get

    @classmethod
    def get(cls, **kwargs):
        get_ = cls.dispatch_get(Com.App.httpmod)
        content = get_(**kwargs)
        LogEq.debug('content', content)
        return content
