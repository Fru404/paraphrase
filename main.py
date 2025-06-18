# Import necessary modules
import nest_asyncio
from pyngrok import ngrok

from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import torch
from transformers import BartForConditionalGeneration, BartTokenizer

# Apply asyncio patch for Colab/interactive environments
nest_asyncio.apply()

# Set up ngrok
ngrok.set_auth_token("2IWN0C7fuFHe14Ir6w0rhDSZ9m8_6jukyLciKVJfqXpTcinjU")
public_url = ngrok.connect(8000)  # FastAPI default port is 8000
print(f"Public URL: {public_url}")

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

# Load model & tokenizer once at startup
model = BartForConditionalGeneration.from_pretrained('eugenesiow/bart-paraphrase')
tokenizer = BartTokenizer.from_pretrained('eugenesiow/bart-paraphrase')
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

@app.post("/paraphrase")
async def paraphrase(request: ParaphraseRequest, api_key: str = Depends(verify_api_key)):
    input_sentence = request.sentence.strip()
    if not input_sentence:
        raise HTTPException(status_code=400, detail="No input provided.")

    batch = tokenizer(input_sentence, return_tensors='pt').to(device)
    generated_ids = model.generate(
        batch['input_ids'],
        max_length=512,           # increase for longer paraphrase
        num_beams=5,              # more beams = better paraphrase
        num_return_sequences=1,   # return how many paraphrases
        early_stopping=True
    )
    generated_sentence = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)

    return {"paraphrases": generated_sentence}

# Run the app with uvicorn
# For Colab/Jupyter, use this instead of CLI:
import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000)
