# auth.py
from streamlit_supabase_auth_ui.widgets import __login__
import streamlit as st
from supabase import create_client,Client
import os


url:str = os.getenv("supa_url")
key:str = os.getenv("supa_key")
supabase: Client = create_client(url, key)

__login__obj = __login__(
    auth_token=st.secrets["courier_auth_token"],
    company_name="RahulSudev03's Org",
    width=200,
    height=250,
    logout_button_name="Logout",
    hide_menu_bool=False,
    hide_footer_bool=False,
    lottie_url="https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json"
)

def get_logged_in_user():
    username = __login__obj.cookies.get('__streamlit_login_signup_ui_username__')
    return username

def get_logged_in_user_id():
    username = get_logged_in_user()
    response = (
    supabase.table("user_authentication")
    .select("id")
    .eq("username", username)
    .execute()
)
    user_id = response.data[0]["id"]
    return user_id
