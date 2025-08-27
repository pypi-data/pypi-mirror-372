"""Useful functions to ease the streamlit apps development.

Functions to interact and solve common and repetitive procedures
during the streamlit sessions state development and other scenarios.
"""
from typing import Optional, Any
from typing_extensions import deprecated


def get_vars(session, prefix: Optional[str] = None, *args: str
             ) -> dict[str: Any]:
    """Get all session variables with a prefix or the defined args

    Args:
        session: st.session_state
        prefix: the prefix to query for variables in the session
        args: other variables to query in the session

    Retuns:
        dict containing variable name as key and and variable
        content as value
    """
    if prefix:
        add_vars = tuple(
            filter(lambda i: i.startswith(prefix), session.keys())
            )
        args += add_vars
    vars = dict(filter(lambda i: i[0] in args, session.items()))
    return vars


@deprecated('Use SubPages form streamapp instead')
def page_selector(session, page_key: str, page_options: dict) -> None:
    from streamlit import markdown
    page = page_options.get(
        session.get(page_key)
    )
    if callable(page):
        page()
    else:
        markdown('# Select an option!!! ⬆️')
    return


def clear_enviroment(session, *args: str) -> None:
    """Deleted session variables.

    Args:
        args: prefix or variables to be deleted.

    Returns:
        None
    """
    for i in args:
        variables = list(get_vars(session=session, prefix=i).keys())
        for i in variables:
            del session[i]
    return


def get_chunks(data: list, chunk_size: int = 1) -> list[list]:
    """Divide a whole list in a list of sublist with size x

    Args:
        data: the list to be divided
        chunk_size: elements inside every sublist

    Returns:
        a list with the sublists of size chunk_size
    """
    chunks = [
        data[x:x+chunk_size] for x in range(
            0,
            len(data),
            chunk_size
        )
    ]
    return chunks


class Classproperty(object):
    """Class to define class properties similar to
    @property decorator for objects.
    """
    def __init__(self, func) -> None:
        self.func = func

    def __get__(self, _, _self):
        return self.func(_self)
