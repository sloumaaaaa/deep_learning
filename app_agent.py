"""
ESB Academic Assistant - Agentic Version with LangGraph
A multilingual chatbot powered by an AI agent with specialized tools
"""

import streamlit as st
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from fuzzywuzzy import process, fuzz
from datetime import datetime
import json
from io import BytesIO
import hashlib
import pickle
from pathlib import Path
import base64
from groq import Groq

# Optional multimodal dependencies
try:
    from gtts import gTTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

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

# ==================== AUTHENTICATION SYSTEM ====================

# User database (in production, use proper database)
USERS_DB = {
    "admin1": hashlib.sha256("123456".encode()).hexdigest(),
    "admin2": hashlib.sha256("123456".encode()).hexdigest()
}

# Session storage directory
SESSION_DIR = Path("user_sessions")
SESSION_DIR.mkdir(exist_ok=True)

def authenticate(username, password):
    """Authenticate user credentials"""
    if username in USERS_DB:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return USERS_DB[username] == password_hash
    return False

def save_user_session(username, session_data):
    """Save user session to disk"""
    session_file = SESSION_DIR / f"{username}_session.pkl"
    with open(session_file, 'wb') as f:
        pickle.dump(session_data, f)

def load_user_session(username):
    """Load user session from disk"""
    session_file = SESSION_DIR / f"{username}_session.pkl"
    if session_file.exists():
        with open(session_file, 'rb') as f:
            return pickle.load(f)
    return None

