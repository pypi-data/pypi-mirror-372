"""Custom Snowflake connector for Streamlit.

This custom connector tries to ease the use of Jinja templates to generate
queries, it supports direct queries, template queries and template queries
with Jinja formating, inside Jinja template you can use loops, conditionals
and define variables.
Jinja details go to: https://jinja.palletsprojects.com/en/3.1.x/
it must be used carefully to prevent SQLinjection.

Usage:
    conn = st.connection('snow', tye=SnowConnection)
    df1 = conn.query('select * from table')
    df2 = conn.query('select * from table wheer column1 = "{{name}}"',
                     params={'name': 'John'})
    df3 = conn.query_template('path/to/query.sql')
    df4 = conn.query_template('path/to/query.sql',
                              params={'name': 'John', 'last_name': 'Doe'})
"""

from pathlib import Path
from datetime import timedelta
from snowflake import connector
from cryptography.fernet import Fernet
from jinja2 import Environment, FileSystemLoader, BaseLoader
from pandas import read_sql_query, DataFrame
from pandas.io.sql import DatabaseError as DatabaseErrorPd
from streamlit.connections import BaseConnection
from streamlit import cache_data, session_state, secrets, toast
from snowflake.connector.errors import (
    DatabaseError, InternalServerError, ProgrammingError
)
import warnings
warnings.filterwarnings("ignore", category=UserWarning)


