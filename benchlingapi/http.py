import requests
from benchlingapi.exceptions import BenchlingAPIException
import json
import inflection
from benchlingapi.base import ModelInterface


def url_build(*parts):
    """Join parts of a url into a string"""
    return '/'.join(p.strip('/') for p in parts)


class RequestDecorator(object):
    """
    Wraps a function to raise error with unexpected request status codes
    """
    def __init__(self, status_codes):
        if not isinstance(status_codes, list):
            status_codes = [status_codes]
        self.code = status_codes

    def __call__(self, f):
        def wrapped_f(*args, **kwargs):
            r = f(*args)
            if r.status_code not in self.code:
                http_codes = {
                    403: "FORBIDDEN",
                    404: "NOT FOUND",
                    500: "INTERNAL SERVER ERROR",
                    503: "SERVICE UNAVAILABLE",
                    504: "SERVER TIMEOUT"}
                msg = ""
                if r.status_code in http_codes:
                    msg = http_codes[r.status_code]
                raise BenchlingAPIException("HTTP Response Failed {} {}".format(
                    r.status_code, msg))
            return json.loads(r.text)

        return wrapped_f



class AqHTTP(object):

    TIMEOUT = 10

    def __init__(self, apikey, home='https://api.benchling.com/v1/'):
        session = requests.Session()
        session.auth = apikey
        self._session = session
        self.home = home

    def request(self, method, path, timeout=None, **kwargs):
        if timeout is None:
            timeout = self.TIMEOUT
        return self._session.request(method, url_build(self.home, path), timeout=timeout, **kwargs)

    @RequestDecorator([200, 201, 202])
    def post(self, path, json_data=None):
        if json_data is None:
            json_data = {}
        return self.request("post", path, json_data=json_data)

    @RequestDecorator(200)
    def get(self, path):
        return self.request("get", path)

    @RequestDecorator(200)
    def delete(self, path):
        return self.request("delete", path)

    @RequestDecorator([200, 201])
    def patch(self, path, json_data=None):
        if json_data is None:
            json_data = {}
        return self.request("patch", path, json_data=json_data)

    def model_interface(self, model_name):
        return ModelInterface(model_name, self)




class ModelBase(object, metaclass=ModelRegistry):

    def __init__(self):
        self.http = None
        self.data = None

    @classmethod
    def path(cls):
        name = inflection.underscore(cls.__name__)
        name = inflection.dasherize(name)
        name = inflection.pluralize(name)
        return name

    @classmethod
    def all(cls, http):
        return http.post(cls.path())
    
    @classmethod
    def find(cls, http, model_id):
        return http.get(f"{cls.path()}/{model_id}")

    @classmethod
    def delete(cls, http, model_id):
        return http.delete(f"{cls.path()}/{model_id}")

    @classmethod
    def create(cls, http, json_data):
        return http.post(f"{cls.path()}", json_data=json_data)







