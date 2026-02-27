# 🤖 ESB Academic Assistant — Multimodal AI Agent

An intelligent, multilingual, multimodal academic chatbot for **École Supérieure de Business (ESB)**. Built with an agentic architecture using LangChain, Groq LLMs, and Streamlit, it provides information about programs, subjects, career prospects, and more — through text, voice, images, and documents.

---

## 📸 Overview

| Feature | Technology |
|---|---|
| **LLM** | Llama 3.3 70B (Groq) |
| **Vision** | Llama 4 Scout 17B (Groq) |
| **Speech-to-Text** | Whisper Large V3 (Groq) |
| **Text-to-Speech** | gTTS (Google) |
| **Embeddings** | all-MiniLM-L6-v2 (HuggingFace) |
| **Vector Store** | ChromaDB |
| **Keyword Search** | BM25 |
| **Fuzzy Matching** | FuzzyWuzzy + Levenshtein |
| **Framework** | Streamlit |
| **Agent** | Custom EnhancedAgent (multi-tool orchestration) |

---

## 🚀 How to Run

### 1. Clone & Navigate

```bash
cd "deep learning/deeplearning"
```

### 2. Create Environment (optional but recommended)

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Key

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Get a free API key at [console.groq.com](https://console.groq.com).

### 5. Launch the App

```bash
streamlit run app_agent.py
```

The app opens at `http://localhost:8501`. Log in with:

| Username | Password |
|----------|----------|
| `admin1` | `123456` |
| `admin2` | `123456` |

---

## ✨ Features

### 🤖 Agentic Architecture (6 Specialized Tools)

The chatbot uses an **EnhancedAgent** that intelligently selects and combines tools based on the user query:

| Tool | Description |
|------|-------------|
| `search_programs` | Lists all available Master and Bachelor programs |
| `get_program_subjects` | Retrieves the curriculum/subjects for a specific program |
| `get_career_prospects` | Shows job opportunities for a given program |
| `search_general_info` | Hybrid BM25 + semantic search for general ESB questions |
| `compare_programs` | Side-by-side comparison of 2+ programs |
| `search_by_interest` | Recommends programs based on user interests |

The agent supports **multi-tool queries** — asking about subjects AND careers in a single message triggers both tools automatically.

### 🌍 Multilingual Support

- **English**, **Français**, **العربية**
- Automatic language detection from user input
- Responses are generated strictly in the detected language

### 🎨 Multimodal Capabilities

#### 🎤 Voice Input (Speech-to-Text)
- Record audio directly in the browser
- Transcribed by **Groq Whisper Large V3**
- Transcription is used as a chat query automatically

#### 🖼️ Image Analysis (AI Vision)
- Upload PNG, JPG, JPEG, or WEBP images
- Analyzed by **Llama 4 Scout 17B** vision model
- Ask custom questions about the image content

#### 📄 Document Upload (PDF/TXT)
- Upload PDF or plain text files
- Extracted text is stored as context for all subsequent queries
- Ask questions about the uploaded document in natural language

#### 🔊 Text-to-Speech (TTS)
- Toggle in sidebar to enable audio playback of responses
- Auto-detects language (EN/FR/AR) for correct pronunciation
- Powered by Google Text-to-Speech (gTTS)

### 🔐 Multi-User Authentication

- Secure login with SHA-256 password hashing
- Persistent sessions saved to disk (auto-save after each interaction)
- Session restore on re-login (chat history, analytics preserved)
- Admin panel to view active users and manage sessions

### 🔍 Hybrid Search

- **BM25** keyword-based retrieval for exact term matching
- **ChromaDB** vector semantic search for meaning-based retrieval
- Results are combined and deduplicated for best accuracy

### 🧠 Intelligent Features

- **Fuzzy Matching** — tolerates typos in program names (e.g., "GAMA" → "GAMMA")
- **Conversational Memory** — retains last 10 messages for context-aware follow-ups
- **Greeting Detection** — handles "hello", "merci", "bye" without invoking tools
- **Pronoun Resolution** — understands "tell me more about it" using prior context
- **Simulated Streaming** — progressive word-by-word response display

### 📊 Analytics & Export

- **Session Analytics** — tracks total queries, query categories, session duration
- **Chat Export** — download conversation history as a text file
- **Query Categorization** — Programs, Subjects, Careers, Comparison, Image Analysis, General

---

## 📁 Project Structure

```
deeplearning/
├── app_agent.py           # Main application (Streamlit UI + agent + multimodal + auth)
├── esb_agent_tools.py     # 6 specialized LangChain tools for the agent
├── data_esb.txt           # ESB knowledge base (programs, subjects, jobs)
├── requirements.txt       # Python dependencies
├── .env                   # API keys (GROQ_API_KEY)
├── test_agent.py          # System validation script
├── demo_agent.py          # CLI demo for testing
├── app.py                 # Original RAG-only version (legacy)
├── app_with_metrics.py    # Version with evaluation metrics (legacy)
├── chatbot.ipynb          # Jupyter notebook version
├── user_sessions/         # Persisted user session data
└── .streamlit/            # Streamlit configuration
```

---

## 🛠️ Available Programs (from knowledge base)

**Master Programs:**
- Business Analytics (BA)
- Finance Digitale
- GAMMA (Gestion Actuarielle et Modélisation Mathématique)
- Marketing Digital (MKD)
- Comptabilité-Contrôle-Audit (CCA)
- Management Digital & Systèmes d'Information (MDSI)

**Bachelor Programs:**
- Business Intelligence (BI)
- Business Information System (BIS)
- Management
- Comptabilité

---

## 💡 Example Queries

| Query | Tools Used |
|-------|-----------|
| "What programs are available?" | `search_programs` |
| "What subjects are in GAMMA?" | `get_program_subjects` |
| "Jobs for BA graduates?" | `get_career_prospects` |
| "Compare BA vs MKD" | `compare_programs` |
| "I'm interested in data science" | `search_by_interest` |
| "Tell me about the subjects and jobs for CCA" | `get_program_subjects` + `get_career_prospects` |
| *Upload an image* | Llama 4 Scout Vision |
| *Record a voice message* | Whisper STT → Agent |
| *Upload a PDF* | Document extraction → context-aware chat |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────┐
│           Streamlit Web Interface                 │
│    (Chat UI + Multimodal Inputs + Auth)           │
├──────────────────────────────────────────────────┤
│        🎤 Whisper STT  │  🖼️ Vision  │  📄 PDF   │
├──────────────────────────────────────────────────┤
│           EnhancedAgent (Tool Orchestration)      │
│     Fuzzy Match │ Memory │ Language Detection     │
├──────────────────────────────────────────────────┤
│  search_programs │ get_subjects │ get_careers     │
│  compare_programs │ search_by_interest │ general  │
├──────────────────────────────────────────────────┤
│   ChromaDB (Vector)  +  BM25 (Keyword) Hybrid    │
├──────────────────────────────────────────────────┤
│  LLM: Llama 3.3 70B │ Vision: Llama 4 Scout     │
│         All via Groq API                          │
└──────────────────────────────────────────────────┘
```

---

## ⚙️ Tech Stack

- **Python 3.10+**
- **Streamlit** — Web UI
- **LangChain** — Agent framework, tools, embeddings, retrievers
- **Groq API** — LLM (Llama 3.3 70B), Vision (Llama 4 Scout), STT (Whisper)
- **ChromaDB** — Vector database
- **BM25** — Keyword retrieval
- **FuzzyWuzzy** — Fuzzy string matching
- **gTTS** — Text-to-speech
- **PyPDF2** — PDF text extraction
- **HuggingFace Sentence Transformers** — Embeddings (all-MiniLM-L6-v2)

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|---------|
| `data_esb.txt not found` | Ensure the file is in the same directory as `app_agent.py` |
| `API key not found` | Create `.env` with `GROQ_API_KEY=your_key` |
| Voice input not showing | Upgrade Streamlit: `pip install streamlit --upgrade` (requires >= 1.33) |
| Slow first load | Normal — models and embeddings are cached after first run |
| Vision model error | Groq may deprecate models; check [Groq docs](https://console.groq.com/docs/deprecations) |

---

**Created with ❤️ for ESB** | **Powered by LangChain, Groq & Streamlit**
