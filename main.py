import re
import requests
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="YouTube Downloader API - Piped Edition")

# Autoriser les requêtes depuis n'importe quel domaine (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Liste d'instances Piped variées pour maximiser les chances de succès
INSTANCES = [
    "https://pipedapi.adminforge.de",
    "https://api.piped.yt",
    "https://pipedapi.official-halal.site",
    "https://pipedapi.astartes.nl",
    "https://pipedapi.berrytube.space",
    "https://pipedapi.kavin.rocks"
]

# Simuler un vrai navigateur pour éviter les blocages
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def extract_video_id(url: str):
    """Extrait l'ID de la vidéo proprement peu importe le format du lien."""
    pattern = r"(?:v=|\/|be\/)([0-9A-Za-z_-]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None

@app.get("/")
def home():
    return {
        "status": "online",
        "message": "API opérationnelle",
        "usage": "/extract?url=[LIEN_YOUTUBE]"
    }

@app.get("/extract")
def extract(url: str = Query(..., description="L'URL de la vidéo YouTube")):
    video_id = extract_video_id(url)
    if not video_id:
        raise HTTPException(status_code=400, detail="URL YouTube invalide")
    
    # On essaie chaque instance jusqu'à ce qu'une réponde
    for instance in INSTANCES:
        try:
            # Appel à l'endpoint streams de Piped
            response = requests.get(
                f"{instance}/streams/{video_id}", 
                headers=HEADERS, 
                timeout=8 # Timeout raisonnable
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Filtrage et organisation des données
                return {
                    "info": {
                        "title": data.get("title"),
                        "duration": data.get("duration"),
                        "thumbnail": data.get("thumbnailUrl"),
                        "uploader": data.get("uploader"),
                        "views": data.get("views")
                    },
                    "video": [
                        {
                            "quality": f.get("quality"),
                            "format": f.get("format"),
                            "url": f.get("url"),
                            "size": f.get("contentLength")
                        } for f in data.get("videoStreams", [])
                    ],
                    "audio": [
                        {
                            "bitrate": a.get("bitrate"),
                            "format": a.get("format"),
                            "url": a.get("url")
                        } for a in data.get("audioStreams", [])
                    ]
                }
        except Exception:
            continue # Passer à l'instance suivante en cas d'erreur
            
    raise HTTPException(
        status_code=500, 
        detail="Toutes les instances Piped sont saturées. Réessayez dans un instant."
    )

@app.get("/search")
def search(q: str = Query(..., description="Mots-clés de la recherche")):
    for instance in INSTANCES:
        try:
            response = requests.get(
                f"{instance}/search", 
                params={"q": q, "filter": "videos"}, 
                headers=HEADERS, 
                timeout=8
            )
            if response.status_code == 200:
                return response.json().get("items", [])
        except:
            continue
    raise HTTPException(status_code=500, detail="Recherche impossible pour le moment")
