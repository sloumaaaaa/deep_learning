# Quick Start Guide - Agentic Version

## 🚀 Fast Setup (3 Steps)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Your API Key
```bash
# Windows PowerShell
$env:GROQ_API_KEY="your_groq_api_key_here"
```

### 3. Run the App
```bash
streamlit run app_agent.py
```

## 🎯 What Makes This Version Better?

### Traditional RAG (app.py)
- Searches documents
- Returns what it finds
- Sometimes misses structured data

### Agentic Version (app_agent.py)
- **Thinks** about your question
- **Chooses** the right tool
- **Combines** multiple sources
- **Structures** the answer perfectly

## 🛠️ Available Agent Tools

1. **search_programs** - Lists all master/bachelor programs
2. **get_program_subjects** - Shows courses for a specific program
3. **get_career_prospects** - Lists jobs you can get
4. **search_general_info** - General knowledge search

## 💬 Example Queries

Try these questions to see the agent in action:

```
✅ "What master programs are available?"
   → Agent uses: search_programs

✅ "What will I study in Master BA?"
   → Agent uses: get_program_subjects

✅ "What jobs can I get with Bachelor BI?"
   → Agent uses: get_career_prospects

✅ "Tell me about the finance programs and career options"
   → Agent uses: Multiple tools, combines results
```

## 🌍 Multilingual

Ask in any language:
- English: "What programs do you offer?"
- Français: "Quels programmes proposez-vous?"
- العربية: "ما هي البرامج المتاحة؟"

## 🎨 Features

- ✅ AI Agent with reasoning capabilities
- ✅ 4 specialized tools
- ✅ Hybrid search (Vector + BM25)
- ✅ Multilingual (EN, FR, AR)
- ✅ Conversation history
- ✅ Structured responses

## 📊 See It In Action

Watch the agent think:
1. Agent receives your question
2. Agent decides which tool(s) to use
3. Tools execute and return data
4. Agent synthesizes a complete answer

## 🆚 Comparison

| Feature | RAG Version | Agent Version |
|---------|------------|---------------|
| Speed | ⚡ Very Fast | ⚡ Fast |
| Accuracy | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Complex Queries | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Tool Selection | ❌ Fixed | ✅ Dynamic |
| Reasoning | ❌ No | ✅ Yes |

## 🔧 Troubleshooting

**Problem**: ImportError
**Fix**: `pip install -r requirements.txt`

**Problem**: API Error
**Fix**: Set GROQ_API_KEY environment variable

**Problem**: Data not found
**Fix**: Ensure data_esb.txt is in the folder

## 📚 Learn More

See [AGENT_README.md](AGENT_README.md) for complete documentation.

---

**Ready to start? Run:**
```bash
streamlit run app_agent.py
```
