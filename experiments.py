from auth import __login__, get_logged_in_user
from main import save_experiment_for_user
import streamlit as st
import requests
import os

# Display page header
st.title("New Experiment")

# Input fields
experimentName = st.text_input("What would you like to name your experiment?", "")
systemPrompt = st.text_area("Input the system prompt", "", height=68)
query = st.text_area("Enter your query", "", height=68)
groundTruth = st.text_area("Enter the expected output", "", height=68)
metric = st.text_input("Name the metric you want to evaluate the LLM against", "")
metricDef = st.text_area("Define the metric", "", height=68)

# Initialize session state for evaluation results if not present
if "evaluation_results" not in st.session_state:
    st.session_state.evaluation_results = None

# Evaluate button
if st.button("Evaluate"):
    if query and systemPrompt and groundTruth:
        payload = {
            "query": query,
            "systemPrompt": systemPrompt,
            "groundTruth": groundTruth,
            "metric": metric,
            "metricDef": metricDef,
        }
        with st.spinner("Evaluating... Please wait!"):
            try:
                response = requests.post(os.getenv("backend_url"), json=payload)
                if response.status_code == 200:
                    st.session_state.evaluation_results = response.json()
                    # Display evaluation results
                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader("Gemini Results")
                        st.text_area("Answer", st.session_state.evaluation_results.get("gemini_answer", ""), height=100, disabled=True)
                        st.text(f"Response Time: {st.session_state.evaluation_results.get('gemini_response_time', 0)} seconds")
                        st.text(f"Fuzz Ratio: {st.session_state.evaluation_results.get('geminiFuzzRatio', 0)}")
                        st.text_area("AI Evaluation", st.session_state.evaluation_results.get("geminiEval", ""), height=100, disabled=True)

                    with col2:
                        st.subheader("Mistral Results")
                        st.text_area("Answer", st.session_state.evaluation_results.get("mistral_answer", ""), height=100, disabled=True)
                        st.text(f"Response Time: {st.session_state.evaluation_results.get('mistral_response_time', 0)} seconds")
                        st.text(f"Fuzz Ratio: {st.session_state.evaluation_results.get('mistralFuzzRatio', 0)}")
                        st.text_area("AI evaluation", st.session_state.evaluation_results.get("mistralEval", ""), height=100, disabled=True)
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please fill out all fields before submitting.")

# Save button (conditionally shown if evaluation_results exist)
if st.session_state.evaluation_results:
    if st.button("Save Experiment"):
        with st.spinner("Saving..."):
            username = get_logged_in_user()
            try:
                if save_experiment_for_user(
                    username,
                    experimentName,
                    systemPrompt,
                    query,
                    groundTruth,
                    # Gemini fields
                    st.session_state.evaluation_results.get("gemini_answer", ""),
                    st.session_state.evaluation_results.get("gemini_response_time", "0"),
                    st.session_state.evaluation_results.get("geminiFuzzRatio", "0"),
                    st.session_state.evaluation_results.get("geminiEval", ""),
                    # Mistral fields
                    st.session_state.evaluation_results.get("mistral_answer", ""),
                    st.session_state.evaluation_results.get("mistral_response_time", "0"),
                    st.session_state.evaluation_results.get("mistralFuzzRatio", "0"),
                    st.session_state.evaluation_results.get("mistralEval", ""),
                    metric,
                    metricDef,
                ):
                    st.success("Successfully saved experiment")
                else:
                    st.error("Could not save experiment")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

