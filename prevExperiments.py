from auth import __login__obj as __login__, get_logged_in_user,get_logged_in_user_id
from main import getUserExperiments
import streamlit as st
import pandas as pd


user_id = get_logged_in_user_id()

# Find all experiments associated with the user
experiments = getUserExperiments(user_id)

if experiments:
    experiments_df = pd.DataFrame(experiments)
    st.dataframe(experiments_df)
    
else:
    st.warning("No experiments yet! Start by creating a new experiment")
    
