from fastapi import FastAPI, Response
from pydantic import BaseModel
from typing import List
import requests
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import io

app = FastAPI()

class PrintRequest(BaseModel):
    image_urls: List[str]

@app.post("/generate-pdf")
async def generate_pdf(request: PrintRequest):
    pdf_buffer = io.BytesIO()
    # A4 è 595x842 punti
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    
    # Dimensioni carta (es. 63mm x 88mm = 178pt x 250pt circa)
    # Regola questi valori se le tue carte hanno dimensioni diverse
    card_w = 178 
    card_h = 250
    
    for i, url in enumerate(request.image_urls):
        if i >= 9: break
        try:
            response = requests.get(url, timeout=5)
            img = ImageReader(io.BytesIO(response.content))
            
            # Calcolo posizione: griglia 3x3
            col = i % 3
            row = 2 - (i // 3)
            
            # x, y partono dal basso a sinistra
            # Puoi cambiare 30, 50 per spostare l'intero blocco di carte
            x = 30 + (col * card_w)
            y = 50 + (row * card_h)
            
            c.drawImage(img, x, y, width=card_w, height=card_h)
        except Exception:
            continue

    c.showPage()
    c.save()
    pdf_buffer.seek(0)
    return Response(content=pdf_buffer.read(), media_type="application/pdf")