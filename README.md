# 🤖 Auto Contract Interpreter – Gemini 1.5 + Tkinter PDF Analyzer

A desktop app that reads your PDF contracts, interprets them using Google Gemini AI, and highlights key legal insights like clauses, risks, unusual terms, and actionable advice. It even reads the results aloud!

---

## 🚀 Features

- 📂 Upload **any PDF contract**
- 🧠 AI-powered analysis using **Gemini 1.5 Flash**
- 📋 Extracts:
  - Key Clauses
  - Risks
  - Unusual Terms
  - Actionable Insights
- 💬 Ask custom questions about the contract
- 🔊 Built-in **Text-to-Speech (TTS)** playback
- 🖥️ Clean, responsive **Tkinter GUI**
- 📄 Scrollable output and copy-paste support

---

## 🛠️ Tech Stack

| Component        | Library/Tool            |
|------------------|--------------------------|
| GUI              | Tkinter                 |
| PDF Parsing      | PyMuPDF (`fitz`)        |
| AI Model         | Google Gemini 1.5 Flash |
| LLM Integration  | LangChain               |
| TTS Playback     | pyttsx3                 |
| Layout Styling   | ttk + custom placement  |

---

## 📦 Installation

> Requires Python 3.8+

### 1. Clone the repository

```bash
git clone https://github.com/your-username/auto-contract-interpreter.git
cd auto-contract-interpreter
```

### 2. Create a virtual environment (optional but recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your Gemini API key

Option 1: Hardcode it in `app.py`:

```python
api_key = "YOUR_GEMINI_API_KEY_HERE"
```

Option 2 (recommended): Use a `.env` file:

```env
GEMINI_API_KEY=your_key_here
```

And load it in code:

```python
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
```

---

## ▶️ How to Run

```bash
python app.py
```

- Upload your contract PDF.
- Scroll to view AI-generated insights.
- Ask custom questions.
- Listen with TTS support.

---

## 📁 Project Structure

```
auto-contract-interpreter/
├── app.py              # Main application file
├── requirements.txt    # Dependencies list
├── README.md           # Project overview
├── LICENSE             # MIT License
└── .env (optional)     # Your Gemini API key (not tracked by Git)
```

---

## 📌 Example Use Cases

- Understand freelance or business contracts
- Summarize terms before signing
- Aid visually impaired users with TTS
- Explore LLMs + desktop apps

---

## 📝 License

MIT License. See [LICENSE] file for full details.

---

## 🙌 Contributions


1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
3. Make your changes and commit:
   ```bash
   git commit -am "Add your feature"
4. Push to your work:
   ```bash
   git push origin feature/your-feature-name
5. Open a pull request on GitHub 🎉
