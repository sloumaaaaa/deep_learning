"""
ESB Academic Assistant - Streamlit Web Application
A multilingual chatbot powered by RAG (Retrieval-Augmented Generation)
with Hybrid Search (BM25 + Semantic + Keyword Matching)
"""

import streamlit as st
import os
import re
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

# Set page config
st.set_page_config(
    page_title="ESB Academic Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize LLM and RAG components (cached for performance)
@st.cache_resource
def load_rag_components():
    """Load and cache RAG components"""
    
    # Set API keys
    if "GROQ_API_KEY" not in os.environ:
         GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # Initialize LLM
    llm = ChatGroq(model="llama-3.3-70b-versatile")
    
    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Load documents
    try:
        loader = TextLoader("data_esb.txt", encoding="utf-8")
        docs = loader.load()
    except FileNotFoundError:
        st.error("❌ data_esb.txt not found. Please ensure the file exists in the current directory.")
        st.stop()
    
    # Split documents with better parameters
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,  # Larger chunks to keep context
        chunk_overlap=100  # More overlap for continuity
    )
    splits = text_splitter.split_documents(docs)
    
    # Create vectorstore for semantic search
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
    
    # Create semantic retriever
    semantic_retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 8}  # Get more results
    )
    
    # Create BM25 retriever for keyword search
    bm25_retriever = BM25Retriever.from_documents(splits)
    bm25_retriever.k = 8
    
    # Smart hybrid retriever with pattern-based search
    def hybrid_retriever(query):
        """
        Smart retriever combining:
        1. Pattern-based keyword search (for structured data)
        2. BM25 keyword search
        3. Semantic search
        """
        
        query_lower = query.lower()
        all_docs = []
        seen_content = set()
        
        # PATTERN-BASED SEARCH: Extract exact patterns from raw text
        pattern_results = []
        raw_text = docs[0].page_content if docs else ""
        
        # Pattern 1: Find master/bachelor programs sections
        if "licence" in query_lower or "bachelor" in query_lower or "license" in query_lower:
            pattern = r"bachelor programs in esb\s*:\s*\[(.*?)\]"
            matches = re.findall(pattern, raw_text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                pattern_results.append(Document(
                    page_content=f"bachelor programs in esb : [{match}]",
                    metadata={"source": "pattern_match"}
                ))
        
        # Pattern 2: Find specific program subjects
        if "matière" in query_lower or "subject" in query_lower or "cours" in query_lower:
            # Extract program name from query
            programs = ["master BA", "master finance digitale", "master GAMMA", "master MKD", "master MDSI", "master CCA",
                       "bachelor BI", "bachelor BIS", "bachelor management", "bachelor comptabilite"]
            for prog in programs:
                if prog.lower() in query_lower:
                    pattern = rf"subjects to study in {prog}\s*:\s*\[(.*?)\]"
                    matches = re.findall(pattern, raw_text, re.IGNORECASE | re.DOTALL)
                    for match in matches:
                        pattern_results.append(Document(
                            page_content=f"subjects to study in {prog} : [{match}]",
                            metadata={"source": "pattern_match"}
                        ))
        
        # Pattern 3: Find jobs/careers
        if "job" in query_lower or "emploi" in query_lower or "career" in query_lower or "métier" in query_lower:
            pattern = r"jobs you can get choosing.*?\s*:\s*\[(.*?)\]"
            matches = re.findall(pattern, raw_text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                pattern_results.append(Document(
                    page_content=match[:500],
                    metadata={"source": "pattern_match"}
                ))
        
        # Add pattern-based results first (highest priority)
        for doc in pattern_results:
            content_hash = hash(doc.page_content[:100])
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                all_docs.append(doc)
        
        # Then add BM25 + Semantic results
        expanded_queries = [query]
        
        if "licence" in query_lower or "license" in query_lower or "bachelor" in query_lower:
            expanded_queries.extend(["bachelor programs", "licences", "subjects"])
        if "master" in query_lower:
            expanded_queries.extend(["master programs", "masters available"])
        if "matière" in query_lower or "subject" in query_lower or "cours" in query_lower:
            expanded_queries.extend(["subjects to study", "courses", "curriculum"])
        if "emploi" in query_lower or "job" in query_lower or "career" in query_lower or "métier" in query_lower:
            expanded_queries.extend(["jobs", "careers", "positions"])
        if "secteur" in query_lower or "sector" in query_lower or "industry" in query_lower:
            expanded_queries.extend(["sector of activity", "industries"])
        
        # Get results for all expanded queries
        for q in expanded_queries:
            try:
                bm25_docs = bm25_retriever.invoke(q)
                semantic_docs = semantic_retriever.invoke(q)
                
                for doc in bm25_docs + semantic_docs:
                    content_hash = hash(doc.page_content[:100])
                    if content_hash not in seen_content:
                        seen_content.add(content_hash)
                        all_docs.append(doc)
            except:
                pass
        
        # Return deduplicated results
        return all_docs[:12]
    
    retriever = hybrid_retriever
    
    # Create RAG chain
    system_prompt = """Tu es un assistant académique très utile et multilingue travaillant pour l'ESB (Esprit School of Business).

INSTRUCTIONS TRÈS IMPORTANTES:
1. RECHERCHE DANS LE CONTEXTE: Cherche TOUTES les informations pertinentes dans le contexte fourni
2. EXHAUSTIF: Fournis une réponse COMPLÈTE et DÉTAILLÉE en utilisant TOUTES les informations du contexte
3. STRUCTURE: Catégorise TOUJOURS les programmes en:
   - 'Licenses' (Bachelor's degrees / Licences)  
   - 'Masters' (Master's degrees / Masters)
4. PRÉCISION: Utilise UNIQUEMENT les informations exactes du contexte fourni
5. SINCÉRITÉ: Si une info n'est PAS dans le contexte, dis-le clairement

Le contexte contient des listes complètes de:
- Masters disponibles
- Licences disponibles
- Matières pour chaque programme
- Emplois après chaque cursus
- Secteurs d'activité

RÉPONDS TOUJOURS en cherchant ces informations dans le contexte.

Context: {context}

Question: {question}

Réponse complète et détaillée:"""
    
    prompt = ChatPromptTemplate.from_template(system_prompt)
    question_answer_chain = prompt | llm | StrOutputParser()
    
    def rag_chain(query):
        # Retrieve relevant documents using hybrid search
        docs = retriever(query)
        
        # Create context from retrieved documents
        context = "\n".join([doc.page_content for doc in docs])
        
        # Invoke the chain with proper variables
        result = question_answer_chain.invoke({
            "context": context, 
            "question": query
        })
        return result
    
    return rag_chain

# Load RAG components
rag_chain = load_rag_components()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your multilingual assistant. I can assist you in English, French, and Arabic. Please choose your preferred language: English, Français, or عربي"}
    ]

if "language_preference" not in st.session_state:
    st.session_state.language_preference = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# App title and description
st.title("🎓 ESB Academic Assistant")
st.markdown("### Multilingual Chat with RAG")
st.markdown("---")

# Sidebar for language selection and settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    if st.session_state.language_preference is None:
        st.info("👈 Please select a language to start chatting")
        language = st.radio(
            "Select your preferred language:",
            ["English", "Français", "عربي"],
            key="lang_select"
        )
        
        if st.button("Continue with " + language):
            st.session_state.language_preference = language.lower() if language != "عربي" else "arabic"
            st.rerun()
    else:
        st.success(f"✅ Current language: {st.session_state.language_preference.capitalize()}")
        
        if st.button("🔄 Change Language"):
            st.session_state.language_preference = None
            st.session_state.messages = [st.session_state.messages[0]]
            st.session_state.chat_history = []
            st.rerun()
        
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = [st.session_state.messages[0]]
            st.session_state.chat_history = []
            st.rerun()
    
    st.divider()
    st.markdown("### 📚 About")
    st.markdown("""
    This chatbot is powered by:
    - **RAG**: Retrieval-Augmented Generation
    - **LLM**: Llama 3.3 70B
    - **Vector DB**: Chroma
    - **Framework**: Streamlit
    """)

# Display chat messages
if st.session_state.language_preference is not None:
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    user_input = st.chat_input("Type your question here...")
    
    if user_input:
        # Check for exit keywords
        exit_keywords = {
            "english": ["bye", "exit", "quit"],
            "french": ["au revoir", "adieu", "quitter"],
            "arabic": ["وداعاً", "خروج"]
        }
        
        lang_key = st.session_state.language_preference
        if lang_key == "français":
            lang_key = "french"
        elif lang_key == "عربي":
            lang_key = "arabic"
        
        if any(keyword in user_input.lower() for keyword in exit_keywords.get(lang_key, [])):
            # Exit messages
            exit_messages = {
                "english": "Goodbye! Thank you for using ESB Academic Assistant. 👋",
                "french": "Au revoir ! Merci d'avoir utilisé l'Assistant Académique ESB. 👋",
                "arabic": "وداعاً! شكراً لاستخدامك مساعد ESB الأكاديمي. 👋"
            }
            
            st.chat_message("user").markdown(user_input)
            st.chat_message("assistant").markdown(exit_messages.get(lang_key, exit_messages["english"]))
            st.session_state.language_preference = None
            st.stop()
        
        # Add user message to session state
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").markdown(user_input)
        
        # Get AI response
        with st.spinner("🤔 Thinking..."):
            try:
                # Invoke RAG chain
                response = rag_chain(user_input)
                
                # Add assistant response
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.session_state.chat_history.extend([
                    HumanMessage(content=user_input),
                    AIMessage(content=response)
                ])
                
                # Display response
                st.chat_message("assistant").markdown(response)
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.chat_message("assistant").markdown(f"Sorry, I encountered an error: {str(e)}")
