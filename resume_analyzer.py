from PyPDF2 import PdfReader
import spacy
import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from transformers import pipeline
from typing import List, Dict, Optional

# Load spaCy model
nlp = spacy.load("en_core_web_md")

# Get current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF file"""
    resume_text = ""
    try:
        with open(pdf_path, "rb") as file:
            reader = PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:  # avoid None
                    resume_text += page_text + " "
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    return resume_text

def load_skills_from_file(skills_path: Optional[str] = None) -> List[str]:
    """Load skills from JSON file"""
    if skills_path is None:
        skills_path = os.path.join(current_dir, "skills.json")
    
    try:
        with open(skills_path, "r") as f:
            skills_data = json.load(f)
        return [skill.lower() for skill in skills_data["skills"]]
    except FileNotFoundError:
        print(f"Warning: skills.json not found at {skills_path}")
        return []
    except Exception as e:
        print(f"Warning: Failed to load skills: {str(e)}")
        return []

def preprocess_text(text: str) -> str:
    """Preprocess text using spaCy"""
    doc = nlp(text.lower())
    # Remove stopwords and punctuation
    tokens = [token.text for token in doc if not token.is_stop and not token.is_punct]
    return " ".join(tokens)

def get_top_terms(tfidf_scores: np.ndarray, feature_names: np.ndarray, n: int = 10) -> List[Dict[str, float]]:
    """Get top terms with their TF-IDF scores"""
    idx = np.argsort(tfidf_scores)[-n:]
    return [{"term": feature_names[i], "score": float(tfidf_scores[i])} for i in idx if tfidf_scores[i] > 0]

def analyze_with_llm(text: str, task_type: str = "summarization") -> str:
    """Analyze text using Hugging Face models"""
    try:
        if task_type == "summarization":
            # Try using a summarization model first (better for this task)
            summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
            
            # Truncate if too long for the model
            if len(text) > 1000:
                text_truncated = text[:1000]
            else:
                text_truncated = text
            
            # Create a prompt for skill extraction
            skill_prompt = f"Extract key technical skills from: {text_truncated}"
            
            # Use summarization to extract key points
            summary = summarizer(skill_prompt, max_length=100, min_length=30, do_sample=False)
            return summary[0]['summary_text']
        
        else:
            # Fallback to text generation
            generator = pipeline("text-generation", 
                                model="gpt2", 
                                max_new_tokens=100, 
                                do_sample=True, 
                                temperature=0.7,
                                pad_token_id=50256)
            
            # Truncate job description if too long
            if len(text) > 1000:
                text = text[:1000] + "..."
            
            prompt = f"Job Description: {text}\n\nKey technical skills and requirements:"
            
            # Generate response
            response = generator(prompt, max_new_tokens=50, num_return_sequences=1, truncation=True)
            return response[0]['generated_text']
            
    except Exception as e:
        print(f"Error with Hugging Face model: {e}")
        return "LLM analysis unavailable due to model error."

def analyze_resume_with_jd(resume_path: str, job_description: str, required_skills: Optional[List[str]] = None) -> Dict:
    """Analyze resume against job description"""
    
    # Extract resume text
    resume_text = extract_text_from_pdf(resume_path)
    
    # Load skills if not provided
    if required_skills is None:
        required_skills = load_skills_from_file()
    
    # Preprocess texts
    resume_text_processed = preprocess_text(resume_text)
    jd_text_processed = preprocess_text(job_description)
    
    # TF-IDF Vectorization
    vectorizer = TfidfVectorizer()
    documents = [resume_text_processed, jd_text_processed]
    tfidf_matrix = vectorizer.fit_transform(documents)
    
    # Calculate similarity score
    similarity_score = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])
    
    # Extract important terms
    feature_names = np.array(vectorizer.get_feature_names_out())
    resume_tfidf = tfidf_matrix[0].toarray()[0]
    jd_tfidf = tfidf_matrix[1].toarray()[0]
    
    resume_top_terms = get_top_terms(resume_tfidf, feature_names)
    jd_top_terms = get_top_terms(jd_tfidf, feature_names)
    
    # Skills matching
    resume_skills = [skill for skill in required_skills if skill in resume_text.lower()]
    jd_skills = [skill for skill in required_skills if skill in job_description.lower()]
    matched_skills = list(set(resume_skills) & set(jd_skills))
    missing_skills = list(set(jd_skills) - set(resume_skills))
    
    # Calculate skills match percentage
    skills_match_percentage = (len(matched_skills) / len(jd_skills) * 100) if jd_skills else 0
    
    # LLM analysis
    llm_analysis = analyze_with_llm(job_description, "summarization")
    
    return {
        "resume_skills": resume_skills,
        "jd_skills": jd_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "skills_match_percentage": round(skills_match_percentage, 2),
        "similarity_score": round(similarity_score, 2),
        "resume_top_terms": resume_top_terms,
        "jd_top_terms": jd_top_terms,
        "llm_analysis": llm_analysis
    }

def analyze_resume_only(resume_path: str, required_skills: Optional[List[str]] = None) -> Dict:
    """Analyze resume without job description comparison"""
    
    # Extract resume text
    resume_text = extract_text_from_pdf(resume_path)
    
    # Load skills if not provided
    if required_skills is None:
        required_skills = load_skills_from_file()
    
    # Preprocess text
    resume_text_processed = preprocess_text(resume_text)
    
    # TF-IDF Vectorization
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([resume_text_processed])
    
    # Extract important terms
    feature_names = np.array(vectorizer.get_feature_names_out())
    resume_tfidf = tfidf_matrix[0].toarray()[0]
    resume_top_terms = get_top_terms(resume_tfidf, feature_names)
    
    # Skills extraction
    resume_skills = [skill for skill in required_skills if skill in resume_text.lower()]
    
    # LLM analysis
    llm_analysis = analyze_with_llm(resume_text, "summarization")
    
    return {
        "resume_skills": resume_skills,
        "resume_top_terms": resume_top_terms,
        "llm_analysis": llm_analysis
    }

# For backward compatibility - keep the original script functionality
if __name__ == "__main__":
    # Load job description from file
    jd_path = os.path.join(current_dir, "job_desc.txt")
    try:
        with open(jd_path, "r") as f:
            jd_text = f.read()
    except FileNotFoundError:
        print(f"Error: job_desc.txt not found at {jd_path}")
        exit(1)
    
    # Use the hardcoded resume path for the original script
    resume_path = "/Users/sarveshsahasrabudhe/Downloads/Sarvesh - Resume.pdf"
    
    # Analyze resume with job description
    result = analyze_resume_with_jd(resume_path, jd_text)
    
    # Print results
    print("\n=== Skills Analysis ===")
    print("Resume Skills:", result["resume_skills"])
    print("JD Skills:", result["jd_skills"])
    print("Matched Skills:", result["matched_skills"])
    print("Missing Skills:", result["missing_skills"])
    print(f"Skills Match %: {result['skills_match_percentage']:.2f}%")
    
    print("\n=== TF-IDF Analysis ===")
    print(f"Document Similarity Score: {result['similarity_score']:.2f}")
    print("\nTop terms in Resume:")
    for term_data in reversed(result["resume_top_terms"]):
        print(f"  {term_data['term']}: {term_data['score']:.4f}")
    print("\nTop terms in Job Description:")
    for term_data in reversed(result["jd_top_terms"]):
        print(f"  {term_data['term']}: {term_data['score']:.4f}")
    
    print("\n=== LLM Keyword Analysis ===")
    print("Extracted Keywords from Job Description:")
    print(result["llm_analysis"])
