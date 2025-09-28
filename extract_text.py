from PyPDF2 import PdfReader
import spacy
import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from transformers import pipeline

# Load spaCy model
nlp = spacy.load("en_core_web_md")

# Get current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# --- 1. Load Resume Text ---
resume_path = "/Users/sarveshsahasrabudhe/Downloads/Sarvesh - Resume.pdf"
resume_text = ""
with open(resume_path, "rb") as file:
    reader = PdfReader(file)
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:  # avoid None
            resume_text += page_text + " "

# --- 2. Load Job Description Text ---
jd_path = os.path.join(current_dir, "job_desc.txt")
try:
    with open(jd_path, "r") as f:
        jd_text = f.read()
except FileNotFoundError:
    print(f"Error: job_desc.txt not found at {jd_path}")
    exit(1)

# --- 3. Load Skills List ---
skills_path = os.path.join(current_dir, "skills.json")
try:
    with open(skills_path, "r") as f:
        required_skills = [skill.lower() for skill in json.load(f)["skills"]]
except FileNotFoundError:
    print(f"Error: skills.json not found at {skills_path}")
    exit(1)

# --- 4. Preprocess Texts ---
def preprocess_text(text):
    doc = nlp(text.lower())
    # Remove stopwords and punctuation
    tokens = [token.text for token in doc if not token.is_stop and not token.is_punct]
    return " ".join(tokens)

resume_text_processed = preprocess_text(resume_text)
jd_text_processed = preprocess_text(jd_text)

# --- 5. TF-IDF Vectorization ---
vectorizer = TfidfVectorizer()
documents = [resume_text_processed, jd_text_processed]
tfidf_matrix = vectorizer.fit_transform(documents)

# Calculate similarity score
similarity_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

# --- 6. Extract Important Terms ---
# Get feature names (terms) and their TF-IDF scores
feature_names = np.array(vectorizer.get_feature_names_out())
resume_tfidf = tfidf_matrix[0].toarray()[0]
jd_tfidf = tfidf_matrix[1].toarray()[0]

# Get top terms from resume and job description
def get_top_terms(tfidf_scores, feature_names, n=10):
    idx = np.argsort(tfidf_scores)[-n:]
    return [(feature_names[i], tfidf_scores[i]) for i in idx if tfidf_scores[i] > 0]

resume_top_terms = get_top_terms(resume_tfidf, feature_names)
jd_top_terms = get_top_terms(jd_tfidf, feature_names)

# --- 7. Traditional Skills Matching ---
resume_skills = [skill for skill in required_skills if skill in resume_text.lower()]
jd_skills = [skill for skill in required_skills if skill in jd_text.lower()]
matched = list(set(resume_skills) & set(jd_skills))
missing = list(set(jd_skills) - set(resume_skills))

# --- 8. Print Results ---
print("\n=== Skills Analysis ===")
print("Resume Skills:", resume_skills)
print("JD Skills:", jd_skills)
print("Matched Skills:", matched)
print("Missing Skills:", missing)
print(f"Skills Match %: {(len(matched) / len(jd_skills) * 100) if jd_skills else 0:.2f}%")

print("\n=== TF-IDF Analysis ===")
print(f"Document Similarity Score: {similarity_score:.2f}")
print("\nTop terms in Resume:")
for term, score in reversed(resume_top_terms):
    print(f"  {term}: {score:.4f}")
print("\nTop terms in Job Description:")
for term, score in reversed(jd_top_terms):
    print(f"  {term}: {score:.4f}")

# Initialize Hugging Face text generation pipeline
# Using a more suitable model for text summarization/extraction
generator = pipeline("text-generation", 
                    model="gpt2", 
                    max_new_tokens=100, 
                    do_sample=True, 
                    temperature=0.7,
                    pad_token_id=50256)

# Create a prompt for skill extraction
def extract_skills_with_hf(job_description):
    # Truncate job description if too long
    if len(job_description) > 1000:
        job_description = job_description[:1000] + "..."
    
    prompt = f"Job Description: {job_description}\n\nKey technical skills and requirements:"
    
    # Generate response
    response = generator(prompt, max_new_tokens=50, num_return_sequences=1, truncation=True)
    return response[0]['generated_text']

# Get Hugging Face analysis of job description
try:
    # Try using a summarization model first (better for this task)
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    
    # Truncate if too long for the model
    if len(jd_text) > 1000:
        jd_text_truncated = jd_text[:1000]
    else:
        jd_text_truncated = jd_text
    
    # Create a prompt for skill extraction
    skill_prompt = f"Extract key technical skills from: {jd_text_truncated}"
    
    # Use summarization to extract key points
    summary = summarizer(skill_prompt, max_length=100, min_length=30, do_sample=False)
    llm_keywords = summary[0]['summary_text']
    
except Exception as e:
    print(f"Error with Hugging Face summarization model: {e}")
    try:
        # Fallback to text generation
        llm_keywords = extract_skills_with_hf(jd_text)
    except Exception as e2:
        print(f"Error with Hugging Face text generation model: {e2}")
        # Final fallback: simple keyword extraction
        llm_keywords = "Fallback: Using simple keyword extraction due to model errors."

print("\n=== LLM Keyword Analysis ===")
print("Extracted Keywords from Job Description:")
print(llm_keywords)
