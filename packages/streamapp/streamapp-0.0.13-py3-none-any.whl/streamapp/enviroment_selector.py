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
    session_state, secrets, container, image, columns, selectbox,
    button, sidebar
)
from typing import Literal
from .utils import page_selector


class EnvironmentSelector:
    """Enviroment selector in variables.

    type: class callable

    Set session state variables with images to show and
    access from session_state.environment.

    toml file:
        [ENVIRONMENTS]
        AR = 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/\
            Flag_of_Argentina.svg/2560px-Flag_of_Argentina.svg.png'
        BR = 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/\
            Flag_of_Brazil.svg/1280px-Flag_of_Brazil.svg.png'
        MX = 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fc/\
            Flag_of_Mexico.svg/1280px-Flag_of_Mexico.svg.png'
    """
    try:
        environments = dict(secrets.ENVIRONMENTS)
    except AttributeError:
        host = 'yt3.googleusercontent.com/ytc/AIdro_m3Dbjaq8CDkal5bP6rJ'
        img = '-IRDj2JTH5OlWM9-HAAWbeym0I=s176-c-k-c0x00ffffff-no-rj'
        environments = {
            'main': {
                'image': 'https://'+host+img
            }
        }

    def __init__(self, location: Literal['main', 'sidebar'] = 'main') -> None:
        """Initialization.

        Setting the first variable in toml file as default
        environment variable, and show the image by default.

        Args:
            None

        Return:
            None
        """
        if location == 'sidebar':
            col1, col2 = sidebar.container().columns([3, 1])
        else:
            col1, col2 = container().columns([3, 1])
        col1.selectbox(
            'Enviroment Select',
            self.environments.keys(),
            key='__EnvironmentSelect',
            placeholder='Select Enviroment',
            on_change=self.change_enviroment,
            label_visibility='collapsed',
            index=list(self.environments.keys()).index(
                session_state.get(
                    'environment',
                    list(self.environments.keys())[0]
                )
            )
        )
        self.change_enviroment()
        with col2:
            self.show_image()
        return

    @classmethod
    def change_enviroment(cls) -> None:
        """Replace session state variable.

        Args:
            None

        Return:
            None
        """
        session_state.environment = session_state.get(
            '__EnvironmentSelect'
        )
        session_state.environment_url = cls.environments.get(
            session_state.environment
        ).get('url', '')

    @staticmethod
    def set_options(key: str, option: callable) -> None:
        """Create a widget to show subpages.

        Set the active subpage inside pages.

        Args:
            key: str subpage`s name
            option: callable funtion to show streamlit widgets

        Return:
            None
        """
        session_state[key] = option

    @classmethod
    def show_image(cls, width: int = 40):
        """Show environment image in the front.

        Args:
            width: image width in the front

        Return:
            None
        """
        if session_state.environment is not None:
            return image(
                cls.environments
                .get(session_state.environment, '')
                .get('image'),
                width=width
            )
        return

    @classmethod
    def change_options(cls, key: str, page_options: dict[str: callable],
                       include_pages: bool = False,
                       place_holder: str = 'Expander') -> None:
        """[DEPRECATE]
        Change between subpages inside a page.

        Args:
            key: page name for the selectos
            page_options: a dict with subpages names and defined function

        Return:
            None
        """
        col1, col2 = columns([7, 1])
        with col1.expander(place_holder, expanded=False):
            selectbox(
                'Options',
                key=f'{key}_selected',
                options=page_options.keys(),
                label_visibility='hidden',
                placeholder=place_holder
            )
            button(
                'Select Option',
                on_click=cls.set_options,
                kwargs={
                    'key': key,
                    'option': session_state.get(f'{key}_selected')
                },
                type='primary'
            )
        with col2:
            cls.show_image()

        if include_pages:
            page_selector(session_state, key, page_options)
            return
        return
