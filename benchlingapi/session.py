import requests
from benchlingapi.exceptions import BenchlingAPIException, ModelNotFoundError
import json
from benchlingapi.base import ModelRegistry
from benchlingapi.models import __all__ as allmodels
from benchlingapi.utils import url_build
from functools import partial, wraps


class RequestDecorator(object):
    """
    Wraps a function to raise error with unexpected request status codes
    """
    def __init__(self, status_codes):
        if not isinstance(status_codes, list):
            status_codes = [status_codes]
        self.code = status_codes

    def __call__(self, f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):
            r = f(*args, **kwargs)
            if r.status_code not in self.code:
                http_codes = {
                    400: "BAD REQUEST",
                    403: "FORBIDDEN",
                    404: "NOT FOUND",
                    500: "INTERNAL SERVER ERROR",
                    503: "SERVICE UNAVAILABLE",
                    504: "SERVER TIMEOUT"}
                msg = ""
                if r.status_code in http_codes:
                    msg = http_codes[r.status_code]
                    msg += f"\nrequest: {r.request}"
                    msg += f"\nurl: {r.request.path_url}"
                    msg += f"\nresponse: {r.text}"
                raise BenchlingAPIException("HTTP Response Failed {} {}".format(
                    r.status_code, msg))
            return r.json()

        return wrapped_f


class Http(object):
    TIMEOUT = 30
    HOME = 'https://benchling.com/api/v2'
    NEXT = "nextToken"

    def __init__(self, api_key):
        session = requests.Session()
        session.auth = (api_key, '')
        self.__session = session
        self.post = RequestDecorator([200, 201, 202])(partial(self.request, "post"))
        self.get = RequestDecorator(200)(partial(self.request, "get"))
        self.delete = RequestDecorator(200)(partial(self.request, "delete"))
        self.patch = RequestDecorator([200, 201])(partial(self.request, "patch"))

    def request(self, method, path, timeout=None, action=None, **kwargs):
        if timeout is None:
            timeout = self.TIMEOUT
        if action is not None:
            path += ":" + action
        return self.__session.request(method, url_build(self.HOME, path), timeout=timeout, **kwargs)

    def get_pages(self, path, timeout=None, action=None, **kwargs):
        get_response = partial(self.get, path, timeout=timeout, action=action)

        response = get_response(**kwargs)

        while response is not None:
            yield response

            next = response.get(self.NEXT, None)

            # update params with nextToken
            params = kwargs.get(self.NEXT, {})
            params.update({self.NEXT: next})
            kwargs["params"] = params

            if next is not None:
                response = get_response(**kwargs)
            else:
                response = None


class Session(object):

    def __init__(self, api_key):
        self.__http = Http(api_key)
        self.__interfaces = {}
        for model_name in allmodels:
            model_cls = ModelRegistry.get_model(model_name)
            nmspc = {"session": self}
            # if model_cls.blacklist is not None:
            #     for blacklisted_method in model_cls.blacklist:
            #         nmspc[blacklisted_method] = None
            mymodel = type(model_name, (model_cls,), nmspc)
            setattr(self, model_name, mymodel)
            self.__interfaces[model_name] = mymodel

    @property
    def http(self):
        return self.__http

    @property
    def url(self):
        return self.__http.HOME

    @property
    def models(self):
        return list(ModelRegistry.models.keys())

    def set_timeout(self, timeout_in_seconds):
        self.__http.timeout = timeout_in_seconds

    @property
    def interfaces(self):
        return self.__interfaces

    def interface(self, model_name):
        if model_name not in self.interfaces:
            raise ModelNotFoundError("No model by name of \"{}\"".format(model_name))
        return self.interfaces[model_name]