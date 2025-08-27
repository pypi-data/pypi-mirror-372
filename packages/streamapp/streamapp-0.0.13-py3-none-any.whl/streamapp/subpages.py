"""Enviroment variables to streamlit session.

Set session state variables with images to show,
they are stored in session_state.environment and you
can change between them from a selector and put it to
each variable an image to show.

Usage:
    from streamapp_utils import EnvironmentSelector
    EnvironmentSelector()

    `or use it as widget in Login`
    from streamapp_utils import EnvironmentSelector, login
    login(
        roles=['admin', 'tester', 'main'],
        side_bar_widget=EnvironmentSelector
    )
"""
from streamlit import (
    session_state, container, sidebar, markdown, secrets, error
)
from dataclasses import dataclass
from typing import Literal
from .auth.roles import Roles


@dataclass
class SubPages:
    key: str
    page_options: dict[str: tuple[callable, list[str]]]
    location: Literal['main', 'sidebar'] = 'main'

    def __post_init__(self):
        """
        Change subpages inside a page.

        Args:
            key: page name for the selectos
            page_options: a dict with subpages names and defined function

        Return:
            None
        """
        try:
            if self.location == 'main':
                con = container()
            else:
                con = sidebar.container()
            con.selectbox(
                'Options',
                key=f'__SubPages_{self.key}_selected',
                options=self.page_options.keys(),
                index=list(self.page_options.keys()).index(
                    session_state.get(
                        f'__SubPages_{self.key}_subpage',
                        list(self.page_options.keys())[0]
                    )
                ),
                label_visibility='hidden',
                on_change=self.__set_subpage
            )
            if session_state.get(f'__SubPages_{self.key}_subpage') is None:
                self.__set_subpage()

            page, roles = self.page_options.get(
                session_state.get(f'__SubPages_{self.key}_subpage')
            )

            if callable(page):
                Roles.allow_acces(roles)
                page()
            else:
                admin_contact = secrets.get('admin_contact', '')
                markdown(
                    f"""
                    # Invalid page option ⛔
                    Contact your admin for more info {admin_contact}
                    """
                )
        except Exception as e:
            if secrets.get('dev', False):
                error(e)
            else:
                admin_contact = secrets.get('admin_contact', '')
                error(
                    f"""
                        # ⛔ Something went wrong with this page
                        Contact your admin {admin_contact}
                    """
                )
        return

    def __set_subpage(self) -> None:
        """Update selected page in session state for the key."""
        session_state[f'__SubPages_{self.key}_subpage'] = session_state.get(
            f'__SubPages_{self.key}_selected'
        )
