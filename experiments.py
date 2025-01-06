from auth import __login__, get_logged_in_user
from main import save_experiment_for_user, get_db_connection
import streamlit as st
import requests

st.title("Experiments")
st.header("Input section")

# Input fields
experimentName = st.text_input("What would you like to name your experiment?")
systemPrompt = st.text_area("Input the system prompt", "", height=68)
query = st.text_area("Enter your query", "", height=68)
groundTruth = st.text_area("Enter the expected output", "", height=68)
metric = st.text_input("Name the metric you want to evaluate the LLM against")
metricDef = st.text_area("Define the metric")

# Variables to store evaluation results
evaluation_results = {}

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
                response = requests.post("http://127.0.0.1:8000/evaluate", json=payload)
                if response.status_code == 200:
                    data = response.json()
                    evaluation_results.update({
                        "answer": data.get("answer", ""),
                        "response_time": data.get("response_time", 0),
                        "fuzzRatio": data.get("fuzzRatio", 0),
                        "Groq Answer": data.get("Groq Answer", ""),
                    })  # Store evaluation results
                    
                    col1, col2 = st.columns(2)
                    st.success("Evaluation complete!")
                    with col1:
                        st.subheader("LLM output")
                        st.write(f"**Answer:** {data['answer']}")
                        st.metric("Response Time (seconds)", f"{data['response_time']:.3f}")
                        st.metric("FuzzRatio", f"{data['fuzzRatio']:.3f}")
                    with col2:
                        st.subheader("Evaluation")
                        st.write(data.get("Groq Answer"))
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please fill out all fields before submitting.")

# Save experiment logic
if st.button("Save Experiment"):
    with st.spinner("Saving..."):
        username = get_logged_in_user()
        try:
            if save_experiment_for_user(username,
                experimentName,
                systemPrompt,
                query,
                groundTruth,
                evaluation_results.get('answer'," "),
                evaluation_results.get('response_time','0'),
                evaluation_results.get('fuzzRatio','0'),
                evaluation_results.get('Groq Answer',""),
                metric,
                metricDef,
            ):
                st.success("Successfully saved experiment")
            else:
                st.error("Could not save experiment")
        except Exception as e:
                st.error(f"An error occurred: {str(e)}")

