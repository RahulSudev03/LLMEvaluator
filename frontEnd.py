from auth import __login__obj as __login__, get_logged_in_user
import streamlit as st

LOGGED_IN = __login__.build_login_ui()

if LOGGED_IN:
    user = get_logged_in_user()
    if user:
        st.sidebar.write(f"Logged in as {user}")
    else:
        st.sidebar.write("No user is logged in.")
    pg = st.navigation([st.Page("home.py"), st.Page("experiments.py"),st.Page("prevExperiments.py")])
    pg.run()


    
    
    # st.header("Home")
    # st.write("This is the LLM Evaluator platform where you can evaluate your queries against LLMs.")
    # st.write("Navigate to the **Experiments** tab to start creating and evaluating experiments.")
    
    
    # st.title("Experiments")
    # st.header("Input section")
    # systemPrompt = st.text_area("Input the system prompt","",height = 68)
    # query = st.text_area("Enter your query","",height = 68)
    # groundTruth = st.text_area("Enter the expected output","",height = 68)
    # metric = st.text_input("Name the metric you want to evaluate the LLM against")
    # metricDef = st.text_area("Define the metric")

    # if st.button("Evaluate"):
    #     if query and systemPrompt and groundTruth:
    #         payload = {
    #             "query":query,
    #             "systemPrompt": systemPrompt,
    #             "groundTruth": groundTruth,
    #             "metric": metric,
    #             "metricDef": metricDef
    #         }
    #         with st.spinner("Evaluating... Please wait!"):
    #             try:
    #                 response = requests.post("http://127.0.0.1:8000/evaluate",json= payload)
    #                 if response.status_code == 200:
    #                     data = response.json()
    #                     col1, col2 = st.columns(2)
    #                     st.success("Evaluation complete!")
    #                     with col1:
    #                         st.subheader("LLM output")
    #                         st.write(f"**Answer:** {data['answer']}")   
    #                         st.metric("Response Time (seconds)", f"{data['response_time']:.3f}")
    #                         st.metric("FuzzRatio",f"{data['fuzzRatio']:.3f}")
    #                     with col2:    
    #                         st.subheader("Evaluation")
    #                         st.write(data.get("Groq Answer"))
                        
    #                 else:
    #                     st.error(f"Error: {response.status_code} - {response.text}")
    #             except Exception as e:
    #                 st.error(f"An error occurred: {str(e)}")
            
    #     else:
    #         st.warning("Please fill out all fields before submitting.")
        
