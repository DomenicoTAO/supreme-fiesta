from fastapi import FastAPI, Response
from pydantic import BaseModel
import json
import os
from typing import List, Dict
import requests
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import io

DATA_FILE = "data.json"

app = FastAPI()

class PrintRequest(BaseModel):
    image_urls: List[str]

@app.post("/generate-pdf")
async def generate_pdf(request: PrintRequest):
    pdf_buffer = io.BytesIO()
    # A4 è 595x842 punti
    c = canvas.Canvas(pdf_buffer, pagesize=A4)

    # Larghezza e altezza totale A4
    page_w, page_h = A4

    # Dimensioni carta (es. 63mm x 88mm = 178pt x 250pt circa)
    # Regola questi valori se le tue carte hanno dimensioni diverse
    card_w = 178
    card_h = 250

    # Calcolo per centrare la griglia 3x3
    grid_w = card_w * 3
    grid_h = card_h * 3    
    offset_x = (page_w - grid_w) / 2
    offset_y = (page_h - grid_h) / 2

    for i, url in enumerate(request.image_urls):
        # Ogni 9 immagini, se non è la prima, aggiungiamo una nuova pagina
        if i > 0 and i % 9 == 0:
            c.showPage()

        try:
            response = requests.get(url, timeout=5)
            img = ImageReader(io.BytesIO(response.content))

            # Calcolo posizione all'interno della pagina corrente (modulo 9)
            pos_in_page = i % 9
            col = pos_in_page % 3
            row = 2 - (pos_in_page // 3)

            # x, y partono dal basso a sinistra
            # Puoi cambiare 30, 50 per spostare l'intero blocco di carte
            x = offset_x + (col * card_w)
            y = offset_y + (row * card_h)

            c.drawImage(img, x, y, width=card_w, height=card_h)
        except Exception:
            continue

    c.showPage()
    c.save()
    pdf_buffer.seek(0)
    return Response(content=pdf_buffer.read(), media_type="application/pdf")

# Funzione helper per caricare/salvare
def load_data():
    # Se il file non esiste, lo crea vuoto e restituisce un dizionario vuoto
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)
        return {}
    # Se esiste, lo legge normalmente
    with open(DATA_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            # Gestisce il caso in cui il file esiste ma è corrotto/vuoto
            return {}

def save_data(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f)

@app.post("/save-list")
async def save_list(item: Dict):
    # item conterrà: {"name": "...", "color": "...", "vcm": "...", "urls": [...]}
    data = load_data()
    name = item.get("name")
    # Controllo se il nome è già presente nel dizionario (data)
    if name in data:
        return {"status": "error", "message": "Il nome della lista esiste già!"}, 400
    # Se non esiste, procediamo al salvataggio
    data[name] = {
        "color": item.get("color"),
        "vcm": item.get("vcm"),
        "urls": item.get("urls")
    }
    save_data(data)
    return {"status": "success"}

@app.get("/list-names")
async def list_names():
    data = load_data()
    # Restituiamo una lista di oggetti con nome e tipo
    return [{"name": k, "color": v["color"], "vcm": v["vcm"]} for k, v in data.items()]

@app.get("/get-list")
async def get_list(name: str):
    data = load_data()
    # Controlla se la lista esiste
    if name in data:
        return data[name]  # Restituisce il dizionario {"type": "...", "urls": [...]}
    else:
        return {"error": "Lista non trovata"}, 404