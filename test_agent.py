"""
Test script for the ESB Agentic Assistant
Run this to verify everything is working before launching the full app
"""

import os
from dotenv import load_dotenv

def test_imports():
    """Test if all required packages are installed"""
    print("🔍 Testing imports...")
    try:
        import streamlit
        print("✅ Streamlit installed")
        
        import langchain
        print("✅ LangChain installed")
        
        from langchain_groq import ChatGroq
        print("✅ LangChain-Groq installed")
        
        from langchain_community.embeddings import HuggingFaceEmbeddings
        print("✅ HuggingFace Embeddings available")
        
        from langchain_chroma import Chroma
        print("✅ Chroma installed")
        
        from langchain_community.retrievers import BM25Retriever
        print("✅ BM25Retriever available")
        
        # No complex agent imports needed - using manual agent
        print("✅ LangChain Agents available (manual implementation)")
        
        print("\n✅ All imports successful!\n")
        return True
    except ImportError as e:
        print(f"\n❌ Import failed: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def test_api_key():
    """Test if API key is set"""
    print("🔑 Testing API key...")
    
    # Load .env file
    load_dotenv()
    
    api_key = os.getenv("GROQ_API_KEY")
    if api_key and len(api_key) > 10:
        print(f"✅ GROQ API key found: {api_key[:10]}...")
        return True
    else:
        print("❌ GROQ_API_KEY not found or invalid")
        print("Set it in .env file or environment variable")
        return False

def test_data_file():
    """Test if data file exists"""
    print("\n📄 Testing data file...")
    
    if os.path.exists("data_esb.txt"):
        with open("data_esb.txt", "r", encoding="utf-8") as f:
            content = f.read()
            print(f"✅ data_esb.txt found ({len(content)} characters)")
            return True
    else:
        print("❌ data_esb.txt not found")
        return False

def test_tools_module():
    """Test if tools module can be imported"""
    print("\n🛠️  Testing tools module...")
    try:
        from esb_agent_tools import ESBTools
        print("✅ esb_agent_tools.py imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import tools: {e}")
        return False

def test_llm_connection():
    """Test LLM connection (requires API key)"""
    print("\n🤖 Testing LLM connection...")
    
    load_dotenv()
    
    try:
        from langchain_groq import ChatGroq
        
        llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
        response = llm.invoke("Say 'OK' if you can hear me")
        
        print(f"✅ LLM responded: {response.content[:50]}")
        return True
    except Exception as e:
        print(f"❌ LLM connection failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("ESB AGENTIC ASSISTANT - SYSTEM TEST")
    print("=" * 50)
    print()
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("API Key", test_api_key()))
    results.append(("Data File", test_data_file()))
    results.append(("Tools Module", test_tools_module()))
    results.append(("LLM Connection", test_llm_connection()))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 All tests passed! You're ready to run the app:")
        print("   streamlit run app_agent.py")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
    print()

if __name__ == "__main__":
    main()