class SnowConnection(BaseConnection):
    """Custom Snowflake Connector for Streamlit.

    This custom connector tries to ease the use of Jinja templates to generate
    queries, it supports direct queries, template queries, template queries
    with Jinja formating, inside Jinja template you can use loops, conditionals
    and define variables.
    """
    def _connect(self):
        """Connect to Snowflake server.

        Use the credentials avaialable in .streamlit/secrets.toml file for
        streamlit Apps or the credentials in secrets for production.

        Args: None

        Returns:
            connector object.
        """
        try:
            connection = connector.connect(
                **self.__check_tocken(
                    dict(secrets.SNOW_SERVER)
                )
            )
            return connection
        except (DatabaseError, KeyError, AttributeError):
            return

    def __check_tocken(self, credentials: dict) -> dict:
        """Snowflake connector checker.

        Check for hashed password for snowflake with Fernet encoder,
        if you use external browser reset the user name to streamlit user.
        To unhash the password use the key in .secrets/toml file

        Args:
            credentials: The Snowflake credential from .secrets/toml

        Returns:
            A dict with the credentials checked
        """
        try:
            if secrets.get('snow_key', False):
                token = Fernet(secrets.key.encode()).decrypt(
                    credentials.get('password', '').encode()
                ).decode()
                credentials.pop('password')
                credentials.update(password=token)
        except Exception:
            credentials.pop('user')
            credentials.update(user=session_state.get('name'))
        return credentials

    @classmethod
    def get_variables(cls, file_name) -> dict:
        """Search for varibles in jinja templates

        Search all simple variables in Jina templates, simple variables are
        those within double braces `{{varaible}}`

        Args:
            file_name: The path to the jinja template

        Returns:
            A dict with the varibles as keys
        """
        try:
            query_path = Path(
                secrets.get('queries_path', ''),
                file_name
            ).as_posix()
            params, i, j = set(), 0, 0
            with open(query_path, 'r') as f:
                query = f.read()

            while i >= 0:
                i = query.find('{{', j)
                j = query.find('}}', i)
                if i >= 0:
                    params.add(query[i+2:j])
            params = {k: None for k in params}
            return params
        except (FileNotFoundError):
            return {'Error': 'File Not Found'}

    @classmethod
    def render(cls, query: str, params: dict, template: bool = True) -> str:
        """Render Jinja templates with the given variables.

        Inject the variables to the template in Jinja and applies the formating
        for conditionals and loops form a text input or a path to the file
        with the query.

        Args:
            query: the SQL query or path to the query.
            params: dict with the variables to be injected in the SQL template.
            direct: default True, True to use a SQL query as input,
                False to use a query template.

        Returns:
            str object with the query rendered qith the variables
        """
        try:
            if template:
                query = Path(query)
                if not query.name.lower().endswith('.sql'):
                    query = query.with_suffix('.sql')
                query_path = Path(
                    secrets.get('queries_path', ''),
                    query
                ).as_posix()
                query_rendered = Environment(
                    loader=FileSystemLoader('')
                ).get_template(query_path).render(**params)
            else:
                query_rendered = Environment(
                    loader=BaseLoader()
                ).from_string(query).render(**params)
        except Exception as e:
            return str(e)
        return query_rendered

    def query(self, query: str, params: dict = dict(), template: bool = False,
              ttl: timedelta = timedelta(minutes=30),
              succes_confirmation: bool = True) -> DataFrame:
        """Executes the given query.

        Args:
            query: the SQL Statement or Path to Jinja template.
            params: a dict with the varable names and values to be injected in
                Jinja template.
            template: if True search for the template in the path defined in
                `query` argument.
            ttl: timedelta object to streamlit mantain the resuklt in chache.

        Returns:
            a Pandas dataframe with the result, if any Exection occurs during
            the execution, this is returned in the dataframe results.
        """
        query_rendered = SnowConnection.render(query, params, template)

        @cache_data(ttl=ttl)
        def _query(query_rendered):
            frm = read_sql_query(query_rendered, self._instance)
            frm.rename(columns=str.upper, inplace=True)
            return frm

        try:
            result = _query(query_rendered)
            if succes_confirmation:
                toast('Success!', icon='✅')
        except AttributeError:
            toast('Something when wrong!! ⛔')
            return DataFrame(data={'Error Reason': ['Check your credentials']})
        except (DatabaseError, DatabaseErrorPd, InternalServerError) as e:
            toast('Something when wrong!! ⛔')
            if secrets.get('dev'):
                return DataFrame(data={'Error Reason': [str(e)]})
            return DataFrame(data={'Error Reason': ['Query Error']})
        else:
            return result

    def query_async(self, query: str, params: dict = dict(),
                    template: bool = False,
                    ttl: timedelta = timedelta(minutes=30)) -> str:
        """Executes the given query.

        This metod uses the async funtionality in Snowflake to run queries
        whitch the responde isn't neccessary, or could be checkeck later.
        Use this method is there is a long running query or the responde is not
        needed like in good performed insert or update operations.

        Args:
            query: the SQL Statement or Path to Jinja template.
            params: a dict with the varable names and values to be injected in
                Jinja template.
            template: if True search for the template in the path defined in
                `query` argument.
            ttl: timedelta object to streamlit mantain the resuklt in chache.

        Returns:
            a Snowflake query Id.
        """
        query_rendered = SnowConnection.render(query, params, template)

        @cache_data(ttl=ttl)
        def _query(query_rendered):
            with self._instance.cursor(connector.DictCursor) as cur:
                cur.execute_async(query_rendered)
            return cur.sfqid

        try:
            result = _query(query_rendered)
        except AttributeError:
            toast('Something when wrong!! ⛔')
            return 'Check your credentials'
        except (DatabaseError, InternalServerError) as e:
            toast('Something when wrong!! ⛔')
            if secrets.get('dev'):
                return str(e)
            return 'Query Error'
        else:
            return result

    def get_async_results(self, sfqid) -> DataFrame:
        """Call query result from async query

        Retrieve the result of an async query with teh query ID,
        and pass the result as a Pandas Dataframe

        Args:
            sfwid: The snowflake query id to retrieve data

        Returns:
            A pandas Dataframe with the query result
        """
        msg = toast('Gathering data...')
        try:
            if self._instance.is_still_running(
                    self._instance.get_query_status(sfqid)):
                msg.toast('The query is still runing', icon='🚀')
                return DataFrame()

            with self._instance.cursor(connector.DictCursor) as cur:
                msg.toast('Gathering data...', icon='⚙️')
                cur.get_results_from_sfqid(sfqid)
                frm = DataFrame(cur.fetchall())
            frm.rename(columns=str.upper, inplace=True)
            msg.toast('Success!!', icon='✅')
            return frm
        except AttributeError:
            msg.toast('Something when wrong!! ⛔')
            return DataFrame(data={'Error Reason': ['Check your credentials']})
        except ProgrammingError as e:
            if secrets.get('dev'):
                return DataFrame(data={'Error Reason': [str(e)]})
            return DataFrame(data={'Error Reason': ['Query Error']})
