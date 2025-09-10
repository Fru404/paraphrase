from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

import google.generativeai as genai

# Load API key from environment
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY environment variable not set.")

genai.configure(api_key=API_KEY)

# Initialize FastAPI app
app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://baselaunch-site.web.app/"],  # Or restrict
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Custom header API key for user authentication
MY_API_KEY = "Secret"

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != MY_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

#  Pydantic request model
class ParaphraseRequest(BaseModel):
    sentence: str

# Endpoint using Gemini 2.5 Flash
@app.post("/paraphrase")
async def paraphrase(request: ParaphraseRequest, api_key: str = Depends(verify_api_key)):
    input_sentence = request.sentence.strip()
    if not input_sentence:
        raise HTTPException(status_code=400, detail="No input provided.")

    # Create a Gemini model client
    model = genai.GenerativeModel("gemini-2.5-flash")

    # Use Gemini to paraphrase
    response = model.generate_content(
    f"Humanize this sentence clearly, do not over change the sentence structure. Just give the single paraphrased sentence only, no explanation, no list. Don't inlude 'em dash': \"{input_sentence}\""
)


    # Extract text from Gemini response
    paraphrased = response.text.strip() if hasattr(response, 'text') else str(response)

    return {"paraphrases": [paraphrased]}
