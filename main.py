from fastapi import FastAPI
from pydantic import BaseModel
import time
import google.generativeai as genai
from dotenv import load_dotenv
from groq import Groq
from rapidfuzz import fuzz
import psycopg2
import os

load_dotenv()

#Configuring Gemini
genai.configure(api_key = os.getenv('GEMINI_API_KEY'))

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



# Define a POST route
@app.post("/evaluate")
async def evaluate_llm(request: LLMRequest):
    start_time = time.time()
    systemPrompt  = request.systemPrompt
    model=genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction = systemPrompt)
    response = model.generate_content(request.query)
    answer = response.text
    
        
    # Calculate response time
    response_time = time.time() - start_time
    evalResponse = LLMeval(systemPrompt, request.query, answer,request.groundTruth,request.metric, request.metricDef)
    
    fuzzRatio = fuzzy_match(answer, request.groundTruth)

    return{
        "answer": answer.strip(),
        "response_time":response_time,
        "fuzzRatio": fuzzRatio,
        "Groq Answer": evalResponse
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
    
    
