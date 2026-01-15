import re
import requests
import random
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Piped API Ultimate Proxy")

# Autorise ton futur Frontend à appeler cette API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ta liste d'instances mise à jour
INSTANCES = [
    "https://pipedapi.tokhmi.xyz",
    "https://pipedapi.moomoo.me",
    "https://api-piped.mha.fi",
    "https://pipedapi.leptons.xyz",
    "https://pipedapi.astartes.nl",
    "https://pipedapi.adminforge.de"
]

def extract_id(url: str):
    pattern = r"(?:v=|\/|be\/)([0-9A-Za-z_-]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None

@app.get("/extract")
def extract(url: str = Query(..., description="Lien YouTube")):
    video_id = extract_id(url)
    if not video_id:
        raise HTTPException(status_code=400, detail="ID de vidéo introuvable")

    random.shuffle(INSTANCES)
    
    for instance in INSTANCES[:4]:
        try:
            # On utilise l'endpoint /streams/:videoId de la doc
            r = requests.get(f"{instance}/streams/{video_id}", timeout=8)
            
            if r.status_code == 200:
                data = r.json()
                
                # On structure la réponse selon la doc officielle que tu as envoyée
                return {
                    "title": data.get("title"),
                    "description": data.get("description"),
                    "uploader": data.get("uploader"),
                    "duration": data.get("duration"), # en secondes
                    "thumbnail": data.get("thumbnailUrl"),
                    "proxyUrl": data.get("proxyUrl"), # Utile pour contourner les blocages d'images
                    "video": [
                        {
                            "url": v.get("url"),
                            "quality": v.get("quality"),
                            "format": v.get("format"),
                            "codec": v.get("codec"),
                            "size_bytes": v.get("bitrate") # La doc dit: bitrate in bytes
                        } for v in data.get("videoStreams", [])
                    ],
                    "audio": [
                        {
                            "url": a.get("url"),
                            "format": a.get("format"),
                            "quality": a.get("quality")
                        } for a in data.get("audioStreams", [])
                    ],
                    "subtitles": data.get("subtitles", []) # Ajout des sous-titres
                }
        except:
            continue
            
    raise HTTPException(status_code=503, detail="Instances saturées ou YouTube bloque l'IP du serveur.")

# Nouveau : Endpoint de suggestions de recherche (basé sur ta doc)
@app.get("/suggest")
def suggest(q: str):
    for instance in INSTANCES:
        try:
            r = requests.get(f"{instance}/suggestions", params={"query": q}, timeout=5)
            if r.status_code == 200:
                return r.json() # Renvoie une liste de mots-clés
        except:
            continue
    return []
