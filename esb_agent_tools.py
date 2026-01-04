"""
ESB Agent Tools - Specialized tools for the academic assistant agent
"""

import re
from typing import List
from langchain.tools import tool
from langchain_core.documents import Document


class ESBTools:
    """Collection of tools for ESB Academic Assistant"""
    
    def __init__(self, raw_data_text: str, vectorstore, bm25_retriever):
        self.raw_data = raw_data_text
        self.vectorstore = vectorstore
        self.bm25_retriever = bm25_retriever
    
    @staticmethod
    def extract_programs(text: str, program_type: str) -> List[str]:
        """Extract programs from raw text using pattern matching"""
        pattern = rf"{program_type} programs in esb\s*:\s*\[(.*?)\]"
        matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
        
        if matches:
            # Parse the list format
            programs_str = matches[0]
            # Extract program names from quotes
            programs = re.findall(r"'([^']+)'", programs_str)
            return programs
        return []
    
    @staticmethod
    def extract_subjects(text: str, program_name: str) -> List[str]:
        """Extract subjects for a specific program"""
        pattern = rf"subjects to study in {re.escape(program_name)}\s*:\s*\[(.*?)\]"
        matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
        
        if matches:
            subjects_str = matches[0]
            subjects = re.findall(r"'([^']+)'", subjects_str)
            return subjects
        return []
    
    @staticmethod
    def extract_jobs(text: str, program_name: str) -> List[str]:
        """Extract job prospects for a specific program"""
        pattern = rf"jobs you can get choosing (?:master|bachelor) in {re.escape(program_name)}\s*:\s*\[(.*?)\]"
        matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
        
        if matches:
            jobs_str = matches[0]
            jobs = re.findall(r"'([^']+)'", jobs_str)
            return jobs
        return []
    
    def create_tools(self):
        """Create and return all agent tools"""
        
        @tool
        def search_programs(query: str) -> str:
            """
            Search for available master and bachelor programs at ESB.
            Use this tool when users ask about available programs, degrees, or formations.
            
            Args:
                query: The search query (e.g., "master programs", "bachelor programs", "all programs")
            
            Returns:
                A formatted string with the list of programs
            """
            query_lower = query.lower()
            
            # Extract programs from raw data
            masters = self.extract_programs(self.raw_data, "master")
            bachelors = self.extract_programs(self.raw_data, "bachelor")
            
            result = []
            
            if "master" in query_lower or "all" in query_lower or "programmes" in query_lower:
                if masters:
                    result.append("📚 **Master Programs at ESB:**")
                    for i, prog in enumerate(masters, 1):
                        result.append(f"  {i}. {prog}")
            
            if "bachelor" in query_lower or "licence" in query_lower or "all" in query_lower:
                if bachelors:
                    if result:
                        result.append("")
                    result.append("🎓 **Bachelor Programs at ESB:**")
                    for i, prog in enumerate(bachelors, 1):
                        result.append(f"  {i}. {prog}")
            
            if not result:
                # Fallback to semantic search
                docs = self.bm25_retriever.invoke(query)
                if docs:
                    return docs[0].page_content[:500]
                return "No programs found matching your query."
            
            return "\n".join(result)
        
        @tool
        def get_program_subjects(program_name: str) -> str:
            """
            Get the list of subjects/courses for a specific program.
            Use this tool when users ask about courses, subjects, curriculum, or what to study in a program.
            
            Args:
                program_name: The name or abbreviation of the program (e.g., "BA", "finance digitale", "BI")
            
            Returns:
                A formatted string with the list of subjects
            """
            # Normalize program name
            program_name_lower = program_name.lower().strip()
            
            # Map common abbreviations to full names
            program_mapping = {
                "ba": "master BA",
                "gamma": "master GAMMA",
                "mkd": "master MKD",
                "mdsi": "master MDSI",
                "cca": "master CCA",
                "bi": "bachelor BI",
                "bis": "bachelor BIS",
                "business intelligence": "bachelor BI",
                "business information system": "bachelor BIS",
                "management": "bachelor management",
                "comptabilite": "bachelor comptabilite",
                "comptabilité": "bachelor comptabilite"
            }
            
            # Try to find the program name
            search_name = program_mapping.get(program_name_lower, program_name_lower)
            
            # Search in raw data
            subjects = self.extract_subjects(self.raw_data, search_name)
            
            if not subjects:
                # Try alternative names
                for key, value in program_mapping.items():
                    if key in program_name_lower or program_name_lower in key:
                        subjects = self.extract_subjects(self.raw_data, value)
                        if subjects:
                            break
            
            if subjects:
                result = [f"📖 **Subjects in {program_name}:**", ""]
                for i, subject in enumerate(subjects, 1):
                    result.append(f"{i}. {subject}")
                return "\n".join(result)
            
            return f"No subjects found for program: {program_name}. Please check the program name."
        
        @tool
        def get_career_prospects(program_name: str) -> str:
            """
            Get job opportunities and career prospects for a specific program.
            Use this tool when users ask about jobs, careers, employment, or what they can do after graduation.
            
            Args:
                program_name: The name or abbreviation of the program
            
            Returns:
                A formatted string with job opportunities
            """
            program_name_lower = program_name.lower().strip()
            
            # Map common abbreviations
            program_mapping = {
                "ba": "BA",
                "gamma": "GAMMA",
                "mkd": "MKD",
                "mdsi": "MDSI",
                "cca": "CCA",
                "bi": "BI",
                "bis": "BIS",
                "business intelligence": "BI",
                "business information system": "BIS",
                "management": "management",
                "comptabilite": "comptabilite",
                "comptabilité": "comptabilite"
            }
            
            search_name = program_mapping.get(program_name_lower, program_name_lower)
            jobs = self.extract_jobs(self.raw_data, search_name)
            
            if not jobs:
                # Try alternative names
                for key, value in program_mapping.items():
                    if key in program_name_lower or program_name_lower in key:
                        jobs = self.extract_jobs(self.raw_data, value)
                        if jobs:
                            break
            
            if jobs:
                result = [f"💼 **Career Prospects for {program_name}:**", ""]
                for i, job in enumerate(jobs, 1):
                    result.append(f"{i}. {job}")
                return "\n".join(result)
            
            return f"No career information found for program: {program_name}"
        
        @tool
        def search_general_info(query: str) -> str:
            """
            Search for general information about ESB, programs, or academic topics.
            Use this tool for questions that don't fit the other specialized tools.
            
            Args:
                query: The search query
            
            Returns:
                Relevant information from the knowledge base
            """
            # Use hybrid search
            try:
                # BM25 search
                bm25_docs = self.bm25_retriever.invoke(query)
                
                # Semantic search
                semantic_docs = self.vectorstore.as_retriever(
                    search_type="similarity",
                    search_kwargs={"k": 5}
                ).invoke(query)
                
                # Combine and deduplicate
                all_docs = []
                seen = set()
                for doc in bm25_docs + semantic_docs:
                    content_hash = hash(doc.page_content[:100])
                    if content_hash not in seen:
                        seen.add(content_hash)
                        all_docs.append(doc)
                
                if all_docs:
                    # Return top results
                    context = "\n\n".join([doc.page_content for doc in all_docs[:5]])
                    return context[:2000]  # Limit context size
                
                return "No relevant information found."
            except Exception as e:
                return f"Search error: {str(e)}"
        
        return [search_programs, get_program_subjects, get_career_prospects, search_general_info]
