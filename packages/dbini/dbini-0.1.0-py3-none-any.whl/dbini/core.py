import os, json, uuid
from pathlib import Path

class Collection:
    def __init__(self, path: Path):
        self.path = path
        self.path.mkdir(parents=True, exist_ok=True)

    def add(self, data: dict) -> str:
        cid = str(uuid.uuid4())
        with open(self.path / f"{cid}.json", "w") as f:
            json.dump(data, f, indent=2)
        return cid

    def find(self, query: dict):
        for file in self.path.glob("*.json"):
            with open(file) as f:
                doc = json.load(f)
            if all(k in doc and doc[k] == v for k, v in query.items()):
                yield doc

    def update(self, cid: str, updates: dict):
        path = self.path / f"{cid}.json"
        if not path.exists():
            return False
        with open(path) as f:
            doc = json.load(f)
        doc.update(updates)
        with open(path, "w") as f:
            json.dump(doc, f, indent=2)
        return True


class DBini:
    def __init__(self, project_path: str):
        self.root = Path(project_path)
        (self.root / "data/collections").mkdir(parents=True, exist_ok=True)
        (self.root / "files").mkdir(parents=True, exist_ok=True)

    def collection(self, name: str) -> Collection:
        return Collection(self.root / "data/collections" / name)

    def save_file(self, filepath: str) -> str:
        fid = str(uuid.uuid4())
        ext = os.path.splitext(filepath)[1]
        dest = self.root / "files" / f"{fid}{ext}"
        with open(filepath, "rb") as src, open(dest, "wb") as dst:
            dst.write(src.read())
        return fid
