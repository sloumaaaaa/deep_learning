"""
ESB Academic Assistant - Streamlit avec Métriques d'Évaluation
Version avancée avec calcul des métriques ROUGE, BLEU, Cosine Similarity
"""

import streamlit as st
import os
import re
import pandas as pd
import numpy as np
from datetime import datetime
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

# Métriques d'évaluation
from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk

# Télécharger ressources NLTK
try:
    nltk.download('punkt', quiet=True)
except:
    pass

# Set page config
st.set_page_config(
    page_title="ESB Academic Assistant with Metrics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# FONCTIONS D'ÉVALUATION
# ============================================================================

def calculate_rouge_scores(reference: str, generated: str) -> dict:
    """Calcule les scores ROUGE-1, ROUGE-2, ROUGE-L"""
    try:
        scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        scores = scorer.score(reference, generated)
        return {
            'ROUGE-1': round(scores['rouge1'].fmeasure, 4),
            'ROUGE-2': round(scores['rouge2'].fmeasure, 4),
            'ROUGE-L': round(scores['rougeL'].fmeasure, 4)
        }
    except:
        return {'ROUGE-1': 0, 'ROUGE-2': 0, 'ROUGE-L': 0}

def calculate_bleu_score(reference: str, generated: str) -> float:
    """Calcule le score BLEU"""
    try:
        ref_tokens = word_tokenize(reference.lower())
        gen_tokens = word_tokenize(generated.lower())
        return round(sentence_bleu([ref_tokens], gen_tokens), 4)
    except:
        return 0.0

def calculate_cosine_similarity(reference: str, generated: str) -> float:
    """Calcule la similarité cosinus"""
    try:
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform([reference, generated])
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        return round(similarity, 4)
    except:
        return 0.0

def evaluate_response(question: str, reference: str, generated: str) -> dict:
    """Évalue une réponse avec toutes les métriques"""
    return {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'question': question,
        'reference': reference,
        'generated': generated,
        **calculate_rouge_scores(reference, generated),
        'BLEU': calculate_bleu_score(reference, generated),
        'Cosine_Similarity': calculate_cosine_similarity(reference, generated)
    }

# ============================================================================
# COMPOSANTS RAG
# ============================================================================
import os

@st.cache_resource
def load_rag_components():
    """Load and cache RAG components"""
    
    if "GROQ_API_KEY" not in os.environ:
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    llm = ChatGroq(model="llama-3.3-70b-versatile")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    try:
        loader = TextLoader("data_esb.txt", encoding="utf-8")
        docs = loader.load()
    except FileNotFoundError:
        st.error("❌ data_esb.txt not found.")
        st.stop()
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    splits = text_splitter.split_documents(docs)
    
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
    
    semantic_retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 8}
    )
    
    bm25_retriever = BM25Retriever.from_documents(splits)
    bm25_retriever.k = 8
    
    def hybrid_retriever(query):
        query_lower = query.lower()
        all_docs = []
        seen_content = set()
        
        pattern_results = []
        raw_text = docs[0].page_content if docs else ""
        
        if "licence" in query_lower or "bachelor" in query_lower or "license" in query_lower:
            pattern = r"bachelor programs in esb\s*:\s*\[(.*?)\]"
            matches = re.findall(pattern, raw_text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                pattern_results.append(Document(
                    page_content=f"bachelor programs in esb : [{match}]",
                    metadata={"source": "pattern_match"}
                ))
        
        if "matière" in query_lower or "subject" in query_lower or "cours" in query_lower:
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
        
        if "job" in query_lower or "emploi" in query_lower or "career" in query_lower or "métier" in query_lower:
            pattern = r"jobs you can get choosing.*?\s*:\s*\[(.*?)\]"
            matches = re.findall(pattern, raw_text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                pattern_results.append(Document(
                    page_content=match[:500],
                    metadata={"source": "pattern_match"}
                ))
        
        for doc in pattern_results:
            content_hash = hash(doc.page_content[:100])
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                all_docs.append(doc)
        
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
        
        return all_docs[:12]
    
    retriever = hybrid_retriever
    
    system_prompt = """Tu es un assistant académique très utile et multilingue travaillant pour l'ESB.

INSTRUCTIONS TRÈS IMPORTANTES:
1. RECHERCHE DANS LE CONTEXTE: Cherche TOUTES les informations pertinentes
2. EXHAUSTIF: Fournis une réponse COMPLÈTE et DÉTAILLÉE
3. STRUCTURE: Catégorise les programmes en 'Licenses' et 'Masters'
4. PRÉCISION: Utilise UNIQUEMENT les informations exactes du contexte
5. SINCÉRITÉ: Si une info n'est PAS dans le contexte, dis-le clairement

Context: {context}

Question: {question}

Réponse complète et détaillée:"""
    
    prompt = ChatPromptTemplate.from_template(system_prompt)
    question_answer_chain = prompt | llm | StrOutputParser()
    
    def rag_chain(query):
        docs = retriever(query)
        context = "\n".join([doc.page_content for doc in docs])
        result = question_answer_chain.invoke({
            "context": context, 
            "question": query
        })
        return result
    
    return rag_chain

# ============================================================================
# INITIALISATION SESSION STATE
# ============================================================================

rag_chain = load_rag_components()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! Choose your language: English, Français, or عربي"}
    ]

if "language_preference" not in st.session_state:
    st.session_state.language_preference = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "evaluation_history" not in st.session_state:
    st.session_state.evaluation_history = []

if "reference_answers" not in st.session_state:
    st.session_state.reference_answers = {}

# ============================================================================
# INTERFACE STREAMLIT
# ============================================================================

st.title("🎓 ESB Academic Assistant with Metrics")
st.markdown("### Multilingual Chat with RAG + Evaluation Metrics")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings & Metrics")
    
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
        st.subheader("📊 Évaluation")
        
        # Option pour fournir une réponse de référence
        st.markdown("#### Ajouter réponse de référence")
        ref_question = st.text_input("Question pour l'évaluation:", placeholder="ex: Quels sont les masters?")
        ref_answer = st.text_area("Réponse de référence:", placeholder="Entrez la bonne réponse...", height=100)
        
        if st.button("💾 Sauvegarder réponse de référence"):
            if ref_question and ref_answer:
                st.session_state.reference_answers[ref_question] = ref_answer
                st.success("✅ Réponse de référence sauvegardée!")
        
        # Afficher l'historique des évaluations
        if st.session_state.evaluation_history:
            st.markdown("#### 📈 Historique des métriques")
            eval_df = pd.DataFrame(st.session_state.evaluation_history)
            
            st.dataframe(eval_df[[
                'timestamp', 'ROUGE-1', 'ROUGE-2', 'BLEU', 'Cosine_Similarity'
            ]], use_container_width=True, height=300)
            
            # Statistiques globales
            st.markdown("#### 📊 Statistiques globales")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Avg ROUGE-1", f"{eval_df['ROUGE-1'].mean():.4f}")
            with col2:
                st.metric("Avg ROUGE-2", f"{eval_df['ROUGE-2'].mean():.4f}")
            with col3:
                st.metric("Avg BLEU", f"{eval_df['BLEU'].mean():.4f}")
            with col4:
                st.metric("Avg Cosine Sim", f"{eval_df['Cosine_Similarity'].mean():.4f}")
            
            # Télécharger les métriques
            csv = eval_df.to_csv(index=False)
            st.download_button(
                label="📥 Télécharger métriques (CSV)",
                data=csv,
                file_name="metrics.csv",
                mime="text/csv"
            )

# Chat interface
if st.session_state.language_preference is not None:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    user_input = st.chat_input("Type your question here...")
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").markdown(user_input)
        
        with st.spinner("🤔 Thinking..."):
            try:
                response = rag_chain(user_input)
                
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.session_state.chat_history.extend([
                    HumanMessage(content=user_input),
                    AIMessage(content=response)
                ])
                
                # Évaluation automatique si réponse de référence existe
                if user_input in st.session_state.reference_answers:
                    ref_answer = st.session_state.reference_answers[user_input]
                    metrics = evaluate_response(user_input, ref_answer, response)
                    st.session_state.evaluation_history.append(metrics)
                    
                    # Afficher les métriques
                    with st.container():
                        st.markdown("---")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("ROUGE-1", metrics['ROUGE-1'])
                        with col2:
                            st.metric("BLEU", metrics['BLEU'])
                        with col3:
                            st.metric("Cosine Sim", metrics['Cosine_Similarity'])
                        with col4:
                            st.metric("ROUGE-L", metrics['ROUGE-L'])
                        st.markdown("---")
                
                st.chat_message("assistant").markdown(response)
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.chat_message("assistant").markdown(f"Sorry, I encountered an error: {str(e)}")