def login_page():
    """Display login page"""
    st.title("🔐 ESB Academic Assistant - Login")
    st.markdown("### Secure Authentication Required")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("#### Please enter your credentials")
        username = st.text_input("👤 Username", key="login_username")
        password = st.text_input("🔑 Password", type="password", key="login_password")
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("🚀 Login", use_container_width=True):
                if authenticate(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.login_time = datetime.now()
                    
                    # Load existing session or create new
                    saved_session = load_user_session(username)
                    if saved_session:
                        st.session_state.messages = saved_session.get("messages", [])
                        st.session_state.chat_history = saved_session.get("chat_history", [])
                        st.session_state.analytics = saved_session.get("analytics", {
                            "total_queries": 0,
                            "queries_by_type": {},
                            "start_time": datetime.now()
                        })
                    
                    st.success(f"✅ Welcome back, {username}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
        
        with col_btn2:
            if st.button("👥 Active Users", use_container_width=True):
                st.info(f"🟢 Registered Users: {len(USERS_DB)}")
    
    st.markdown("---")
    st.info("💡 Default users: admin1, admin2 | Password: 123456")

def logout():
    """Logout current user and save session"""
    if "username" in st.session_state:
        # Save session before logout
        session_data = {
            "messages": st.session_state.get("messages", []),
            "chat_history": st.session_state.get("chat_history", []),
            "analytics": st.session_state.get("analytics", {})
        }
        save_user_session(st.session_state.username, session_data)
    
    # Clear session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# ==================== END AUTHENTICATION SYSTEM ====================

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
    
    # Create a manual agent executor with enhanced features
    class EnhancedAgent:
        def __init__(self, llm, tools):
            self.llm = llm
            self.tools = {tool.name: tool for tool in tools}
            self.all_programs = ["BA", "GAMMA", "MKD", "MDSI", "CCA", "BI", "BIS", "management", "comptabilite", "finance digitale"]
        
        def fuzzy_match_program(self, query):
            """Find program names in query using fuzzy matching"""
            found_programs = []
            query_upper = query.upper()
            
            # First, check for exact matches (case-insensitive)
            for prog in self.all_programs:
                if prog.upper() in query_upper:
                    found_programs.append(prog)
            
            # If no exact match, try fuzzy matching with strict threshold
            if not found_programs:
                for prog in self.all_programs:
                    # Use token_set_ratio for better matching
                    score = fuzz.token_set_ratio(prog.upper(), query_upper)
                    if score > 80:  # Strict threshold
                        found_programs.append(prog)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_programs = []
            for prog in found_programs:
                if prog not in seen:
                    seen.add(prog)
                    unique_programs.append(prog)
            
            return unique_programs
        
        def invoke(self, inputs):
            query = inputs.get("input", "")
            chat_history = inputs.get("chat_history", [])
            query_lower = query.lower()
            responses = []
            
            # Handle greetings and simple conversational inputs
            greetings = ["hello", "hi", "hey", "bonjour", "salut", "bonsoir", "مرحبا", "السلام عليكم", "هلا"]
            simple_thanks = ["thank", "thanks", "merci", "شكرا"]
            simple_bye = ["bye", "goodbye", "au revoir", "وداعا", "مع السلامة"]
            
            # Check if it's just a greeting
            query_words = query_lower.split()
            if any(greeting in query_lower for greeting in greetings) and len(query_words) <= 3:
                return {
                    "output": f"Hello {st.session_state.username}! 👋 How can I help you today?\n\nI can assist you with:\n- 📚 Available programs\n- 📖 Course subjects\n- 💼 Career prospects\n- 🆚 Program comparisons\n- 🎯 Interest-based recommendations\n\nFeel free to ask me anything!"
                }
            
            # Check if it's a thank you
            if any(thanks in query_lower for thanks in simple_thanks) and len(query_words) <= 3:
                return {
                    "output": "You're welcome! 😊 Is there anything else I can help you with?"
                }
            
            # Check if it's a goodbye
            if any(bye in query_lower for bye in simple_bye) and len(query_words) <= 3:
                return {
                    "output": "Goodbye! 👋 Feel free to come back anytime you need help. Have a great day!"
                }
            
            # Check if user is referring to previous context
            pronouns = ["it", "that", "this", "the first", "the second", "them"]
            if any(p in query_lower for p in pronouns) and chat_history:
                # Add context from last message
                last_msg = str(chat_history[-1].content) if chat_history else ""
                query = f"Context: {last_msg[:200]}\n\nCurrent question: {query}"
            
            # Multi-tool detection
            needs_programs = any(kw in query_lower for kw in ["programmes", "programs", "master", "bachelor", "licence", "available", "disponible", "list"])
            needs_subjects = any(kw in query_lower for kw in ["subject", "matière", "cours", "study", "étudier", "curriculum", "learn"])
            needs_careers = any(kw in query_lower for kw in ["job", "emploi", "career", "carrière", "débouché", "métier", "work"])
            needs_comparison = any(kw in query_lower for kw in ["compare", "vs", "versus", "difference", "better"])
            
            # Check for interest-based search
            if any(kw in query_lower for kw in ["interested in", "want to study", "like", "passion"]):
                interest_result = self.tools["search_by_interest"].invoke(query)
                responses.append(interest_result)
            
            # Handle comparison
            if needs_comparison:
                programs = self.fuzzy_match_program(query)
                if len(programs) >= 2:
                    compare_result = self.tools["compare_programs"].invoke(", ".join(programs[:3]))
                    responses.append(compare_result)
            
            # Find mentioned programs with fuzzy matching
            programs_in_query = self.fuzzy_match_program(query)
            
            # Execute appropriate tools
            if needs_programs and not programs_in_query:
                prog_result = self.tools["search_programs"].invoke(query)
                responses.append(prog_result)
            
            if needs_subjects:
                if programs_in_query:
                    # Only process the first matched program to avoid duplicates
                    for prog in programs_in_query[:1]:  # Limit to first match
                        subj_result = self.tools["get_program_subjects"].invoke(prog)
                        if "No subjects found" not in subj_result:
                            responses.append(subj_result)
                            break  # Stop after first successful match
                        else:
                            # Suggest similar programs
                            match, score = process.extractOne(prog, self.all_programs, scorer=fuzz.ratio)
                            responses.append(f"⚠️ Program '{prog}' not found. Did you mean: {match}?")
            
            if needs_careers:
                if programs_in_query:
                    # Only process the first matched program to avoid duplicates
                    for prog in programs_in_query[:1]:  # Limit to first match
                        career_result = self.tools["get_career_prospects"].invoke(prog)
                        if "No career information" not in career_result:
                            responses.append(career_result)
                            break  # Stop after first successful match
            
            # If no specific tool matched or need general info
            if not responses or (not needs_programs and not needs_subjects and not needs_careers and not needs_comparison):
                general_result = self.tools["search_general_info"].invoke(query)
                if general_result and general_result != "No relevant information found.":
                    responses.append(general_result)
            
            # Combine all responses
            if not responses:
                responses.append("Je n'ai pas trouvé d'information spécifique. Pouvez-vous reformuler votre question?")
            
            combined_response = "\n\n---\n\n".join(responses)
            
            # Detect query language
            query_lang = "english"
            if any(word in query_lower for word in ["quels", "quel", "quelle", "programmes", "matières", "cours", "débouchés"]):
                query_lang = "french"
            elif any(char in query for char in ["ا", "ل", "ع", "ر", "ب", "ي"]):
                query_lang = "arabic"
            
            # Use LLM to format with STRICT language instruction
            lang_instruction = {
                "english": "RESPOND ONLY IN ENGLISH. Do not use French or Arabic.",
                "french": "RÉPONDS UNIQUEMENT EN FRANÇAIS. N'utilise pas l'anglais ou l'arabe.",
                "arabic": "أجب باللغة العربية فقط. لا تستخدم الإنجليزية أو الفرنسية."
            }
            
            # Include document context if provided
            doc_context = inputs.get("document_context", "")
            doc_section = f"\n\nDocument uploaded by user:\n{doc_context[:2000]}\n" if doc_context else ""
            
            prompt = f"""User's question: {query}

Information found:
{combined_response}{doc_section}

CRITICAL INSTRUCTIONS:
- {lang_instruction[query_lang]}
- If document context is provided, use it to answer the user's question
- Format information clearly and professionally
- Use appropriate emojis (📚 🎓 💼 🌟)
- Structure with headings, lists, and separations
- Be concise but complete
- If multiple programs mentioned, organize by program
- LANGUAGE DETECTED: {query_lang.upper()} - USE THIS LANGUAGE ONLY!"""
            
            final_response = self.llm.invoke(prompt)
            return {"output": final_response.content}
    
    agent_executor = EnhancedAgent(llm, tools)
    
    return agent_executor

# ==================== MULTIMODAL FUNCTIONS ====================

def get_groq_client():
    """Get Groq client for multimodal APIs"""
    return Groq(api_key=os.getenv("GROQ_API_KEY"))

def transcribe_audio(audio_bytes):
    """Transcribe audio using Groq Whisper"""
    try:
        client = get_groq_client()
        transcription = client.audio.transcriptions.create(
            file=("audio.wav", audio_bytes),
            model="whisper-large-v3",
        )
        return transcription.text
    except Exception as e:
        return f"Error transcribing audio: {str(e)}"

def analyze_image(image_bytes, user_prompt="Describe this image in detail."):
    """Analyze image using Groq Vision model"""
    try:
        client = get_groq_client()
        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        
        # Detect image type
        if image_bytes[:4] == b'\x89PNG':
            media_type = "image/png"
        elif image_bytes[:2] == b'\xff\xd8':
            media_type = "image/jpeg"
        else:
            media_type = "image/jpeg"
        
        completion = client.chat.completions.create(
            model="llama-3.2-90b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            temperature=0.3,
            max_tokens=1024,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error analyzing image: {str(e)}"

def extract_document_text(uploaded_file):
    """Extract text from uploaded document"""
    try:
        if uploaded_file.type == "application/pdf":
            if not PDF_AVAILABLE:
                return "PDF support requires PyPDF2. Install with: pip install PyPDF2"
            reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip() if text.strip() else "Could not extract text from this PDF."
        elif uploaded_file.type == "text/plain":
            return uploaded_file.read().decode("utf-8")
        else:
            return f"Unsupported file format: {uploaded_file.type}"
    except Exception as e:
        return f"Error reading document: {str(e)}"

def text_to_speech(text, lang="en"):
    """Convert text to speech using gTTS"""
    if not TTS_AVAILABLE:
        return None
    try:
        # Clean text for TTS (remove emojis, markdown, special chars)
        clean_text = re.sub(r'[^\w\s.,!?;:\'\-"]', '', text)
        clean_text = re.sub(r'[#*_|]', '', clean_text)
        clean_text = clean_text.strip()
        if not clean_text:
            return None
        tts = gTTS(text=clean_text[:5000], lang=lang)
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer
    except Exception as e:
        return None

# ==================== END MULTIMODAL FUNCTIONS ====================

# Load agent
try:
    agent_executor = load_agent()
except Exception as e:
    st.error(f"❌ Error loading agent: {str(e)}")
    st.stop()

# ==================== AUTHENTICATION CHECK ====================

# Check if user is authenticated
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    login_page()
    st.stop()

# ==================== END AUTHENTICATION CHECK ====================

# Initialize session state (user-specific)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": f"Hello {st.session_state.username}! 👋 I am your intelligent academic assistant powered by AI agents. I can help you with:\n\n🎓 Available programs (Masters & Bachelors)\n📚 Course subjects for each program\n💼 Career prospects and job opportunities\n🔍 Compare programs side-by-side\n🎯 Match programs to your interests\n🏫 General information about ESB\n\nI speak English, Français, and العربية. How can I help you today?"}
    ]

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "analytics" not in st.session_state:
    st.session_state.analytics = {
        "total_queries": 0,
        "queries_by_type": {},
        "start_time": datetime.now()
    }

# App title and description
st.title(f"🤖 ESB Academic Assistant - {st.session_state.username}")
st.markdown("### AI Agent with Specialized Tools | Multi-User | Multimodal 🎤🖼️📄🔊")
st.markdown("---")

# Sidebar
with st.sidebar:
    # User info section
    st.markdown(f"### 👤 User: **{st.session_state.username}**")
    session_duration = (datetime.now() - st.session_state.login_time).seconds // 60
    st.caption(f"⏱️ Session: {session_duration} min")
    
    if st.button("🚪 Logout", use_container_width=True):
        logout()
    
    st.divider()
    
    st.header("⚙️ Agent Settings")
    
    st.success("✅ Agent Status: Active")
    st.info(f"🛠️ Available Tools: 6")
    
    st.markdown("""
    **Agent Capabilities:**
    - 🔍 Program Search
    - 📖 Subject Lookup
    - 💼 Career Information
    - 🆚 Program Comparison
    - 🎯 Interest Matching
    - 🌐 General Search
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = [st.session_state.messages[0]]
            st.session_state.chat_history = []
            st.rerun()
    
    with col2:
        if st.button("📥 Export Chat"):
            if len(st.session_state.messages) > 1:
                # Create text export
                export_text = f"ESB Academic Assistant - Chat Export\n"
                export_text += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                export_text += "="*50 + "\n\n"
                
                for msg in st.session_state.messages:
                    role = msg["role"].upper()
                    content = msg["content"]
                    export_text += f"{role}:\n{content}\n\n" + "-"*50 + "\n\n"
                
                # Create download button
                st.download_button(
                    label="💾 Download TXT",
                    data=export_text,
                    file_name=f"esb_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
    
    st.divider()
    
    # Analytics section
    st.markdown("### 📊 Session Analytics")
    st.metric("Total Queries", st.session_state.analytics["total_queries"])
    
    if st.session_state.analytics["queries_by_type"]:
        st.markdown("**Query Types:**")
        for qtype, count in st.session_state.analytics["queries_by_type"].items():
            st.text(f"{qtype}: {count}")
    
    st.divider()
    
    # Admin Panel (only for admin users)
    if st.session_state.username in ["admin1", "admin2"]:
        st.markdown("### 👑 Admin Panel")
        
        if st.button("📋 View All Users", use_container_width=True):
            st.markdown("**Active Users:**")
            session_files = list(SESSION_DIR.glob("*_session.pkl"))
            for session_file in session_files:
                username = session_file.stem.replace("_session", "")
                st.text(f"• {username}")
        
        if st.button("🗑️ Clear All Sessions", use_container_width=True):
            if st.checkbox("⚠️ Confirm deletion"):
                for session_file in SESSION_DIR.glob("*_session.pkl"):
                    session_file.unlink()
                st.success("All sessions cleared!")
        
        st.divider()
    
    st.markdown("### 📚 Technology Stack")
    st.markdown("""
    - **Agent**: Enhanced Multi-Tool Agent
    - **LLM**: Llama 3.3 70B (Groq)
    - **Tools**: 6 Custom ESB Tools
    - **Search**: Hybrid (BM25 + Vector)
    - **Features**: Fuzzy Match + Memory
    - **Framework**: Streamlit
    """)
    
    st.divider()
    st.markdown("### 💡 Pro Tips")
    st.markdown("""
    - **Compare**: "Compare BA vs GAMMA"
    - **Interest**: "I'm interested in data"
    - **Multi-query**: Ask about subjects AND jobs
    - **Follow-up**: "Tell me more about the first one"
    - **Any language**: EN, FR, AR
    """)
    
    st.divider()
    st.markdown("### � Multimodal Features")
    st.toggle("🔊 Text-to-Speech", key="tts_enabled")
    st.markdown("""
    - 🎤 **Voice Input** (Whisper STT)
    - 🖼️ **Image Analysis** (AI Vision)
    - 📄 **Document Upload** (PDF/TXT)
    - 🔊 **Text-to-Speech** (gTTS)
    """)
# ==================== MULTIMODAL INPUT SECTION ====================
with st.expander("🎨 Multimodal Input (Voice, Image, Document)", expanded=False):
    mm_tab1, mm_tab2, mm_tab3 = st.tabs(["🎤 Voice Input", "🖼️ Image Analysis", "📄 Document Upload"])
    
    with mm_tab1:
        st.markdown("**Record your question and click Transcribe:**")
        try:
            audio_data = st.audio_input("🎙️ Speak your question")
            if audio_data:
                if st.button("📝 Transcribe & Ask", key="transcribe_btn", type="primary"):
                    with st.spinner("🎤 Transcribing with Groq Whisper..."):
                        transcript = transcribe_audio(audio_data.getvalue())
                        if transcript and not transcript.startswith("Error"):
                            st.session_state.pending_voice_input = transcript
                            st.rerun()
                        else:
                            st.error(f"Transcription failed: {transcript}")
        except Exception:
            st.warning("⚠️ Voice input requires Streamlit >= 1.33. Please upgrade: `pip install streamlit --upgrade`")
    
    with mm_tab2:
        uploaded_image = st.file_uploader("Upload an image for AI analysis", type=["png", "jpg", "jpeg", "webp"], key="image_uploader")
        if uploaded_image:
            st.image(uploaded_image, caption=f"📷 {uploaded_image.name}", use_container_width=True)
            image_question = st.text_input(
                "What would you like to know about this image?",
                value="Describe this image in detail and relate it to academic programs if relevant.",
                key="image_question"
            )
            if st.button("🔍 Analyze Image", key="analyze_img_btn", type="primary"):
                with st.spinner("🖼️ Analyzing with AI Vision (Llama 3.2 90B)..."):
                    analysis = analyze_image(uploaded_image.getvalue(), image_question)
                    st.session_state.pending_image_result = {
                        "question": image_question,
                        "answer": analysis,
                        "filename": uploaded_image.name
                    }
                    st.rerun()
    
    with mm_tab3:
        uploaded_doc = st.file_uploader("Upload a document for context", type=["pdf", "txt"], key="doc_uploader")
        if uploaded_doc:
            doc_text = extract_document_text(uploaded_doc)
            if doc_text and not doc_text.startswith(("Error", "PDF support", "Unsupported", "Could not")):
                st.session_state.document_context = doc_text
                preview = doc_text[:500] + "..." if len(doc_text) > 500 else doc_text
                st.text_area("📄 Document Preview:", preview, height=150, disabled=True)
                st.success(f"✅ Document loaded ({len(doc_text):,} chars). Ask questions about it in the chat!")
                if st.button("🗑️ Clear Document Context", key="clear_doc"):
                    st.session_state.pop("document_context", None)
                    st.rerun()
            else:
                st.error(doc_text)
        elif "document_context" in st.session_state:
            st.info(f"📄 Document loaded ({len(st.session_state.document_context):,} chars). Ask questions in the chat below!")
            if st.button("🗑️ Clear Document Context", key="clear_doc_active"):
                st.session_state.pop("document_context", None)
                st.rerun()

# ==================== PROCESS MULTIMODAL INPUTS ====================
# Handle pending image analysis
if "pending_image_result" in st.session_state:
    img_result = st.session_state.pop("pending_image_result")
    st.session_state.messages.append({"role": "user", "content": f"🖼️ [Image: {img_result['filename']}] {img_result['question']}"})
    st.session_state.messages.append({"role": "assistant", "content": f"🖼️ **Image Analysis:**\n\n{img_result['answer']}"})
    st.session_state.analytics["total_queries"] += 1
    st.session_state.analytics["queries_by_type"]["Image Analysis"] = \
        st.session_state.analytics["queries_by_type"].get("Image Analysis", 0) + 1
    session_data = {"messages": st.session_state.messages, "chat_history": st.session_state.chat_history, "analytics": st.session_state.analytics}
    save_user_session(st.session_state.username, session_data)

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get user input (text or voice)
pending_voice = st.session_state.pop("pending_voice_input", None)
user_input = st.chat_input("Ask me anything about ESB programs... 🎤💬")

if pending_voice:
    user_input = pending_voice
    st.toast("🎤 Voice input transcribed!")

if user_input:
    # Update analytics
    st.session_state.analytics["total_queries"] += 1
    
    # Categorize query
    query_lower = user_input.lower()
    if "program" in query_lower or "master" in query_lower or "bachelor" in query_lower:
        query_type = "Programs"
    elif "subject" in query_lower or "cours" in query_lower:
        query_type = "Subjects"
    elif "job" in query_lower or "career" in query_lower:
        query_type = "Careers"
    elif "compare" in query_lower:
        query_type = "Comparison"
    else:
        query_type = "General"
    
    st.session_state.analytics["queries_by_type"][query_type] = \
        st.session_state.analytics["queries_by_type"].get(query_type, 0) + 1
    
    # Add user message to session state
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("🤔 Agent analyzing query and selecting tools..."):
            try:
                # Prepare input for agent
                agent_input = {
                    "input": user_input,
                    "chat_history": st.session_state.chat_history[-10:],  # Last 10 messages for context
                    "document_context": st.session_state.get("document_context", "")
                }
                
                # Invoke enhanced agent
                result = agent_executor.invoke(agent_input)
                response = result["output"]
                
                # Display response with streaming effect (simulated)
                response_placeholder = st.empty()
                full_response = ""
                
                # Simulate streaming by showing response progressively
                import time
                words = response.split()
                for i in range(0, len(words), 5):  # Show 5 words at a time
                    full_response = " ".join(words[:i+5])
                    response_placeholder.markdown(full_response + "▌")
                    time.sleep(0.05)  # Small delay for effect
                
                response_placeholder.markdown(response)
                
                # Text-to-Speech if enabled
                if st.session_state.get("tts_enabled", False) and TTS_AVAILABLE:
                    tts_lang = "en"
                    resp_lower = response.lower()
                    if any(w in resp_lower for w in ["programme", "matière", "informations", "également", "vous"]):
                        tts_lang = "fr"
                    elif any(c in response for c in ["ا", "ل", "ع", "ر"]):
                        tts_lang = "ar"
                    tts_audio = text_to_speech(response, tts_lang)
                    if tts_audio:
                        st.audio(tts_audio, format="audio/mp3")
                
                # Update session state
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.session_state.chat_history.extend([
                    HumanMessage(content=user_input),
                    AIMessage(content=response)
                ])
                
                # Auto-save session after each interaction
                session_data = {
                    "messages": st.session_state.messages,
                    "chat_history": st.session_state.chat_history,
                    "analytics": st.session_state.analytics
                }
                save_user_session(st.session_state.username, session_data)
                
            except Exception as e:
                error_msg = f"❌ Agent Error: {str(e)}\n\n💡 Try rephrasing your question or ask about:\n- Available programs\n- Subjects in a program\n- Career opportunities\n- Comparing programs"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("*✨ Multimodal AI Agents*")
with col2:
    st.markdown("*🚀 Groq LLM + Whisper + Vision*")
with col3:
    duration = (datetime.now() - st.session_state.analytics["start_time"]).seconds // 60
    st.markdown(f"*⏱️ Session: {duration}min*")
