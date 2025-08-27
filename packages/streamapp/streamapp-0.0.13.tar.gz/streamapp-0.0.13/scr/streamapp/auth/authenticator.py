"""Custom handler for streamlit Authenticator.

Login class to handle the login and logout from
streamlit authenticator, checking for password and
setting up the roles to acces specifict pages.
Streamlit Authenticator: https://blog.streamlit.io/streamlit-\
    authenticator-part-1-adding-an-authentication-component-to-your-app/

Usage:
    from streamapp import auth
    `in the begining of your app file after set_page_config`
    auth.login(['admin', 'role1', 'role2'])
"""

from streamlit import (
    secrets, connection, error, session_state, warning, stop,
    sidebar, caption, toast, rerun
)
from streamlit_authenticator import Authenticate, LoginError
from logging import info as log_info
from yaml.loader import SafeLoader
from yaml import load
from typing import Optional, Callable
from .roles import Roles
from .mongo_auth import MongoAuth
from .user_panel import UserControlUi


class Auth(UserControlUi):
    """Custom Login handler for streamlit authenticator.

    type: class callable

    This custom login handler checks for hashed password and
    sets up the roles to acces specifict pages.

    toml file:
        [credentials.usernames]
        Pepe.name = 'pepe@gmail.com'
        Pepe.roles = ['admin']
        Pepe.password = '$2b$12$6E4nrCcqA...'

    """
    def __init__(self) -> None:
        """Initialize clas and super class UserUi"""
        super().__init__()
        self()

    def __call__(self) -> None:
        """Check for valid credentials from secrets file"""
        session_state.authentication_status = None
        try:
            if secrets.get('mongo_auth'):
                self.conn = connection('auth', MongoAuth)
                self._update_mongo_credentials()
                log_info('Logging with Mongo DB')
            else:
                self.conn = None
                with open('.streamlit/config.yaml') as file:
                    __credentials = load(file, Loader=SafeLoader)

                session_state.authenticator = Authenticate(
                    credentials=__credentials['credentials'],
                    cookie_name=__credentials['cookie']['name'],
                    cookie_key=__credentials['cookie']['key'],
                    cookie_expiry_days=__credentials['cookie']['expiry_days']
                )
                log_info('Logging with Config file')
        except (TypeError, FileNotFoundError):
            error('Invalid App credentials')
            stop()
        except KeyError:
            session_state.authentication_status = None
            warning('Try again something went wrong')
            stop()
        except AttributeError:
            error('There is no credentials setted up')
            stop()

    def _update_mongo_credentials(self):
        """Check for changes in credentials for Mongo Auth method

        Refresh the authenticator with the latest credentials info
        in Mongo database.

        Args:
            None

        Returns:
            None
        """
        __credentials = {
            'usernames': {
                x['username']: x for x in self.conn.get_users()
            },
        }
        session_state.authenticator = Authenticate(
            credentials=__credentials,
            cookie_name=secrets
            .get('auth_cookie', dict())
            .get('cookie_name', 'cokkie'),
            cookie_key=secrets
            .get('auth_cookie', dict())
            .get('cookie_key', 'key=='),
            cookie_expiry_days=secrets
            .get('auth_cookie', dict())
            .get('cookie_expiry_days', 1)
        )
        return None

    def login(self, roles: Optional[list] = None,
              side_bar_widget: Callable = lambda: None) -> None:
        """Login callable to set up session user variables.

        This callable use the .secrets/toml file to get the user
        variables and check for the login and set up roles.

        Args:
            roles: list with the user granted roles

        Return:
            None
        """
        if not session_state.get('authentication_status'):
            try:
                name, status, username = session_state.authenticator.login(
                    location='main',
                    max_login_attempts=3
                )
                if self.conn is None and status:
                    session_state['roles'] = session_state.authenticator\
                        .authentication_handler\
                        .credentials['usernames']\
                        .get(username, dict())\
                        .get('roles', [])
                    session_state['profile_img'] = session_state.authenticator\
                        .authentication_handler\
                        .credentials['usernames']\
                        .get(username, dict())\
                        .get('img', b'')
                elif status:
                    user = self.conn.get_user(name)
                    session_state.roles = user.get('roles', [])
                    session_state.profile_img = user.get('img', b'')
                    del user
                del name, status, username
            except KeyError:
                session_state.authentication_status = None
            except AttributeError:
                self()
            except LoginError:
                admin_contact = secrets.get('admin_contact', '')
                warning(f"""
                # ⛔ Too many attemps
                ---
                Your user has been blocked temporarlly for security
                If after 20 minutes is still blocked contact your admin
                to reset the password {admin_contact}
                """)
        try:
            if session_state.authentication_status:
                self.logout(side_bar_widget)
                Roles.allow_acces(roles)
            elif session_state.authentication_status is False:
                error('Username/password is incorrect')
                stop()
            elif session_state.authentication_status is None:
                warning('Please enter your username and password')
                stop()
        except (AttributeError, KeyError):
            session_state.authentication_status = None
        return

    def logout(self, side_bar_widget: Callable = None) -> None:
        """Logout and delete the session variable for user auth.

        Args:
            None

        Returns:
            None
        """
        session_state.authenticator.logout('Logout', 'sidebar')
        if not session_state.get('authentication_status', False):
            try:
                del session_state.roles
                del session_state.profile_img
                return
            except AttributeError:
                return
        with sidebar:
            if isinstance(side_bar_widget, Callable):
                side_bar_widget()
            caption(f'Welcome **{session_state.name}**')
        return

    def user_page(self):
        """Show a page to update user details.

        Args:
            None

        Returns:
            None
        """
        if self.conn is None:
            error('⛔ No valid option for your login method')
            return
        if session_state.authentication_status:
            response = self.user_panel()

            if response:
                session_state.get(
                    'authenticator'
                ).authentication_handler.execute_logout()
                self._update_mongo_credentials()
                toast('🔄️ Login again to see the changes')
                rerun()
        return

    def admin_page(self):
        """Shows an admin page to update users details.

        Args:
            None

        Returns:
            None
        """
        if self.conn is None:
            error('⛔ No valid option for your login method')
            return
        if session_state.authentication_status:
            response = self.admin_panel()
            if response:
                self._update_mongo_credentials()
        return
