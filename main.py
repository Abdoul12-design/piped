import re
import requests
import random
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="YouTube Multi-Source API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sélection des instances les plus stables de ta liste
INSTANCES = [
    "https://pipedapi.tokhmi.xyz",
    "https://pipedapi.moomoo.me",
    "https://api-piped.mha.fi",
    "https://piped-api.garudalinux.org",
    "https://pipedapi.leptons.xyz",
    "https://piped-api.lunar.icu",
    "https://pipedapi.r4fo.com",
    "https://pipedapi.nosebs.ru",
    "https://pa.il.ax",
    "https://api.piped.projectsegfau.lt",
    "https://pipedapi.astartes.nl",
    "https://pipedapi.osphost.fi"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
}

def extract_id(url: str):
    pattern = r"(?:v=|\/|be\/)([0-9A-Za-z_-]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None

@app.get("/extract")
def extract(url: str = Query(..., description="URL YouTube")):
    video_id = extract_id(url)
    if not video_id:
        raise HTTPException(status_code=400, detail="URL YouTube invalide")

    # On mélange la liste pour ne pas toujours taper sur la même instance
    random.shuffle(INSTANCES)
    
    # On tente les 5 premières instances sélectionnées au hasard
    for instance in INSTANCES[:5]:
        try:
            response = requests.get(
                f"{instance}/streams/{video_id}", 
                headers=HEADERS, 
                timeout=7
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "source_used": instance,
                    "title": data.get("title"),
                    "duration": data.get("duration"),
                    "thumbnail": data.get("thumbnailUrl"),
                    "video": data.get("videoStreams"),
                    "audio": data.get("audioStreams")
                }
        except:
            continue
            
    raise HTTPException(
        status_code=503, 
        detail="Toutes les instances ont échoué. YouTube bloque temporairement les accès serveurs."
    )
