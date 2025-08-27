# src/dbini/server.py
"""
DBini REST + WebSocket server.

Features:
- CRUD endpoints for documents
- Query endpoint
- File upload / download
- List collections & files
- WebSocket realtime: tails wal/append.log and pushes new WAL entries to subscribers

Usage:
    from dbini.server import serve
    serve(project_root="myproject", host="127.0.0.1", port=8080)

Or run:
    python -m dbini.server  # will start default project "dbini_project"
"""

from __future__ import annotations
import os
import json
import tempfile
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, UploadFile, File, Body, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .core import DBini  # assumes core.py defines DBini
from .core import utcnow_iso

# ----------------- Config / helpers -----------------
DEFAULT_PROJECT = "dbini_project"

def load_project_config(project_root: Path) -> Dict[str, Any]:
    cfg_path = project_root / "meta" / "project.json"
    if not cfg_path.exists():
        return {}
    try:
        return json.loads(cfg_path.read_text(encoding="utf-8"))
    except Exception:
        return {}

async def validate_api_key(project_root: Path, provided_key: Optional[str]) -> bool:
    """
    Optional lightweight API key check:
    If meta/project.json contains {"api_key": "..."} then provided_key must match.
    If no api_key set, allow access.
    """
    cfg = load_project_config(project_root)
    required = cfg.get("api_key")
    if not required:
        return True
    return provided_key == required

def require_key_dependency(project_root: Path):
    """
    Returns a FastAPI dependency function bound to project_root
    that checks X-Api-Key header.
    """
    async def _dep(x_api_key: Optional[str] = None):
        ok = await validate_api_key(project_root, x_api_key)
        if not ok:
            raise HTTPException(status_code=401, detail="Invalid API key")
    return _dep

