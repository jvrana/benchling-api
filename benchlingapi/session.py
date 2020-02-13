r"""
Session (:mod:`benchlingapi.session`)
=====================================

.. currentmodule:: benchlingapi.session

Main entrypoint for the benchling api. To open a session,
use your *Benchling-provided API key*. From there, you
can access the session-enabled models:

.. code-block:: python

    from benchlingapi import Session

    api_key = "asdfe8iunaoerhgoaher"
    session = Session(api_key)
    session.DNASequence
    session.AASequence
    session.Oligo
    session.Registry

If your homespace URL for benchling is different from `https://benchling.com/api/v2`, you may
specify your organization homespace using the `org` parameter, as in
`https://{org}.benchling.com/api/v2/`

.. code-block:: python

    org = "myorganization"
    session = Session(api_key, org=org)

You may also specify the homespace directly:

.. code-block:: python

    home = "https://myorganization.benchling.com/api/v2"
    session = Session(api_key, home=home)

For more information on the models and their methods, see the
:ref:`API model docs <api_models>`
"""
from functools import partial
from functools import wraps
from typing import Any
from typing import Generator
from typing import List
from typing import Type

import requests

from benchlingapi.exceptions import BenchlingAPIException
from benchlingapi.exceptions import exception_dispatch
from benchlingapi.exceptions import ModelNotFoundError
from benchlingapi.models.base import ModelBase
from benchlingapi.models.base import ModelRegistry
from benchlingapi.models.models import __all__ as allmodels
from benchlingapi.utils import un_underscore_keys
from benchlingapi.utils import url_build


class RequestDecorator:
    """Wraps a function to raise error with unexpected request status codes."""

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
                    504: "SERVER TIMEOUT",
                }
                msg = ""
                if r.status_code in http_codes:
                    msg = http_codes[r.status_code]
                    msg += "\nrequest: {}".format(r.request)
                    msg += "\nurl: {}".format(r.request.path_url)
                    msg += "\nresponse: {}".format(r.text)

                e = BenchlingAPIException(
                    "HTTP Response Failed {} {}".format(r.status_code, msg)
                )
                e.response = r
                exception_dispatch(e)
            return r.json()

        return wrapped_f


class Http:
    """Creates and responds to the Benchling server."""

    TIMEOUT = 30  #: default request timeout for the session
    DEFAULT_HOME = (
        "https://benchling.com/api/v2"
    )  #: default home url to use if not provided.
    NEXT = "nextToken"  #: nextToken key for pagination

    def __init__(self, api_key, home=None):
        """

        .. versionchanged:: 2.1.12
            Ad
        :param api_key:
        :param home:
        """
        if home is None:
            home = self.DEFAULT_HOME
        session = requests.Session()
        session.auth = (api_key, "")
        self._home = home
        self.__session = session
        self.post = RequestDecorator([200, 201, 202])(partial(self.request, "post"))
        self.get = RequestDecorator(200)(partial(self.request, "get"))
        self.delete = RequestDecorator(200)(partial(self.request, "delete"))
        self.patch = RequestDecorator([200, 201])(partial(self.request, "patch"))

    def request(
        self, method: str, path: str, timeout: int = None, action: str = None, **kwargs
    ) -> Any:

        if "json" in kwargs:
            kwargs["json"] = un_underscore_keys(kwargs["json"])
        if "params" in kwargs:
            kwargs["params"] = un_underscore_keys(kwargs["params"])

        if timeout is None:
            timeout = self.TIMEOUT
        if action is not None:
            path += ":" + action
        return self.__session.request(
            method, url_build(self._home, path), timeout=timeout, **kwargs
        )

    def get_pages(
        self, path: str, timeout: int = None, action: str = None, **kwargs
    ) -> Generator[Any, None, None]:
        get_response = partial(self.get, path, timeout=timeout, action=action)

        response = get_response(**kwargs)

        while response is not None:
            yield response

            # update params with nextToken
            next = response.get(self.NEXT, None)
            kwargs.get("params", {}).update({self.NEXT: next})

            if next:
                response = get_response(**kwargs)
            else:
                response = None


class Session:
    """The session object.

    This serves as the main interface for using the BenchlingAPI.
    """

    def __init__(self, api_key: str, org: str = None, home: str = None):
        """
        Initialize a new Benchling API Session.

        .. versionchanged:: 2.1.12
            Added the `org` and `home` arguments to give users more control
            over homespace.

        :param api_key: Benchling provided api_key
        :param org: optional org name. If provided, sets home URL
            to `https://{home}.benchling.com/api/v2`
        :param home: optional home name. If not provided, sets home
            to `https://benchling.com/api/v2`. See `org` argument.
        """
        if org:
            home = "https://{org}.benchling.com/api/v2".format(org=org)
        self.__http = Http(api_key, home=home)
        self.__interfaces = {}
        for model_name in allmodels:
            model_cls = ModelRegistry.get_model(model_name)
            namespace = {"session": self}
            mymodel = type(model_name, (model_cls,), namespace)
            setattr(self, model_name, mymodel)
            self.__interfaces[model_name] = mymodel

    @property
    def http(self) -> Http:
        """Return the http requester object."""
        return self.__http

    @property
    def url(self) -> str:
        """Return home benchling url."""
        return self.__http._home

    def help(self):
        """Print api documentation url."""
        help_url = "https://docs.benchling.com/reference"
        print('Visit "{}"'.format(help_url))

    @property
    def models(self) -> List[str]:
        """List all models."""
        return list(ModelRegistry.models.keys())

    def set_timeout(self, timeout_in_seconds: int):
        """Set the request timeout."""
        self.__http.timeout = timeout_in_seconds

    @property
    def interfaces(self):
        """List all model interfaces."""
        return self.__interfaces

    def interface(self, model_name) -> Type[ModelBase]:
        """Return a model interface by name."""
        if model_name not in self.interfaces:
            raise ModelNotFoundError('No model by name of "{}"'.format(model_name))
        return self.interfaces[model_name]
