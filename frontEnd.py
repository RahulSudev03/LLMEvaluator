import streamlit as st
import requests
from streamlit_supabase_auth_ui.widgets import __login__

__login__obj = __login__(auth_token = st.secrets["courier_auth_token"],
                    company_name = "RahulSudev03's Org",
                    width = 200, height = 250,
                    logout_button_name = 'Logout', hide_menu_bool = False,
                    hide_footer_bool = False,
                    lottie_url = 'https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json')

LOGGED_IN= __login__obj.build_login_ui()

tabs = st.tabs(["Home", "Experiments"])

if LOGGED_IN == True:
    
    with tabs[0]:
        st.header("Home")
        st.write("This is the LLM Evaluator platform where you can evaluate your queries against LLMs.")
        st.write("Navigate to the **Experiments** tab to start creating and evaluating experiments.")
    
    with tabs[1]:
        st.title("Experiments")
        st.header("Input section")
        systemPrompt = st.text_area("Input the system prompt","",height = 68)
        query = st.text_area("Enter your query","",height = 68)
        groundTruth = st.text_area("Enter the expected output","",height = 68)

        if st.button("Evaluate"):
            if query and systemPrompt and groundTruth:
                payload = {
                    "query":query,
                    "systemPrompt": systemPrompt,
                    "groundTruth": groundTruth
                }
                with st.spinner("Evaluating... Please wait!"):
                    try:
                        response = requests.post("http://127.0.0.1:8000/evaluate",json= payload)
                        if response.status_code == 200:
                            data = response.json()
                            col1, col2 = st.columns(2)
                            st.success("Evaluation complete!")
                            with col1:
                                st.subheader("LLM output")
                                st.write(f"**Answer:** {data['answer']}")   
                                st.metric("Response Time (seconds)", f"{data['response_time']:.3f}")
                            with col2:    
                                st.subheader("Evaluation")
                                st.write(data.get("Groq Answer"))
                            
                        else:
                            st.error(f"Error: {response.status_code} - {response.text}")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
                
            else:
                st.warning("Please fill out all fields before submitting.")
        
