# 🤖 ESB Academic Assistant - Agentic Edition

## Overview

This is an **agentic AI assistant** that uses **LangChain agents** with specialized tools to help students and prospective students learn about ESB (Esprit School of Business) programs.

### What's New in Agentic Version?

Unlike the original RAG-only approach, this version uses an **AI agent** that can:
- **Think and reason** about which tool to use
- **Break down complex queries** into multiple tool calls
- **Combine information** from different sources
- **Provide more accurate** and structured responses

## Architecture

```
┌─────────────────────────────────────────┐
│     Streamlit Web Interface             │
├─────────────────────────────────────────┤
│     User Input & Session Management     │
├─────────────────────────────────────────┤
│        LangChain Agent Executor         │
│    (Reasoning & Tool Orchestration)     │
├─────────────────────────────────────────┤
│          Specialized Tools:             │
│  ┌───────────────────────────────────┐  │
│  │  1. search_programs               │  │
│  │  2. get_program_subjects          │  │
│  │  3. get_career_prospects          │  │
│  │  4. search_general_info           │  │
│  └───────────────────────────────────┘  │
├─────────────────────────────────────────┤
│  Vector Store (Chroma) & BM25 Search    │
├─────────────────────────────────────────┤
│    LLM (Llama 3.3 70B via Groq)        │
└─────────────────────────────────────────┘
```

## Key Components

### 1. Agent (`app_agent.py`)
The main application that:
- Creates and manages the LangChain agent
- Handles the Streamlit UI
- Manages conversation history
- Orchestrates tool usage

### 2. Tools Module (`esb_agent_tools.py`)
Contains 4 specialized tools:

#### 🔍 `search_programs`
- **Purpose**: Find available master and bachelor programs
- **Use Case**: "What programs does ESB offer?"
- **Returns**: Categorized list of all programs

#### 📖 `get_program_subjects`
- **Purpose**: Get curriculum/subjects for a specific program
- **Use Case**: "What subjects are in the Master BA program?"
- **Returns**: Complete list of courses

#### 💼 `get_career_prospects`
- **Purpose**: Find job opportunities after graduation
- **Use Case**: "What jobs can I get with a Bachelor in BI?"
- **Returns**: List of career paths and positions

#### 🌐 `search_general_info`
- **Purpose**: General knowledge base search
- **Use Case**: "Tell me about ESB's finance programs"
- **Returns**: Relevant context from documents

## Installation

### Prerequisites

- Python 3.8+
- pip
- GROQ API key

### Setup Steps

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

2. **Set up environment variables**

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Or set environment variable:

```bash
# Windows PowerShell
$env:GROQ_API_KEY="your_key_here"

# Windows CMD
set GROQ_API_KEY=your_key_here

# Linux/Mac
export GROQ_API_KEY=your_key_here
```

3. **Ensure data file exists**

Make sure `data_esb.txt` is in the same directory

## Running the Application

```bash
streamlit run app_agent.py
```

The app will open at `http://localhost:8501`

## How It Works

### Agent Decision-Making Process

1. **User asks a question** → Agent receives it
2. **Agent analyzes** the question to understand intent
3. **Agent selects** appropriate tool(s) to use
4. **Tools execute** and return information
5. **Agent synthesizes** the results
6. **Agent responds** in a structured, helpful format

### Example Flow

**User Query**: "What can I study in the Master BA program and what jobs can I get?"

**Agent Reasoning**:
1. This question has TWO parts
2. First part → use `get_program_subjects` tool
3. Second part → use `get_career_prospects` tool
4. Combine both results

**Agent Actions**:
```
Tool Call 1: get_program_subjects(program_name="Master BA")
Tool Call 2: get_career_prospects(program_name="Master BA")
```

**Agent Response**: Structured answer with both subjects AND careers

## Advantages Over Traditional RAG

| Feature | Traditional RAG | Agentic Approach |
|---------|----------------|------------------|
| **Query Understanding** | Simple retrieval | Multi-step reasoning |
| **Tool Selection** | Single retrieval | Multiple specialized tools |
| **Complex Queries** | May miss context | Breaks down into sub-tasks |
| **Accuracy** | Depends on retrieval | Uses best tool for each part |
| **Flexibility** | Fixed pipeline | Dynamic decision-making |

