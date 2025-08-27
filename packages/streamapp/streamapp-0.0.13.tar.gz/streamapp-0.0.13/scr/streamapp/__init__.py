from streamlit import connection
from .snow_class import SnowConnection
from .auth.authenticator import Auth
from .enviroment_selector import EnvironmentSelector
from .report_generator import ReportGenerator, InMemoryZip
from .auth.roles import Roles
from .cards import Card
from .validators import BaseValidator
from .requests import BaseRequest
from .subpages import SubPages
from functools import wraps


class Conn:

    @property
    def connection(cls):
        return connection('snow', type=SnowConnection)

    @property
    def query(cls):
        return connection('snow', type=SnowConnection).query

    @property
    def query_async(cls):
        return connection('snow', type=SnowConnection).query_async

    @property
    def get_async_results(cls):
        return connection('snow', type=SnowConnection).get_async_results


class Authenticator:
    auth = None

    def _checker(func):
        @wraps(func)
        def wrapper(cls, *args, **kwargs):
            if cls.auth is None:
                cls.auth = Auth()
            return func(cls, *args, **kwargs)
        return wrapper

    @property
    @_checker
    def login(cls):
        return cls.auth.login

    @property
    @_checker
    def user_page(cls):
        return cls.auth.user_page

    @property
    @_checker
    def admin_page(cls):
        return cls.auth.admin_page


conn = Conn()
auth = Authenticator()
setattr(BaseValidator, 'conn', conn)

__all__ = [
    'EnvironmentSelector',
    'ReportGenerator',
    'Roles',
    'Card',
    'BaseRequest',
    'utils',
    'BaseValidator',
    'InMemoryZip',
    'SubPages'
]
