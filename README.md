# 🧪 AutoTest Agent

AutoTest Agent is an AI-powered developer tool that takes a Python code module and its intended use case, and then automatically generates and runs unit/integration tests using `pytest`. It is designed to accelerate test-driven development, boost code coverage, and improve overall code quality.

---

## 💡 The Problem & Solution

* **The Problem:** Developers often skip writing tests due to tight deadlines, complex mock setups, or lack of coverage expertise. This results in regression bugs in production, difficult code reviews, and fragile refactoring.
* **The Solution:** AutoTest Agent automates the entire process. Paste your code, describe the intended behavior, and the AI agent automatically designs test suites, compiles them, executes them in an isolated test environment, and reports back the console output in real-time.

---

## 🔧 Key Features

1. **📥 Python Code Input** — Input any Python module (classes, helper functions, utility modules) to be tested.
2. **🗒️ Use Case Description** — Enter a short description of how the module *should* behave.
3. **🤖 AI Test Generator** — Leverages state-of-the-art LLMs (LLaMA 3.3 70B via Groq API) to generate detailed, syntactically valid `pytest` test suites, covering success states, boundary conditions, custom parameters, and exception handling.
4. **▶️ Isolated Test Runner** — Executes the generated tests on your Python code module inside a secure, temporary workspace using Python's subprocess modules.
5. **💬 Real-Time Feedback Loop** — View execution results, exit codes, and output logs. You can refine inputs and regenerate or rerun tests on the fly.
6. **☀️/🌙 Theme Toggle** — Beautiful Light and Dark mode options.

---

## 🧰 Technology Stack

* **Frontend**: React (JS, CSS, Vite)
* **Backend**: Python (Flask, Flask-CORS)
* **Test Engine**: Python `pytest`
* **AI Model**: LLaMA 3.3 70B Versatile (via Groq API)

---

## 🚀 How to Run Locally

### 1. Start the Backend Server

Open a terminal at the root of the project and navigate to the backend:

```bash
cd backend/
```

Activate the Python virtual environment:
* **Windows**:
  ```powershell
  .\venv\Scripts\activate
  ```
* **macOS/Linux**:
  ```bash
  source venv/bin/activate
  ```

Start the Flask server:
```bash
python app.py
```
The backend runs on `http://localhost:5000`. Make sure you have a valid `GROQ_API_KEY` set in your `backend/.env` file.

### 2. Start the Frontend Server

Open another terminal and navigate to the frontend:

```bash
cd frontend/
```

Install the Node dependencies:
```bash
npm install
```

Start the development server:
```bash
npm run dev
```
Open `http://localhost:5173` (or the URL displayed in the console) in your browser.
