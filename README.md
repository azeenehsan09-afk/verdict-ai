# ⚖️ Verdict — AI Decision Courtroom

**Every decision deserves a fair trial.**

Verdict is an AI-powered decision-making platform that turns difficult personal decisions into an interactive courtroom experience. Instead of receiving a single AI-generated answer, users get multiple perspectives, challenge the Judge's reasoning, and receive a final verdict based on their responses.

## ✨ Features

- **Three AI Perspectives:** Hear arguments from an Optimist, Skeptic, and Realist.
- **AI Judge:** Evaluates the arguments and delivers an initial verdict.
- **Appeal System:** Challenge the Judge with additional information or counterarguments.
- **Reconsideration:** The Judge reviews the appeal and may revise the verdict.
- **Final Reflection:** Answer an overlooked question before the trial concludes.
- **Final Verdict:** Receive a final conclusion, supporting reasoning, and a practical next step.

## ⚙️ How It Works

1. **Present Your Decision** — Enter a decision you are struggling with.
2. **Hear Both Sides** — Three AI personas analyze the situation from different perspectives.
3. **Receive the Verdict** — The AI Judge evaluates the arguments and provides an initial recommendation.
4. **Challenge the Judge** — Submit an appeal if you disagree or have additional information.
5. **Reflect** — Answer the Judge's overlooked question.
6. **Get the Final Verdict** — Receive the final evaluation and a practical next step.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| HTML5 | Website structure |
| CSS3 | Styling and responsive design |
| JavaScript | Frontend interactions and API requests |
| Python | Backend logic |
| Flask | API development |
| Google Gemini API | AI-powered analysis and verdicts |

## 📁 Project Structure

```text
verdict-ai/
│
├── index.html
├── style.css
├── script.js
├── app.py
├── .env
├── .gitignore
└── venv/
```

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/azeenehsan09-afk/verdict-ai.git
cd verdict-ai
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

**Windows PowerShell**
```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install flask flask-cors google-genai python-dotenv
```

### 4. Configure your API key

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

Replace `your_api_key_here` with your own Google Gemini API key.

**Important:** Never upload your `.env` file or expose your API key publicly.

### 5. Run the backend

```bash
python app.py
```

The Flask backend will run at:

```text
http://127.0.0.1:5000
```

### 6. Launch the frontend

Open `index.html` using the VS Code Live Server extension.

## 🎯 Project Goal

Verdict explores how AI can support better decision-making by presenting multiple viewpoints rather than simply giving users a direct answer.

It encourages critical thinking, reflection, and informed choices while keeping the final decision in the user's hands.

## 👥 Contributors

- **Azeen Ehsan** — [GitHub](https://github.com/azeenehsan09-afk)

## 📜 License

This project is currently developed as a hackathon project. A license has not yet been selected.

---

**Verdict — Every decision deserves a fair trial. ⚖️**
