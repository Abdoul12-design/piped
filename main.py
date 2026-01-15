from fastapi import FastAPI, HTTPException, Query
import requests
import re

app = FastAPI(title="Piped API Proxy")

INSTANCES = [
    "https://pipedapi.kavin.rocks",
    "https://pipedapi.adminforge.de",
    "https://pipedapi.leptons.xyz"
]

def extract_video_id(url: str):
    """Extrait l'ID d'une vidéo YouTube de manière robuste."""
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    return match.group(1) if match else None

@app.get("/")
def read_root():
    return {"status": "online", "endpoints": ["/extract", "/search"]}

@app.get("/extract")
def extract(url: str = Query(..., description="URL de la vidéo")):
    video_id = extract_video_id(url)
    if not video_id:
        raise HTTPException(status_code=400, detail="ID de vidéo invalide")
    
    for instance in INSTANCES:
        try:
            # On interroge l'endpoint streams de Piped
            res = requests.get(f"{instance}/streams/{video_id}", timeout=10)
            if res.status_code == 200:
                data = res.json()
                return {
                    "title": data.get("title"),
                    "duration": data.get("duration"),
                    "thumbnail": data.get("thumbnailUrl"),
                    "uploader": data.get("uploader"),
                    "video_formats": data.get("videoStreams"),
                    "audio_formats": data.get("audioStreams")
                }
        except Exception:
            continue
    
    raise HTTPException(status_code=500, detail="Aucune instance Piped n'a pu traiter la demande")

@app.get("/search")
def search(q: str = Query(..., description="Mots-clés de recherche")):
    for instance in INSTANCES:
        try:
            # On interroge l'endpoint search de Piped
            res = requests.get(f"{instance}/search", params={"q": q, "filter": "videos"}, timeout=10)
            if res.status_code == 200:
                return res.json().get("items", [])
        except Exception:
            continue
            
    raise HTTPException(status_code=500, detail="Erreur lors de la recherche")
