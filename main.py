from fastapi import FastAPI
from pydantic import BaseModel
import time
import google.generativeai as genai
from dotenv import load_dotenv
from groq import Groq
from rapidfuzz import fuzz
from supabase import create_client,Client
import psycopg2
import os
import streamlit as st
from mistralai import Mistral
import asyncio


load_dotenv()

#Getting supabase credentials
url:str = os.getenv("supa_url")
key:str = os.getenv("supa_key")
supabase: Client = create_client(url, key)

#Configuring Gemini
genai.configure(api_key = os.getenv('GEMINI_API_KEY'))

#Configureing Mistral
mistral_api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-large-latest"

mistralClient = Mistral(api_key=mistral_api_key)

#Configuring groq
groqClient = Groq(
    api_key = os.getenv('GROQ_API_KEY')
)
# Initialize the FastAPI app
app = FastAPI()

#connecting to db
db_url = os.getenv("DATABASE_URL")



# Define a request body schema
class LLMRequest(BaseModel):
    systemPrompt: str
    query: str
    groundTruth: str
    metric:str
    metricDef:str

async def call_gemini(request:LLMRequest):
    start_time = time.time()
    model=genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction = request.systemPrompt)
    response = model.generate_content(request.query)
    answer = response.text
    response_time = time.time() - start_time
    return{
        "answer":answer,
        "response_time":response_time
    }

async def call_mistral(request:LLMRequest):
    start_time = time.time()
    chat_response = mistralClient.chat.complete(
    model = model,
    messages = [
        {
            "role": "user",
            "content": request.query,
        },
    ]
    )
    response_time = time.time() - start_time
    return{
        "answer":chat_response.choices[0].message.content,
        "response_time": response_time
    }
    
    
    
    
    




# Define a POST route
@app.post("/evaluate")
async def evaluate_llm(request: LLMRequest):
    systemPrompt  = request.systemPrompt
    try:
        response_gemini, response_mistral = await asyncio.gather(
            call_gemini(request),
            call_mistral(request)
        )
    except Exception as e:
        return {"error": f"Failed to evaluate LLMs: {str(e)}"}
        
    geminiEvalResponse = LLMeval(systemPrompt, request.query, response_gemini["answer"],request.groundTruth,request.metric, request.metricDef)
    
    mistralEvalResponse = LLMeval(systemPrompt, request.query, response_mistral["answer"],request.groundTruth,request.metric, request.metricDef)
    
    gemini_fuzzRatio = fuzzy_match(response_gemini["answer"], request.groundTruth)
    mistral_fuzzRatio = fuzzy_match(response_mistral["answer"], request.groundTruth)

    return{
        "gemini_answer": response_gemini["answer"],
        "mistral_answer":response_mistral["answer"],
        "gemini_response_time":response_gemini["response_time"],
        "mistral_response_time":response_mistral["response_time"],
        "geminiFuzzRatio": gemini_fuzzRatio,
        "mistralFuzzRatio":mistral_fuzzRatio,
        "geminiEval": geminiEvalResponse,
        "mistralEval":mistralEvalResponse
    }






def LLMeval(systemPrompt, request, answer,groundTruth, metric, metricDef):
    chat_completion = groqClient.chat.completions.create(
    messages=[
        {
            "role":"system",
            "content":f"You are an expert in evaluating the performance of language models (LLMs). Your task is to assess the quality of an LLM's response based on a given metric. The LLM you are evaluating operates under the following system prompt: {systemPrompt}."
        }
        ,{
            "role": "user",
            "content": f""" Here are the details for the evaluation:
            - Question asked to the LLM: {request}
            - Response provided by the LLM: {answer}
            - Expected answer: {groundTruth}
            - Evaluation metric: {metric}
            - Metric definition: {metricDef}  
            
            Please use the following approach to evaluate the response:

            1. Start by providing a step-by-step reasoning process (Chain of Thought) where you analyze how well the LLM's response aligns with the expected answer. Consider both the strengths and weaknesses of the response in relation to the metric definition.
            2. After completing the reasoning, assign a score between 0 and 5, where:
            - 0 = The response fails to meet the metric criteria entirely.
            - 5 = The response meets the metric criteria perfectly.
            3. Finally, provide a concise explanation summarizing the rationale behind your score.

            Your response should follow this format:
            Reasoning:
            <Step-by-step reasoning>

            'Metric score: <score>'
            Reason: '<Concise explanation summarizing your reasoning>'

            Ensure your reasoning is clear, logical, and directly tied to the metric definition. Do not include unnecessary details or extra steps outside the evaluation criteria.""",
            
        }
    ],
    model="llama-3.3-70b-versatile",
)
    return chat_completion.choices[0].message.content


def fuzzy_match(answer,ground_truth):
    return fuzz.ratio(answer,ground_truth)

def get_db_connection():
    conn = psycopg2.connect(db_url)
    return conn

def save_experiment_for_user(desired_username, experiment_name, system_prompt, query, expected_output, gemini_answer, gemini_response_time, gemini_fuzz_ratio, gemini_groq_answer, mistral_answer, mistral_response_time, mistral_fuzz_ratio, mistral_groq_answer, metric, metricDef):
    # Fetch user ID
    response = (
        supabase.table("user_authentication")
        .select("id")
        .eq("username", desired_username)
        .execute()
    )
    user_id = response.data[0]["id"]

    if user_id:
        # Insert experiment
        response = (
            supabase.table("experiments")
            .insert({
                "user_id": user_id,
                "experiment_name": experiment_name,
                "system_prompt": system_prompt,
                "query": query,
                "expected_output": expected_output,
                # Gemini fields
                "gemini_answer": gemini_answer,
                "gemini_response_time": gemini_response_time,
                "gemini_fuzz_ratio": gemini_fuzz_ratio,
                "gemini_evaluation": gemini_groq_answer,
                # Mistral fields
                "mistral_answer": mistral_answer,
                "mistral_response_time": mistral_response_time,
                "mistral_fuzz_ratio": mistral_fuzz_ratio,
                "mistral_evaluation": mistral_groq_answer,
                # Metric fields
                "metric": metric,
                "metric_definition": metricDef
            })
            .execute()
        )
        return True
    else:
        st.error("User not found in the database.")
        return False


def getUserExperiments(user_id):
    response = (
    supabase.table("experiments")
    .select("*")  # Select all columns, or specify specific ones
    .eq("user_id", user_id)  # Filter experiments for the current user
    .execute()
)
    experiments = response.data
    return experiments



    
    
