"""Custom request class to build and send http request

Class definition to use send request with body or not,
send multiple reuqest and covert the responses, interacting
with .secrect stremalit file

Usage
    from streamapp import BaseRequest

    class SendRequest(BaseRequest):
        def __init__(self, id: int):
            self.id = id

        def validate_and_send(self):
            ... some validations
            assert validation, 'no validation'
            self.send(
                request_type='get_pockemon',  # defined in .secrets
                include_in_url=str(1)
            )
"""

from streamlit import session_state, secrets, toast
from requests import get, post, put, patch
from requests.exceptions import MissingSchema, ConnectionError
from pydantic._internal._model_construction import ModelMetaclass
from typing import Optional
from itertools import cycle
from json import loads, JSONDecodeError, dumps
from .enviroment_selector import EnvironmentSelector


class BaseRequest:
    """Class definition to send http request
    It supports single and multiple sends, and supports the
    `get`, `post`, 'patch`, and `put` methods.
    """

    methods = {
        'get': get,
        'post': post,
        'put': put,
        'patch': patch
    }
    headers = {
        'Content-Type': 'application/json'
    }

    def __init__(self) -> None:
        """Init class."""
        self.__response = []
        self.__redirection = []
        self.__error = []
        self.__mult_responses = []

    @staticmethod
    def __get_url(request_type: str, include: str = '') -> str:
        """Look up for environment or host url and the request
        type defined in.secrets file

        Args:
            request_type: name of request variable in .secrects
            include: parameter to include at the end of url

        Returns
            The complete url with environment host and request variable
            if not found request variable return request_type string.
        """
        if session_state.get('environment_url') is None:
            session_state.environment_url = EnvironmentSelector.environments[
                list(EnvironmentSelector.environments.keys())[0]
            ].get('url', '')
        microservice = session_state.get('environment_url', '')
        url = secrets.REQUESTS.get(request_type).get('url', request_type)
        return microservice + url + include

    @staticmethod
    def __method(request_type: str) -> str:
        """Look up for method defined in .secrets for the request_type

        Args:
            request_type: name of request variable in .secrects

        Returns
            The string method to send the request.
        """
        return secrets.REQUESTS.get(request_type).get('method')

    @classmethod
    def __send_json(cls, body: ModelMetaclass, url: str,
                    request_type: str,
                    headers: dict = {}) -> object:
        """Send a json body request.

        Args:
            body: a json type body for the request
            url: the url to send the request
            request_type: name of request variable in .secrects
            headers: headers to include in request

        Returns
            The request reponse object
        """
        response = cls.methods.get(cls.__method(request_type), 'get')(
            url=url,
            headers=cls.headers | headers,
            data=dumps(body.model_dump(mode='json'), ensure_ascii=True)
        )
        return response

    @classmethod
    def __send_url(cls, url: str, request_type: str,
                   headers: Optional[dict] = None) -> object:
        """Send a simple url request.

        Args:
            url: the url to send the request
            request_type: name of request variable in .secrects
            headers: headers to include in request


        Returns
            The request reponse object
        """
        response = cls.methods.get(cls.__method(request_type), 'get')(
            url=url,
            headers=headers
        )
        return response

    def send(self, request_type: str, body: Optional[dict] = None,
             include_in_url: str = '', is_json: bool = False,
             message: str = '', headers: dict = {}) -> list | dict:
        """Send a request.

        Args:
            request_type: name of request variable in .secrects
            body: a json type body for the request
            include_in_url: str to inclde as url parameter
            is_json: send a json body request
            message: message to return in a toast
            headers: headers to include in request

        Returns
            The request's response loaded from json schema.
        """
        try:
            url = self.__get_url(request_type, include=include_in_url)
            if is_json:
                response = self.__send_json(
                    body=body,
                    request_type=request_type,
                    url=url,
                    headers=headers
                )
            else:
                response = self.__send_url(
                    request_type=request_type,
                    url=url,
                    headers=headers
                )
        except MissingSchema:
            toast('Invalid host', icon='❌')
            return ['Invalid host']
        except AttributeError:
            toast('No request found', icon='❌')
            return ['No request found']
        except ConnectionError:
            toast('No connection to host', icon='❌')
            return ['No connection to host']
        else:
            content = self.__response_handler(response.content)
            if 100 <= response.status_code < 300:
                toast('Success ' + message, icon='✅')
            elif 300 <= response.status_code < 400:
                toast('Redirection ' + message, icon='🔀')
            else:
                toast(f'Error {response.status_code} ' + message, icon='⛔')
            return content

    def send_multiple(self, request_type: str,
                      include_in_url: list[str] = [''],
                      bodies: list[Optional[dict]] = [None],
                      is_json: bool = False,
                      headers: dict = {}) -> list:
        """Send multiple request.

        Args:
            request_type: name of request variable in .secrects
            bodies: list of json bodies for the request
            include_in_url: list of url parameters
            is_json: send a json body request

        Returns
            list of responses.
        """
        try:
            max_test = max(len(include_in_url), len(bodies))
            min_test = min(len(include_in_url), len(bodies))
            assert max_test/min_test in (1, max_test), \
                'Invalid convination in bodies and url`s endings'
        except AssertionError as e:
            return [e]

        if len(bodies) < len(include_in_url):
            req = zip(cycle(bodies), include_in_url)
        elif len(bodies) > len(include_in_url):
            req = zip(bodies, cycle(include_in_url))
        else:
            req = zip(bodies, include_in_url)

        responses = []
        for n, request in enumerate(req, 1):
            responses.append(
                self.send(
                    request_type=request_type,
                    body=request[0],
                    include_in_url=request[1],
                    is_json=is_json,
                    message=str(n),
                    headers=headers
                )
            )
        return responses

    @staticmethod
    def __response_handler(response: bytes) -> dict:
        """Transform the responses to dict.

        Args:
            response: a request response

        Returns
            A dict with the json response or string response.
        """
        res = response.decode('utf-8')
        try:
            return loads(res)
        except JSONDecodeError:
            return {'response': res}
