from fastapi import FastAPI, HTTPException, Query
import requests

app = FastAPI(title="YouTube Downloader API")

# Liste d'instances Piped pour la redondance
PIPED_INSTANCES = [
    "https://pipedapi.kavin.rocks",
    "https://pipedapi.adminforge.de",
    "https://pipedapi.leptons.xyz"
]

def get_video_id(url: str):
    if "v=" in url:
        return url.split("v=")[-1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("/")[-1].split("?")[0]
    return url

@app.get("/")
def home():
    return {"message": "API de téléchargement active. Utilisez /extract?url=..."}

@app.get("/extract")
def extract_video(url: str = Query(..., description="URL de la vidéo YouTube")):
    video_id = get_video_id(url)
    
    # Essayer les instances une par une si l'une échoue
    for instance in PIPED_INSTANCES:
        try:
            response = requests.get(f"{instance}/streams/{video_id}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                return {
                    "title": data.get("title"),
                    "duration": data.get("duration"),
                    "thumbnail": data.get("thumbnailUrl"),
                    "uploader": data.get("uploader"),
                    "views": data.get("views"),
                    "video_formats": [
                        {
                            "quality": f.get("quality"),
                            "format": f.get("format"),
                            "url": f.get("url"),
                            "fps": f.get("fps")
                        } for f in data.get("videoStreams", [])
                    ],
                    "audio_formats": [
                        {
                            "bitrate": a.get("bitrate"),
                            "format": a.get("format"),
                            "url": a.get("url")
                        } for f in data.get("audioStreams", [])
                    ]
                }
        except:
            continue
            
    raise HTTPException(status_code=500, detail="Toutes les instances Piped sont injoignables.")
