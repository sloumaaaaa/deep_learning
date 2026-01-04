"""
Simple Demo Script - Shows how the ESB Agent works
Run this to see the agent in action without the Streamlit UI
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
import re
from esb_agent_tools import ESBTools

# Load environment variables
load_dotenv()

print("🤖 ESB Agentic Assistant - Demo")
print("=" * 50)
print()

# Initialize components
print("⚙️  Initializing components...")

# LLM
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
print("✅ LLM initialized")

# Embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
print("✅ Embeddings loaded")

# Load documents
loader = TextLoader("data_esb.txt", encoding="utf-8")
docs = loader.load()
raw_data = docs[0].page_content
print("✅ Data loaded")

# Split documents
text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
splits = text_splitter.split_documents(docs)
print("✅ Documents split")

# Create vectorstore
vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
print("✅ Vectorstore created")

# Create BM25 retriever
bm25_retriever = BM25Retriever.from_documents(splits)
bm25_retriever.k = 8
print("✅ BM25 retriever created")

# Create tools
esb_tools = ESBTools(raw_data, vectorstore, bm25_retriever)
tools = esb_tools.create_tools()
print(f"✅ {len(tools)} tools created")

# Create manual agent
class ManualAgent:
    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = {tool.name: tool for tool in tools}
    
    def invoke(self, inputs):
        query = inputs.get("input", "")
        query_lower = query.lower()
        response = None
        
        # Keyword-based tool selection
        if any(kw in query_lower for kw in ["programmes", "programs", "master", "bachelor", "available"]):
            if "subject" not in query_lower and "job" not in query_lower:
                response = self.tools["search_programs"].invoke(query)
        
        if any(kw in query_lower for kw in ["subject", "mati\u00e8re", "study"]):
            for prog in ["BA", "GAMMA", "BI", "management"]:
                if prog.lower() in query_lower:
                    tool_result = self.tools["get_program_subjects"].invoke(prog)
                    response = tool_result if not response else response + "\n\n" + tool_result
                    break
        
        if any(kw in query_lower for kw in ["job", "emploi", "career"]):
            for prog in ["BA", "GAMMA", "BI", "management"]:
                if prog.lower() in query_lower:
                    tool_result = self.tools["get_career_prospects"].invoke(prog)
                    response = tool_result if not response else response + "\n\n" + tool_result
                    break
        
        if not response:
            response = self.tools["search_general_info"].invoke(query)
        
        prompt = f"Question: {query}\n\nInformation: {response}\n\nFormat this nicely with clear structure."
        final_response = self.llm.invoke(prompt)
        return {"output": final_response.content}

agent_executor = ManualAgent(llm, tools)
print("✅ Agent created")

print()
print("=" * 50)
print("🎯 Running Demo Queries")
print("=" * 50)
print()

# Demo queries
demo_queries = [
    "What master programs are available at ESB?",
    "What subjects will I study in Master BA?",
    "What jobs can I get with Bachelor BI?",
]

for i, query in enumerate(demo_queries, 1):
    print(f"\n{'='*50}")
    print(f"Query {i}: {query}")
    print('='*50)
    
    try:
        result = agent_executor.invoke({"input": query})
        print(f"\n📝 Response:")
        print(result["output"])
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()

print("\n" + "=" * 50)
print("✅ Demo Complete!")
print("=" * 50)
print()
print("🚀 To run the full app with UI:")
print("   streamlit run app_agent.py")
print()
