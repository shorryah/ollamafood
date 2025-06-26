import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests #sends request to ollama

router = APIRouter()

#representation of what the input will be
class Question(BaseModel):
    question: str 

#endpoint to answer food-related qns
@router.post("/ask")
def ask_question(q: Question):
    # Instruction given to Ollama to answer only food-related qns and instructs what to answer if a non-food related qn is asked
    system_prompt = (
        "You are a helpful assistant that ONLY answers questions related to food. "
        "If the question is not related to food, reply with: "
        "'I'm sorry, I can only answer food-related questions.'"
    )
    
    # Combine system prompt and user's question in one text
    prompt = system_prompt + "\nUser question: " + q.question

#prepares the JSON preload with model name that will be used, prompt text and the maximum number of words ollama will use to answer the qn
    payload = {
        "model": "mistral:latest",
        "prompt": prompt,
        "max_tokens": 256
    }

    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload) #post request is sent to ollama
        response.raise_for_status() #checks if request is successful
        raw_text = response.text #gets the raw ollama response
        
        lines = raw_text.strip().split("\n") #splits response answers in new lines
        
        full_answer = ""
        for line in lines:
            chunk = json.loads(line) #answer presented in a presentable format
            full_answer += chunk.get("response", "")
            if chunk.get("done", False):
                break

        return {"question": q.question, "answer": full_answer} #returns json object with original qn and ollama's answer

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama error: {str(e)}")