# ----------------- App factory -----------------
def create_app(project_root: str | Path = DEFAULT_PROJECT, *, allow_origins: Optional[List[str]] = None) -> FastAPI:
    project_root = Path(project_root)
    app = FastAPI(title="dbini", version="0.1")

    # CORS
    origins = allow_origins or ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize DB instance and dependency
    db = DBini(project_root)
    require_key = require_key_dependency(project_root)

    # --------- Endpoints ----------

    @app.get("/v1/health")
    async def health():
        valid, bad_line, msg = db.verify_wal()
        return {"status": "ok", "wal_valid": valid, "wal_bad_line": bad_line, "wal_msg": msg}

    # List collections
    @app.get("/v1/collections")
    async def list_collections(dep=Depends(require_key)):
        return {"collections": db.list_collections()}

    # Create document
    @app.post("/v1/collections/{collection}/documents")
    async def create_document(collection: str, payload: Dict[str, Any] = Body(...), dep=Depends(require_key)):
        try:
            doc_id = db.add_document(collection, payload)
            doc = db.get_document(collection, doc_id)
            return {"id": doc_id, "doc": doc}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Get document
    @app.get("/v1/collections/{collection}/documents/{doc_id}")
    async def get_document(collection: str, doc_id: str, dep=Depends(require_key)):
        doc = db.get_document(collection, doc_id)
        if doc is None:
            raise HTTPException(status_code=404, detail="not found")
        return {"id": doc_id, "doc": doc}

    # Update document (partial)
    @app.patch("/v1/collections/{collection}/documents/{doc_id}")
    async def patch_document(collection: str, doc_id: str, updates: Dict[str, Any] = Body(...), dep=Depends(require_key)):
        ok = db.update_document(collection, doc_id, updates)
        if not ok:
            raise HTTPException(status_code=404, detail="not found")
        return {"id": doc_id, "updated_at": utcnow_iso()}

    # Delete document
    @app.delete("/v1/collections/{collection}/documents/{doc_id}")
    async def delete_document(collection: str, doc_id: str, dep=Depends(require_key)):
        ok = db.delete_document(collection, doc_id)
        if not ok:
            raise HTTPException(status_code=404, detail="not found")
        return {"id": doc_id, "deleted": True}

    # Query (simple filters)
    @app.post("/v1/collections/{collection}:query")
    async def query_collection(collection: str, body: Dict[str, Any] = Body(...), dep=Depends(require_key)):
        """
        Body example:
        { "filters": {"age": {"$gte": 18}}, "limit": 50 }
        """
        filters = body.get("filters")
        limit = body.get("limit")
        try:
            results = db.find(collection, filters=filters, limit=limit)
            return {"count": len(results), "results": results}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    # Upload file (multipart)
    @app.post("/v1/files")
    async def upload_file(file: UploadFile = File(...), dep=Depends(require_key)):
        # write to temp, then call db.save_file
        suffix = Path(file.filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp_path = Path(tmp.name)
            content = await file.read()
            tmp.write(content)
            tmp.flush()
            os.fsync(tmp.fileno())
        try:
            file_id = db.save_file(tmp_path)
            meta = {"fileId": file_id}
            return meta
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            try:
                tmp_path.unlink(missing_ok=True)
            except Exception:
                pass

    # Download file (stream)
    @app.get("/v1/files/{file_id}")
    async def download_file(file_id: str, dep=Depends(require_key)):
        path = db.get_file_path(file_id)
        if not path:
            raise HTTPException(status_code=404, detail="file not found")
        return FileResponse(path, media_type="application/octet-stream", filename=Path(path).name)

    # File metadata
    @app.get("/v1/files/{file_id}/meta")
    async def file_meta(file_id: str, dep=Depends(require_key)):
        files = db.list_files()
        for f in files:
            if f["id"] == file_id:
                return f
        raise HTTPException(status_code=404, detail="meta not found")

    # List files
    @app.get("/v1/files")
    async def list_files(dep=Depends(require_key)):
        files = db.list_files()
        return {"count": len(files), "files": files}

    # Get collection documents (all)
    @app.get("/v1/collections/{collection}/documents")
    async def get_all_docs(collection: str, dep=Depends(require_key)):
        docs = db.find(collection, filters=None)
        return {"count": len(docs), "results": docs}

    # ---------------- WebSocket realtime ----------------
    # This simple implementation tails wal/append.log and sends new JSON objects to connected clients.
    @app.websocket("/v1/ws/{collection}")
    async def websocket_wal(websocket: WebSocket, collection: str, x_api_key: Optional[str] = None):
        # Note: WS clients cannot use Depends easily, so we do a simple inline key check if needed
        allow = await validate_api_key(project_root, x_api_key)
        if not allow:
            await websocket.close(code=4401)
            return

        await websocket.accept()
        wal_file = db._wal_file
        # open wal for reading in text mode and seek to EOF to only send new events
        try:
            with open(wal_file, "rb") as f:
                f.seek(0, os.SEEK_END)
                while True:
                    line = f.readline()
                    if not line:
                        # nothing new, sleep a bit
                        await asyncio.sleep(0.2)
                        continue
                    try:
                        obj = json.loads(line.decode("utf-8"))
                    except Exception:
                        # skip corrupted line
                        continue
                    # If subscription is for a specific collection filter by that
                    if obj.get("collection") and obj.get("collection") != collection:
                        continue
                    # send the wal event
                    await websocket.send_json(obj)
        except WebSocketDisconnect:
            return
        except Exception:
            # if wal doesn't exist yet or other error, keep connection alive and wait
            try:
                while True:
                    await asyncio.sleep(1)
            except WebSocketDisconnect:
                return

    # ---------------- Shutdown handler ----------------
    @app.on_event("shutdown")
    async def shutdown_event():
        try:
            db.close()
        except Exception:
            pass

    # attach db instance for advanced usage
    app.state.db = db
    app.state.project_root = project_root

    return app

# ----------------- Run helper -----------------
def serve(project_root: str = DEFAULT_PROJECT, host: str = "127.0.0.1", port: int = 8080, allow_origins: Optional[List[str]] = None):
    app = create_app(project_root, allow_origins=allow_origins)
    uvicorn.run(app, host=host, port=port)

# ----------------- Module entrypoint -----------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run dbini server")
    parser.add_argument("--project", "-p", default=DEFAULT_PROJECT, help="project folder")
    parser.add_argument("--host", default="127.0.0.1", help="host")
    parser.add_argument("--port", "-P", default=8080, type=int, help="port")
    args = parser.parse_args()
    serve(args.project, host=args.host, port=args.port)
