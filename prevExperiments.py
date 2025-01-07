from auth import __login__obj as __login__, get_logged_in_user, get_logged_in_user_id
from main import getUserExperiments
import streamlit as st
import pandas as pd

user_id = get_logged_in_user_id()

# Find all experiments associated with the user
experiments = getUserExperiments(user_id)

if experiments:
    search_query = st.text_input("Search experiments by name:", "")
    filtered_experiments = [
        exp for exp in experiments if search_query.lower() in exp["experiment_name"].lower()
    ]

    if filtered_experiments:
        for exp in filtered_experiments:
            with st.expander(f"Experiment: {exp['experiment_name']}"):
                st.write(f"**System Prompt:** {exp['system_prompt']}")
                st.write(f"**Query:** {exp['query']}")
                st.write(f"**Expected Output:** {exp['expected_output']}")
                st.write(f"**Metric:** {exp['metric']}")
                st.write(f"**Metric Definition:** {exp['metric_definition']}")
                st.write("### Gemini Results")
                st.write(f"**Gemini Answer:** {exp['gemini_answer']}")
                st.metric("Gemini Response Time", exp['gemini_response_time'])
                st.write(f"**Gemini Fuzz Ratio:** {exp['gemini_fuzz_ratio']}")
                st.write(f"**Gemini Groq Answer:** {exp['gemini_evaluation']}")
                
                st.write("### Mistral Results")
                st.write(f"**Mistral Answer:** {exp['mistral_answer']}")
                st.metric("Mistral Response Time", exp['mistral_response_time'])
                st.write(f"**Mistral Fuzz Ratio:** {exp['mistral_fuzz_ratio']}")
                st.write(f"**Mistral Groq Answer:** {exp['mistral_evaluation']}")
    else:
        st.warning("No experiments match your search.")
else:
    st.warning("No experiments yet! Start by creating a new experiment.")