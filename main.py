from fastapi import FastAPI
from pydantic import BaseModel
import time
import google.generativeai as genai
from dotenv import load_dotenv
from groq import Groq
import os

load_dotenv()

#Configuring Gemini
genai.configure(api_key = os.getenv('GEMINI_API_KEY'))

groqClient = Groq(
    api_key = os.getenv('GROQ_API_KEY')
)
# Initialize the FastAPI app
app = FastAPI()

# Define a request body schema
class LLMRequest(BaseModel):
    systemPrompt: str
    query: str
    groundTruth: str

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
    evalResponse = LLMeval(systemPrompt, request.query, answer,request.groundTruth)

    return{
        "answer": answer.strip(),
        "response_time":response_time,
        "Groq Answer": evalResponse
    }


def LLMeval(systemPrompt, request, answer,groundTruth):
    chat_completion = groqClient.chat.completions.create(
    messages=[
        {
            "role":"system",
            "content":f"You are an LLM evaluation expert. You are currently evaluating an LLM who's system prompt is {systemPrompt}."
        }
        ,{
            "role": "user",
            "content": f""" The question asked to the LLM is {request}, and the answer the LLM provided is {answer}. Compare the given answer with this expected answer: {groundTruth}, and provide a score of how relevant the answer is. give me a score between 0 and 5. 0 being no relevance and 5 having the most relavance. Relevance is defined as: The similarity of the answer compared to the expected answer.Think step by step.
            The answer you provide should be like this, do not show me the steps, all I want is a relavancy score and the reason:-
            Relevancy score: 'score' 
            Reason: 'Reason'  """,
            
        }
    ],
    model="llama-3.3-70b-versatile",
)
    return chat_completion.choices[0].message.content

    
    
