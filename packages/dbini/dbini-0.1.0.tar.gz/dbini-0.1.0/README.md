<div align="center">

# dbini

Zero-config NoSQL backend database as a Python package

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge\&logo=python\&logoColor=white)
![PyPI](https://img.shields.io/pypi/v/dbini?style=for-the-badge)
[![Stars](https://img.shields.io/github/stars/Binidu01/dbini?style=for-the-badge\&logo=github)](https://github.com/Binidu01/dbini/stargazers)
[![Forks](https://img.shields.io/github/forks/Binidu01/dbini?style=for-the-badge\&logo=github)](https://github.com/Binidu01/dbini/network/members)
[![Issues](https://img.shields.io/github/issues/Binidu01/dbini?style=for-the-badge\&logo=github)](https://github.com/Binidu01/dbini/issues)
[![License](https://img.shields.io/github/license/Binidu01/dbini?style=for-the-badge)](https://github.com/Binidu01/dbini/blob/main/LICENSE)

</div>

---

## 📋 Table of Contents

* [🚀 Features](#-features)
* [🛠️ Installation](#-installation)
* [💻 Usage](#-usage)
* [🗂 Project Structure](#-project-structure)
* [🏗️ Built With](#-built-with)
* [🤝 Contributing](#-contributing)
* [📄 License](#-license)
* [📞 Contact](#-contact)
* [🙏 Acknowledgments](#-acknowledgments)

---

## 🚀 Features

* ✨ Zero-config backend database
* 🔥 Store JSON documents and files inside the project folder
* 🛡️ Secure atomic writes for data and files
* 🌐 REST API & WebSocket support for any language
* 📦 Self-contained Python package
* ⚡ Works in Python 3.9+

---

## 🛠️ Installation

### Prerequisites

* Python 3.9+
* pip

### Quick Start

```bash
# Clone the repository
git clone https://github.com/Binidu01/dbini.git

# Navigate to project directory
cd dbini

# (Optional) Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package locally
pip install .

# Run a test script
python examples/test_dbini.py
```

---

## 💻 Usage

### As Local Database

```python
from dbini import DBini

db = DBini("myproject")
user_id = db.collection("users").add({"name": "Alice", "age": 22})
print("Created user:", user_id)

# Query documents
for doc in db.collection("users").find({"age": 22}):
    print(doc)

# Save image/file
file_id = db.save_file("avatar.png")
db.collection("users").update(user_id, {"avatar": file_id})
```

### As API Server

```python
from dbini.server import DBiniServer

server = DBiniServer("myproject")
server.serve(port=8080)
```

**Endpoints Example:**

* `POST /v1/{collection}/documents` → Create document
* `POST /v1/files` → Upload file
* All data stays inside the project folder.

---

## 🗂 Project Structure

Example project layout when using `dbini`:

```
myproject/
 ├─ data/
 │   └─ collections/
 │       └─ users/
 │           ├─ <uuid>.json
 ├─ files/
 │   └─ <uuid>.png
 └─ meta/
     └─ project.json
```

* `collections/` → stores JSON documents per collection
* `files/` → stores images or other files uploaded
* `meta/project.json` → optional project settings

---

## 🏗️ Built With

* **Python** - Core language
* **FastAPI** - REST API server
* **Uvicorn** - ASGI server

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the Project
2. Create your Feature Branch `git checkout -b feature/AmazingFeature`
3. Commit your Changes `git commit -m "Add AmazingFeature"`
4. Push to the Branch `git push origin feature/AmazingFeature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file.

---

## 📞 Contact

**Binidu01** - [GitHub Profile](https://github.com/Binidu01)

Project Link: [https://github.com/Binidu01/dbini](https://github.com/Binidu01/dbini)

---

## 🙏 Acknowledgments

* Thanks to all contributors who helped this project grow
* Built with ❤️ and lots of ☕
* Inspired by Firebase and modern local-first backends

---

<div align="center">

**[⬆ Back to Top](#dbini)**

Made with ❤️ by [Binidu01](https://github.com/Binidu01)

⭐ Star this repo if you find it useful!

</div>
