Here’s a concise, cross-platform guide for running your backend, frontend, and OCR microservice—including all required installations.

---

# Contact Management System: Local Development Guide

## 1. Prerequisites

- **Python 3.10+** (recommended: 3.11)
- **Node.js 18+** (for frontend)
- **npm** (comes with Node.js)
- **conda** (optional, for isolated Python environments)
- **Tesseract-OCR** (for OCR microservice)

---

## 2. Clone the Repository

```sh
git clone <your-repo-url>
cd contact-management
```

---

## 3. Python Environment Setup (Backend & OCR)

### **A. Create and Activate a Virtual Environment**

#### Using conda (recommended for cross-platform):
```sh
conda create -n contact-management python=3.11 -y
conda activate contact-management
```
#### Or using venv (Python built-in):
```sh
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

---

### **B. Install Python Dependencies**

#### Backend:
```sh
pip install -r backend/requirements.txt
```
#### OCR Microservice:
```sh
pip install -r ocr-service/requirements.txt
```

---

### **C. Install Tesseract-OCR (System Dependency)**

#### **Windows:**
- Download and install from [UB Mannheim builds](https://github.com/UB-Mannheim/tesseract/wiki).
- Add the install path (e.g., `C:\Program Files\Tesseract-OCR`) to your system PATH.

#### **macOS:**
```sh
brew install tesseract
```

#### **Linux (Debian/Ubuntu):**
```sh
sudo apt-get update
sudo apt-get install tesseract-ocr
```

---

### **D. Download spaCy English Model**

```sh
python -m spacy download en_core_web_sm
```

---

## 4. Environment Variables

- Copy or create `.env` files in `backend/` and `ocr-service/` as needed.
- Set your OpenAI API key and other secrets in these files.

Example for `backend/.env`:
```
DATABASE_URL=sqlite:///./contact_db.sqlite
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
OPENAI_API_KEY=your_openai_api_key_here
```

---

## 5. Start the Services

### **A. Start the Backend**

```sh
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### **B. Start the OCR Microservice**

```sh
cd ocr-service
uvicorn app:app --host 0.0.0.0 --port 8001 --reload
```

### **C. Start the Frontend**

```sh
cd frontend
npm install
npm run dev
```
- The frontend will be available at [http://localhost:5173](http://localhost:5173).

---

## 6. Usage

- Access the frontend in your browser.
- Log in with your admin credentials.
- Upload files or images to extract contacts.
- Use batch delete, export, and other features.

---

## 7. Troubleshooting

- **CORS errors:** Ensure `ALLOWED_ORIGINS` in your backend `.env` includes your frontend URL.
- **OCR errors:** Make sure Tesseract is installed and in your PATH.
- **LLM errors:** Ensure your OpenAI API key is valid and the model is available.
- **spaCy errors:** Ensure the `en_core_web_sm` model is downloaded.

---

## 8. Cross-Platform Notes

- All commands work on Windows, macOS, and Linux (adjust path separators and activation commands as needed).
- Use `conda` or `venv` for Python environments.
- Use `npm` for frontend dependencies.

---