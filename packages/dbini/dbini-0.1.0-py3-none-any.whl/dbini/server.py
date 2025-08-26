import json, uuid
from pathlib import Path
from fastapi import FastAPI, UploadFile
import uvicorn

class DBiniServer:
    def __init__(self, project_path: str):
        self.root = Path(project_path)
        self.root.mkdir(parents=True, exist_ok=True)

    def serve(self, port: int = 8080):
        app = FastAPI()

        @app.post("/v1/{collection}/documents")
        async def create_doc(collection: str, data: dict):
            cid = str(uuid.uuid4())
            path = self.root / "data/collections" / collection
            path.mkdir(parents=True, exist_ok=True)
            with open(path / f"{cid}.json", "w") as f:
                json.dump(data, f)
            return {"id": cid, **data}

        @app.post("/v1/files")
        async def upload_file(file: UploadFile):
            fid = str(uuid.uuid4())
            path = self.root / "files"
            path.mkdir(parents=True, exist_ok=True)
            dest = path / f"{fid}{Path(file.filename).suffix}"
            with open(dest, "wb") as f:
                f.write(await file.read())
            return {"fileId": fid}

        uvicorn.run(app, port=port)
