from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from PIL import Image
import requests
from io import BytesIO

app = FastAPI()

class PrintRequest(BaseModel):
    image_urls: List[str]

@app.get("/")
def read_root():
    return {"message": "API di stampa pronta. Invia una richiesta POST a /generate-pdf"}

@app.post("/generate-pdf")
async def generate_pdf(request: PrintRequest):
    # Qui aggiungeremo in seguito la logica per il 3x3
    # Per ora, verifichiamo che l'API riceva correttamente gli URL
    return {"ricevute": len(request.image_urls), "urls": request.image_urls}