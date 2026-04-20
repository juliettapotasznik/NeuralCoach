# NeuralCoach

Aplikacja do analizy ćwiczeń fizycznych przy pomocy AI (analiza pozy, feedback, plany treningowe i dieta).

## Struktura projektu

```
NeuralCoach/
├── backend/          # FastAPI (port 8002)
├── frontend/frontend/ # Next.js (port 3000)
├── ai/
│   ├── openvino/     # Ekstrakcja pozy z wideo (port 8001)
│   ├── lstm_autoencoder/ # Analiza LSTM (port 8003)
│   └── training_plan/   # Generator planów treningowych (port 8004)
└── docker-compose.yml
```

---

## Uruchomienie (tryb lokalny — bez AI)

Wymagania: **Python 3.11**, **Node.js**

### 1. Backend (FastAPI)

Otwórz PowerShell i uruchom:

```powershell
cd C:\Users\Asus\Documents\GitHub\NeuralCoach\backend
python -m pip install python-magic-bin
python -m pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

Backend dostępny pod: http://localhost:8002  
Dokumentacja API (Swagger): http://localhost:8002/docs

### 2. Frontend (Next.js)

Otwórz **nowe** okno PowerShell:

```powershell
cd C:\Users\Asus\Documents\GitHub\NeuralCoach\frontend\frontend
npm run dev
```

Frontend dostępny pod: http://localhost:3000

---

## Uruchomienie (tryb pełny — z Docker i AI)

Wymagania: **Docker Desktop**

### 1. Utwórz plik `.env` w katalogu `backend/`

```env
GROQ_API_KEY=twoj_klucz_groq
POSTGRES_USER=neuralcoach
POSTGRES_PASSWORD=neuralcoach_password
POSTGRES_DB=neuralcoach_db
SECRET_KEY=twoj_tajny_klucz
```

### 2. Uruchom wszystko przez Docker Compose

```powershell
cd C:\Users\Asus\Documents\GitHub\NeuralCoach
docker compose up --build
```

| Serwis | URL |
|---|---|
| Frontend (Next.js) | http://localhost:3000 |
| Backend (FastAPI) | http://localhost:8002 |
| OpenVINO (AI) | http://localhost:8001 |
| LSTM Autoencoder (AI) | http://localhost:8003 |
| Training Plan (AI) | http://localhost:8004 |
| MailHog (maile) | http://localhost:8025 |

---

## Maile (rejestracja, reset hasła)

Maile nie wychodzą na zewnątrz — przechwytuje je **MailHog**.  
Podejrzyj je pod: http://localhost:8025

W trybie lokalnym (bez Dockera) uruchom samego MailHoga:
```powershell
docker compose up mailhog
```

---

## Znane problemy

### `ModuleNotFoundError: No module named 'magic'`
Na Windows zainstaluj `python-magic-bin` zamiast `python-magic`:
```powershell
python -m pip install python-magic-bin
```

### Błąd venv wskazuje na nieistniejący folder
Użyj systemowego Pythona (`python -m pip ...`) zamiast przez venv.

### `npm install` — konflikt peer dependencies
Paczki są już zainstalowane w `node_modules`, pomiń ten błąd i uruchom bezpośrednio `npm run dev`.
