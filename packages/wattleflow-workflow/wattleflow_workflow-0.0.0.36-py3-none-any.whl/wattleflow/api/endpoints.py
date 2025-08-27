from datetime import datetime
import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from wattleflow.api.endpoints.model.youtube import YoutubeTranscriptModel

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter("%(levelname)s:    %(message)s"))

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.addHandler(console_handler)

app = FastAPI()


@app.get("/status")
async def root():
    log.info(" end point: status")

    return {
        "timestamp": datetime.now().isoformat(),
        "message": "Youtube api is running!",
    }


@app.get("/api/endpoints/youtube/{url}")
async def translate(url: str):
    log.debug(f"/api/endpoints/youtube/{url}")
    try:
        if url.endswith("ico"):
            return {"content": "Unsupported type"}

        uri = f"https://www.youtube.com/watch?v={url}"
        log.info("uri: %s", uri)

        model = YoutubeTranscriptModel(uri, level=logging.DEBUG)
        return model.view()

    except Exception as e:
        log.error("Error: %", str(e))
        raise HTTPException(status_code=500, detail=e) from e


uvicorn.run(app, host="localhost", port=8001)