## Technology Stack

- **Agent Framework**: LangChain Agent Executor
- **LLM**: Llama 3.3 70B (via Groq API)
- **Embeddings**: HuggingFace (all-MiniLM-L6-v2)
- **Vector Store**: Chroma
- **Keyword Search**: BM25
- **Web Framework**: Streamlit
- **Tool Framework**: LangChain Tools

## Files Structure

```
deeplearning/
├── app_agent.py              # Main agentic application
├── esb_agent_tools.py        # Tool definitions
├── app.py                    # Original RAG version (kept for reference)
├── app_with_metrics.py       # Version with metrics
├── data_esb.txt              # Knowledge base
├── requirements.txt          # Updated dependencies
├── README.md                 # Original documentation
├── AGENT_README.md           # This file
└── .env                      # API keys (create this)
```

## Usage Examples

### Example 1: Finding Programs
```
User: "What master programs are available?"
Agent: Uses search_programs tool
       Returns categorized list of all masters
```

### Example 2: Getting Subjects
```
User: "Tell me about courses in Bachelor BI"
Agent: Uses get_program_subjects("BI")
       Returns complete curriculum
```

### Example 3: Career Information
```
User: "What jobs can I get with Master GAMMA?"
Agent: Uses get_career_prospects("GAMMA")
       Returns list of career paths
```

### Example 4: Complex Query
```
User: "I want to study data science, what program should I choose and what will I study?"
Agent: 1. Uses search_programs to find data-related programs
       2. Uses get_program_subjects for relevant programs
       3. Uses get_career_prospects to show opportunities
       Synthesizes complete answer
```

## Multilingual Support

The agent automatically responds in the language of the question:
- 🇬🇧 **English**
- 🇫🇷 **Français**
- 🇸🇦 **العربية**

## Customization

### Adding New Tools

1. Open `esb_agent_tools.py`
2. Add a new method with `@tool` decorator:

```python
@tool
def your_new_tool(query: str) -> str:
    """
    Description of what this tool does.
    
    Args:
        query: Input parameter
    
    Returns:
        Result string
    """
    # Tool logic here
    return result
```

3. Add it to the `create_tools()` return list

### Modifying Agent Behavior

Edit the system prompt in `app_agent.py`:

```python
system_prompt = """
Your custom instructions here...
"""
```

## Troubleshooting

### Issue: "Module not found"
**Solution**: Run `pip install -r requirements.txt`

### Issue: "API key error"
**Solution**: Set the GROQ_API_KEY environment variable

### Issue: "Data file not found"
**Solution**: Ensure `data_esb.txt` is in the same directory

### Issue: Agent not using tools
**Solution**: Check that the LLM supports function calling (Llama 3.3 does)

## Performance Tips

1. **Caching**: Agent and tools are cached with `@st.cache_resource`
2. **Conversation History**: Limited to last 10 messages to save tokens
3. **Tool Selection**: Agent chooses the most efficient tool
4. **Result Limits**: Each tool returns focused, relevant data

## Comparison with Original Version

### Original (`app.py`)
- ✅ Simple RAG pipeline
- ✅ Fast retrieval
- ❌ Fixed retrieval strategy
- ❌ May miss structured data
- ❌ No reasoning capability

### Agentic (`app_agent.py`)
- ✅ Intelligent tool selection
- ✅ Multi-step reasoning
- ✅ Better handling of complex queries
- ✅ Specialized tools for different needs
- ⚠️ Slightly slower (but more accurate)

## Future Enhancements

Potential improvements:
- [ ] Add memory persistence across sessions
- [ ] Implement more specialized tools
- [ ] Add streaming responses
- [ ] Create admin panel for data management
- [ ] Add analytics and usage tracking
- [ ] Implement rate limiting
- [ ] Add user authentication

## Contributing

To improve the agent:
1. Add more tools in `esb_agent_tools.py`
2. Enhance existing tools with better parsing
3. Improve agent prompts for better reasoning
4. Add more data sources

## License

Educational project for ESB students

## Support

For issues or questions:
- Check the troubleshooting section
- Review the code comments
- Test with simpler queries first

---

**Built with ❤️ using LangChain and Streamlit**
