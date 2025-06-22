# Import necessary modules
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random

# Initialize FastAPI app
app = FastAPI()

# Allow CORS (optional)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or restrict to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API key for authentication
API_KEY = "Secret"

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

# Request body model
class ParaphraseRequest(BaseModel):
    sentence: str

@app.post("/paraphrase")
async def paraphrase(request: ParaphraseRequest, api_key: str = Depends(verify_api_key)):
    input_sentence = request.sentence.strip()
    if not input_sentence:
        raise HTTPException(status_code=400, detail="No input provided.")

    # 🌀 Very simple text mixing: shuffle words
    words = input_sentence.split()
    if len(words) > 1:
        random.shuffle(words)
    mixed_sentence = " ".join(words)

    return {"paraphrases": [mixed_sentence]}
