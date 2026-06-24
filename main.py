from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import requests
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io
from fastapi.responses import Response

app = FastAPI()

class PrintRequest(BaseModel):
    image_urls: List[str]

@app.post("/generate-pdf")
async def generate_pdf(request: PrintRequest):
    if len(request.image_urls) > 9:
        raise HTTPException(status_code=400, detail="Puoi inviare massimo 9 immagini")

    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    w, h = A4
    
    # Griglia 3x3
    for i, url in enumerate(request.image_urls):
        try:
            img_data = requests.get(url).content
            img_io = io.BytesIO(img_data)
            
            # Calcolo posizione (3 colonne, 3 righe)
            col = i % 3
            row = 2 - (i // 3)
            x = 50 + col * 180
            y = 300 + row * 200
            
            c.drawImage(img_io, x, y, width=150, height=200)
        except Exception:
            continue

    c.showPage()
    c.save()
    
    pdf_buffer.seek(0)
    return Response(content=pdf_buffer.read(), media_type="application/pdf")