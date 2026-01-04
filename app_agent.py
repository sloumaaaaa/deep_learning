"""
ESB Academic Assistant - Agentic Version with LangGraph
A multilingual chatbot powered by an AI agent with specialized tools
"""

import streamlit as st
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load environment variables from .env file
load_dotenv()
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
import json
import re
from langchain_core.messages import AIMessage, HumanMessage
from esb_agent_tools import ESBTools

# Set page config
st.set_page_config(
    page_title="ESB Academic Assistant - Agentic",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Agent and Tools (cached for performance)
@st.cache_resource
def load_agent():
    """Load and cache agent with tools"""
    
    # Initialize LLM
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    
    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Load documents
    try:
        loader = TextLoader("data_esb.txt", encoding="utf-8")
        docs = loader.load()
        raw_data = docs[0].page_content
    except FileNotFoundError:
        st.error("❌ data_esb.txt not found. Please ensure the file exists in the current directory.")
        st.stop()
    
    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    splits = text_splitter.split_documents(docs)
    
    # Create vectorstore
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
    
    # Create BM25 retriever
    bm25_retriever = BM25Retriever.from_documents(splits)
    bm25_retriever.k = 8
    
    # Create ESB tools
    esb_tools = ESBTools(raw_data, vectorstore, bm25_retriever)
    tools = esb_tools.create_tools()
    
    # Create a manual agent executor
    class ManualAgent:
        def __init__(self, llm, tools):
            self.llm = llm
            self.tools = {tool.name: tool for tool in tools}
        
        def invoke(self, inputs):
            query = inputs.get("input", "")
            query_lower = query.lower()
            response = None
            
            # Keyword-based tool selection
            if any(kw in query_lower for kw in ["programmes", "programs", "master", "bachelor", "licence", "available", "disponible"]):
                if "subject" not in query_lower and "matière" not in query_lower and "job" not in query_lower and "emploi" not in query_lower:
                    response = self.tools["search_programs"].invoke(query)
            
            if any(kw in query_lower for kw in ["subject", "matière", "cours", "study", "étudier", "curriculum"]):
                for prog in ["BA", "GAMMA", "MKD", "MDSI", "CCA", "BI", "BIS", "management", "comptabilite", "finance"]:
                    if prog.lower() in query_lower:
                        tool_result = self.tools["get_program_subjects"].invoke(prog)
                        response = tool_result if not response else response + "\n\n" + tool_result
                        break
            
            if any(kw in query_lower for kw in ["job", "emploi", "career", "carrière", "débouché", "métier"]):
                for prog in ["BA", "GAMMA", "MKD", "MDSI", "CCA", "BI", "BIS", "management", "comptabilite", "finance"]:
                    if prog.lower() in query_lower:
                        tool_result = self.tools["get_career_prospects"].invoke(prog)
                        response = tool_result if not response else response + "\n\n" + tool_result
                        break
            
            if not response:
                response = self.tools["search_general_info"].invoke(query)
            
            # Format with LLM
            prompt = f"""Question: {query}

Information: {response}

Format this information clearly with emojis and lists. Respond in the same language as the question."""
            
            final_response = self.llm.invoke(prompt)
            return {"output": final_response.content}
    
    agent_executor = ManualAgent(llm, tools)
    
    return agent_executor

# Load agent
try:
    agent_executor = load_agent()
except Exception as e:
    st.error(f"❌ Error loading agent: {str(e)}")
    st.stop()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! 👋 I am your intelligent academic assistant powered by AI agents. I can help you with:\n\n🎓 Available programs (Masters & Bachelors)\n📚 Course subjects for each program\n💼 Career prospects and job opportunities\n🏫 General information about ESB\n\nI speak English, Français, and العربية. How can I help you today?"}
    ]

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# App title and description
st.title("🤖 ESB Academic Assistant - Agentic Edition")
st.markdown("### AI Agent with Specialized Tools")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Agent Settings")
    
    st.success("✅ Agent Status: Active")
    st.info("🛠️ Available Tools: 4")
    
    st.markdown("""
    **Agent Capabilities:**
    - 🔍 Program Search
    - 📖 Subject Lookup
    - 💼 Career Information
    - 🌐 General Search
    """)
    
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = [st.session_state.messages[0]]
        st.session_state.chat_history = []
        st.rerun()
    
    st.divider()
    st.markdown("### 📚 Technology Stack")
    st.markdown("""
    - **Agent**: LangChain Tool-Calling Agent
    - **LLM**: Llama 3.3 70B (Groq)
    - **Tools**: Custom ESB Tools
    - **Search**: Hybrid (BM25 + Vector)
    - **Framework**: Streamlit
    """)
    
    st.divider()
    st.markdown("### 💡 Tips")
    st.markdown("""
    - Ask about specific programs
    - Request career information
    - Query in any language
    - Be specific for best results
    """)

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
user_input = st.chat_input("Ask me anything about ESB programs...")

if user_input:
    # Add user message to session state
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").markdown(user_input)
    
    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("🤔 Agent thinking and using tools..."):
            try:
                # Prepare input for agent
                agent_input = {
                    "input": user_input,
                    "chat_history": st.session_state.chat_history[-10:]  # Last 10 messages
                }
                
                # Invoke agent
                result = agent_executor.invoke(agent_input)
                response = result["output"]
                
                # Display response
                st.markdown(response)
                
                # Update session state
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.session_state.chat_history.extend([
                    HumanMessage(content=user_input),
                    AIMessage(content=response)
                ])
                
            except Exception as e:
                error_msg = f"❌ Agent Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Footer
st.markdown("---")
st.markdown("*Powered by LangChain Agents & Groq LLM*")
