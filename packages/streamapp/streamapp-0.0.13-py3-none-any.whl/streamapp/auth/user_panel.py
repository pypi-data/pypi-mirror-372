"""Custom Streamlit UI page to handled MongoAuth users from streamapp auth.

Class to call for an user interface to interact with credentials and
user information, with a panel for regular user self management and
other panel for admins to manage users.

Uses the .secrets variable `allowed_roles` for the grant roles part,
all roles in this file will be consider to be used in the interface, otherwise
the default roles will be ['admin', 'user']

Usage:
    $ .secrets.toml
    ```
    ...
    allowed_roles = ['analysts', 'support', 'guess', 'admin']
    ```

    from streamapp import auth
    auth.login(['admin', 'guess', 'main'])
    auth.admin_page()
"""
import streamlit as st
from streamlit.runtime.media_file_storage import MediaFileStorageError
from streamlit_authenticator.utilities.hasher import Hasher
from PIL import Image, ImageDraw, UnidentifiedImageError
from io import BytesIO


class UserControlUi:
    "Custom Streamlit UI page to handled MongoAuth users from streamapp auth"
    def __init__(self) -> None:
        """Class initializer and set the roles for the UI"""
        self.allow_roles = st.secrets.get('allowed_roles', ['admin', 'user'])

    def user_panel(self) -> bool:
        """Display user interface.

        Interface to interact with:
            - update username
            - update password
            - update profile picture
            - see user information

        Args:
            None

        Return:
            UI streamlit interface page and
            bool: False if there no chnges, True if a change was performed
        """
        st.subheader('User panel')
        info, name, password, photo = st.tabs([
            'User Info',
            'Update Username',
            'Update Password',
            'Update Photo'
        ])
        with info:
            _, ma, _ = st.container(border=True).columns([1, 4, 1])
            _, img_col, _ = ma.columns(3)
            ma.title(st.session_state.username)
            ma.code('📧 ' + st.session_state.name)
            try:
                ma.divider()
                ims = Image.open(BytesIO(st.session_state.profile_img))
                mask = Image.new("L", ims.size, 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse(
                    (4, 4, ims.size[0] - 4, ims.size[1] - 4),
                    fill=255
                )
                img_col.image(
                    Image.composite(
                        ims,
                        Image.new(ims.mode, ims.size, (255, 255, 255)),
                        mask
                    ),
                    use_container_width=True
                )
            except (MediaFileStorageError, AttributeError,
                    TypeError, UnidentifiedImageError):
                ma.info('Consider to load a profile photo')
            ma.dataframe(
                {'Roles': [st.session_state.roles]},
                use_container_width=True
            )

        with name:
            _, ma, _ = st.columns([1, 3, 1])
            ft = ma.form('Update Username', clear_on_submit=True)
            auth_new_user_name = ft.text_input(
                'Username',
                placeholder='New Username'
            )
            name_bt = ft.form_submit_button('Change Username')
            if name_bt:
                self.conn.update_name(
                    st.session_state.name,
                    auth_new_user_name
                )
                return True

        with password:
            _, ma, _ = st.columns([1, 3, 1])
            ft = ma.form('Update Password', clear_on_submit=True)
            auth_new_password = Hasher._hash(
                ft.text_input(
                    'Password',
                    placeholder='New Password',
                    type='password'
                )
            )
            password_bt = ft.form_submit_button('Update Password')
            if password_bt:
                self.conn.update_password(
                    st.session_state.name,
                    auth_new_password
                )
                return True

        with photo:
            _, ma, _ = st.columns([1, 3, 1])
            ft = ma.form('Update Profile Photo', clear_on_submit=True)
            auth_new_photo = ft.file_uploader(
                'Profile Photo',
                type=['jpg', 'png', 'jpeg'],
                accept_multiple_files=False
            )
            photo_bt = ft.form_submit_button('Change Photo')
            if photo_bt:
                try:
                    self.conn.update_picture(
                        st.session_state.name,
                        auth_new_photo.getvalue()
                    )
                except AttributeError:
                    st.error('Load a Photo')
                return True
        return False

    def admin_panel(self) -> bool:
        """Display admin interface.

        Interface to manage with:
            - reset users passwords
            - create new user
            - delete existing user
            - revoke or grant roles
            - see all users

        Args:
            None

        Return:
            UI streamlit interface page and
            bool: False if there no chnges, True if a change was performed
        """
        if 'admin' not in st.session_state.roles:
            return
        st.subheader('Admin panel')
        reset_pw, new_user, new_role, revoke_role, delete_user, us = st.tabs([
            'Reset User Password',
            'Create user',
            'Grand roles',
            'Revoke roles',
            'Delete user',
            'Users'
        ])
        with reset_pw:
            _, ma, _ = st.columns([1, 3, 1])
            ft = ma.form('Reset User Password', clear_on_submit=True)
            auth_reset_ps_username = ft.selectbox(
                'Username',
                options=[x.get('name') for x in self.conn.get_users()]
            )
            auth_reset_ps_admin = Hasher._hash(
                ft.text_input(
                    'Password',
                    placeholder='New Password',
                    type='password'
                )
            )
            admin_reset_ps_bt = ft.form_submit_button('Reset Password')
            if admin_reset_ps_bt:
                self.conn.update_password(
                    auth_reset_ps_username,
                    auth_reset_ps_admin
                )
                return True

        with new_user:
            _, ma, _ = st.columns([1, 3, 1])
            ft = ma.form('Create User', clear_on_submit=True)
            auth_create_username = ft.text_input(
                'Username',
                placeholder='Username'
            )
            auth_create_email = ft.text_input(
                'Email',
                placeholder='email'
            )
            auth_create_password = Hasher._hash(
                ft.text_input(
                    'Password',
                    placeholder='Password',
                    type='password'
                )
            )
            if isinstance(self.allow_roles, list):
                auth_create_roles = ft.multiselect(
                    'Roles',
                    options=self.allow_roles
                )
            else:
                auth_create_roles = st.text_input(
                    'Roles',
                    placeholder='Role',
                ).split(',')
            auth_create_img = ft.file_uploader(
                'Profile Photo',
                type=['jpg', 'png', 'jpeg'],
                accept_multiple_files=False,
            )
            create_user_bt = ft.form_submit_button('Create user')
            if create_user_bt:
                self.conn.add_user(
                    username=auth_create_username,
                    name=auth_create_email,
                    password=auth_create_password,
                    roles=auth_create_roles,
                    img=(auth_create_img.getvalue()
                         if auth_create_img else b'')
                )
                return True

        with new_role:
            _, ma, _ = st.columns([1, 3, 1])
            ft = ma.form('Grant Role', clear_on_submit=True)
            auth_grant_rl_username = ft.selectbox(
                'Username',
                options=[x.get('name') for x in self.conn.get_users()]
            )
            if isinstance(self.allow_roles, list):
                auth_grant_roles = ft.multiselect(
                    'Roles',
                    options=self.allow_roles
                )
            else:
                auth_grant_roles = st.text_input(
                    'Roles',
                    placeholder='Role',
                ).split(',')
            grant_bt = ft.form_submit_button('Grant Role')
            if grant_bt:
                self.conn.grant_roles(
                    auth_grant_rl_username,
                    auth_grant_roles
                )
                return True

        with revoke_role:
            _, ma, _ = st.columns([1, 3, 1])
            ft = ma.container(border=True)
            auth_revoke_rl_username = ft.selectbox(
                'Username',
                options=[x.get('name') for x in self.conn.get_users()]
            )
            auth_revoke_roles = ft.multiselect(
                'Roles',
                options=self.conn.get_user(
                    auth_revoke_rl_username
                )['roles']
            )
            revoke_bt = ft.button('Revoke Role')
            if revoke_bt:
                self.conn.delete_roles(
                    auth_revoke_rl_username,
                    auth_revoke_roles
                )
                return True

        with delete_user:
            _, ma, _ = st.columns([1, 3, 1])
            ft = ma.form('Delete User', clear_on_submit=True)
            auth_delete_username = ft.selectbox(
                'Username',
                options=[x.get('name') for x in self.conn.get_users()]
            )
            delete_bt = ft.form_submit_button('Delete User')
            if delete_bt:
                self.conn.delete_user(
                    auth_delete_username,
                )
                return True

        with us:
            st.dataframe(
                self.conn.get_users(),
                column_order=['username', 'name', 'roles'],
                use_container_width=True,
                column_config={
                    'username': st.column_config.TextColumn('User'),
                    'name': st.column_config.TextColumn('Email'),
                    'roles': st.column_config.ListColumn('Roles'),
                }
            )
        return False
