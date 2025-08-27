"""Custom Snowflake connector for Streamlit.

This custom connector tries to ease the use of Jinja templates to generate
queries, it supports direct queries, template queries, template queries
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

from streamlit import secrets, session_state, markdown, warning, stop
from typing import Optional, Callable


class Roles:
    """Custom Roles handler for streamapp Authenticator.

    Type: class

    Experimental class decorator to handled roles in fuctions.
    """
    admin_contact = secrets.get('admin_contact', '')
    no_acces = f"""
    # ⛔ You don't have access to this page
    ---
    Your admin hasn't granted to you the role to access this section,
    contact your admin for more details {admin_contact}
    """

    def __init__(self, session: any, roles: list[str]) -> None:
        """Experiemntal initializator for class decorator."""
        self.session = session
        self.roles = set(roles)

    def __call__(self, func: callable) -> Callable:
        """Experimental decorator."""
        if self.roles.intersection(self.session.get('roles', [])):
            def wrapper():
                return func()
            return wrapper
        else:
            return lambda _: None

    @classmethod
    def allow_acces(cls, roles: Optional[list] = None):
        """Handle session roles if user has enough privileges for a page.

        If the users does not have a granted trole for the page the streamlit
        page running is stopped.

        Args:
            roles: list of roles which can access the page

        Return:
            None
        """
        if 'dev' in session_state.get('roles', []):
            warning('Be carefull in development speace', icon='🤖')
        elif roles is None or 'admin' in session_state.get('roles', []):
            return
        elif not set(roles).intersection(session_state.get('roles', [])):
            markdown(cls.no_acces)
            stop()
        return
