SENIOREASE FINAL - FRONTEND + FASTAPI BACKEND

Folder contents:
- index.html / fornt.html = your uploaded SeniorEase frontend
- css/style.css = restored styling
- js/*.js = restored frontend modules + backend connection
- main.py = FastAPI backend
- requirements.txt = Python dependencies

RUN:
1) Open PowerShell in this folder.
2) python -m venv venv
3) venv\Scripts\activate
4) pip install -r requirements.txt
5) python -m uvicorn main:app --reload

Open a SECOND PowerShell in this same folder:
6) python -m http.server 8080

Then open:
http://localhost:8080/index.html

Backend API docs:
http://127.0.0.1:8000/docs

The browser app creates a local backend user automatically on first load.
Emergency calling itself is performed by the device/browser using tel: links where supported; the backend records the emergency event and location.
Hospital results in the backend are demo data and should be replaced with a verified live hospital/Maps service before real deployment.
