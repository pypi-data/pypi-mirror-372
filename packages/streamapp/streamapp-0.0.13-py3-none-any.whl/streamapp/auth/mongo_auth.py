"""Custom Mongo DB connection for streamlit authenticator.

Connection class to handle the credentials in a mongo DB database
to use with streamlit authenticator and to handle users.

Usage:
    from streamapp.auth.mongo_auth import MongoAuth
    from streamlit import connection
    mongo_conn = connection('auth', MongoAuth)
    mongo_conn.get_users()
"""

from streamlit import secrets, toast
from streamlit.connections import BaseConnection
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import ServerSelectionTimeoutError
from logging import warning, info


class MongoAuth(BaseConnection):
    """Custom Mongo connection for streamlit authenticator.

    type: class

    This custom connection allows crete and administrate credentials
    to use in streamlit pages.

    toml file:
        [mongo_auth]
        host = 'localhost'
        port = 27017
        username = 'root'
        password = 'example'

        [mongo_conf]
        database = 'credentials_test'
        collection = 'users'

        `to define cookies`
        [auth_cookie]
        cookie_name = 'cookie'
        cookie_key = 'INTJB0EvLz...'
        cookie_expiry_days = 1
    """
    def _connect(self) -> None:
        """Create the Mongo client connection.

        Connects to mongo db with the credentials available
        in .secrets file

        Args:
            None

        Returns:
            None
        """
        try:
            client = MongoClient(**secrets['mongo_auth'])
            self.__check_database(client)
            self.__check_collection()
            return self.collection
        except (ServerSelectionTimeoutError, KeyError):
            warning('Invalid Mongo Auth module credentials')
            self.collection = None
            return

    def __check_database(self, client: MongoClient) -> None:
        """Check if database and collection are defined in secrets.

        Create the database and collection if not defined in secrets.

        Args:
            None

        Return:
            None
        """
        try:
            if secrets.get('mongo_conf'):
                database = client.get_database(
                    secrets['mongo_conf'].get('database')
                )
                self.collection = database.get_collection(
                    secrets['mongo_conf'].get('collection')
                )
            else:
                database = client.credentials
                self.collection = database.users
        except Exception:
            info('Database and collection created by default')
            database = client.credentials
            self.collection = database.users
        finally:
            info(f'connected to database: {database}')
            info(f'connected to collection: {self.collection.name}')
        return

    def __check_collection(self) -> None:
        """Check if collection for users exists.

        Create the collection if does not exists, with user: admin and
        password: admin

        Args:
            None

        Return:
            None
        """
        if not self.get_users():
            self.add_user(
                username='admin',
                name='admin@admin.com',
                password='admin',
                roles=['admin'],
                img=''
            )
            warning("""
                    Not users settled up in the database
                    Create TESTING USER only for development
                    user: admin
                    password: admin
                    """
                    )
        return

    def error_handler(func) -> callable:
        """Decorator to check for connection errors."""
        def wrapper(*args, **kwargs) -> any:
            try:
                return func(*args, **kwargs)
            except ServerSelectionTimeoutError:
                return {}
        return wrapper

    @error_handler
    def add_user(self, username: str, name: str, password: str,
                 roles: list[str], img: bytes = None) -> dict:
        """Add a new user to the database.

        Args:
            username: user name
            name: user email or other unique user identification
            password: hashed user password
            roles: list of user granted roles
            img: bites representation of user profile picture

        Return:
            Dict with user inserted information.
        """
        user = self.get_user(name=name)
        if user is not None:
            return user
        user = self.__get_user_name(username=username)
        if user is not None:
            toast('Username already in use', icon='🚫')
            return user
        user = self.collection.insert_one(
            {
                'username': username,
                'name': name,
                'password': password,
                'roles': roles,
                'img': img
            }
        )
        return user

    @error_handler
    def get_users(self, get_ids: bool = False) -> list:
        """Retrieve all users in the database.

        Args:
            get_ids: Boolean to retrieve the Mongo _id for the users.

        Return:
            List of dicts with users information.
        """
        users = list(self.collection.find({}, {'_id': get_ids}))
        return users

    @error_handler
    def get_user(self, name: str) -> dict:
        """Get specifict user info

        Args:
            name: name for the user to be retrived

        Return:
            Dict with user information or empty
        """
        user = self.collection.find_one(
            {
                'name': name
            }
        )
        return user

    @error_handler
    def __get_user_name(self, username: str) -> dict:
        """Get specifict user info

        Args:
            username: username for the user to be retrived

        Return:
            Dict with user information or empty
        """
        user = self.collection.find_one(
            {
                'username': username
            }
        )
        return user

    @error_handler
    def delete_user(self, name: str) -> None:
        """Delete specifict user info

        Args:
            name: name for the user to be deleted

        Return:
            None
        """
        self.collection.find_one_and_delete(
            {
                'name': name
            }
        )
        return

    @error_handler
    def update_name(self, name: str, new_username: str) -> dict:
        """Update username for an user

        Args:
            name: name for the user to be update
            new_username: new user name to update

        Return:
            Dict with user information updated
        """
        user = self.__get_user_name(username=new_username)
        if user is not None:
            toast('Username already in use', icon='🚫')
            return self.get_user(name=name)
        user = self.collection.find_one_and_update(
            {
                'name': name
            },
            {
                '$set': {
                    'username': new_username
                }
            },
            return_document=ReturnDocument.AFTER
        )
        return user

    @error_handler
    def update_roles(self, name: str, new_roles: list[str]) -> dict:
        """Update roles for specifict user

        Args:
            name: name for the user to be updated
            new_roles: new roles to update

        Return:
            Dict with user information or empty
        """
        user = self.collection.find_one_and_update(
            {
                'name': name
            },
            {
                '$set': {
                    'roles': new_roles
                }
            },
            return_document=ReturnDocument.AFTER
        )
        return user

    @error_handler
    def delete_roles(self, name: str, delete_roles: list[str]) -> dict:
        """Ungrant roles for specifict user

        Args:
            name: name for the user to be updated
            delete_roles: list of roles to be removed

        Return:
            Dict with user information or empty
        """
        user = self.get_user(name=name)
        for i in delete_roles:
            try:
                user['roles'].remove(i)
            except ValueError:
                pass
            except TypeError:
                return user
        new_user = self.update_roles(
            name=name,
            new_roles=user['roles']
        )
        return new_user

    @error_handler
    def grant_roles(self, name: str, new_roles: list[str]) -> dict:
        """Grant roles for specifict user

        Args:
            name: name for the user to be updated
            new_roles: list of roles to be added

        Return:
            Dict with user information
        """
        user = self.get_user(name=name)
        try:
            roles = list(set([*user['roles'], *new_roles]))
        except TypeError:
            return user
        new_user = self.update_roles(
            name=name,
            new_roles=roles
        )
        return new_user

    @error_handler
    def update_password(self, name: str, new_password: str) -> dict:
        """Update password for specifict user

        Args:
            name: name for the user to be updated
            new_password: Hased password to update

        Return:
            Dict with user information
        """
        user = self.collection.find_one_and_update(
            {
                'name': name
            },
            {
                '$set': {
                    'password': new_password
                }
            },
            return_document=ReturnDocument.AFTER
        )
        return user

    @error_handler
    def update_picture(self, name: str, img: bytes) -> dict:
        """Update picture for specifict user

        Args:
            name: name for the user to be updated
            img: bytes of the new user profile picture

        Return:
            Dict with user information
        """
        user = self.collection.find_one_and_update(
            {
                'name': name
            },
            {
                '$set': {
                    'img': img
                }
            },
            return_document=ReturnDocument.AFTER
        )
        return user
