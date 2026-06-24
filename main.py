from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import requests
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import io
from fastapi.responses import Response

app = FastAPI()

class PrintRequest(BaseModel):
    image_urls: List[str]

@app.post("/generate-pdf")
async def generate_pdf(request: PrintRequest):
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    w, h = A4
    
    # 3x3 griglia
    cell_w = w / 3
    cell_h = h / 3
    
    for i, url in enumerate(request.image_urls):
        if i >= 9: break
        try:
            response = requests.get(url, timeout=5)
            img = ImageReader(io.BytesIO(response.content))
            
            # Posizionamento (senza margini per attaccare le immagini)
            col = i % 3
            row = 2 - (i // 3)
            x = col * cell_w
            y = row * cell_h
            
            c.drawImage(img, x, y, width=cell_w, height=cell_h)
        except Exception as e:
            continue

    c.showPage()
    c.save()
    pdf_buffer.seek(0)
    return Response(content=pdf_buffer.read(), media_type="application/pdf")