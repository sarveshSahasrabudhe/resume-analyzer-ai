# Resume Analyzer API

A FastAPI microservice for analyzing resumes and matching them with job descriptions using AI and machine learning techniques.

## Features

- 📄 **PDF Resume Analysis**: Extract and analyze text from PDF resumes
- 🎯 **Job Description Matching**: Compare resumes against job descriptions
- 🔍 **Skills Extraction**: Identify technical skills using predefined skill lists
- 📊 **TF-IDF Analysis**: Calculate document similarity scores
- 🤖 **AI-Powered Analysis**: Use Hugging Face models for intelligent text analysis
- 🚀 **RESTful API**: Clean, documented API endpoints
- 📖 **Auto-generated Documentation**: Interactive API docs with Swagger UI

## Installation

### Option 1: Docker (Recommended)

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd resume-analyzer-ai
   ```

2. **Build and run with Docker**:
   ```bash
   # Using the build script (recommended)
   ./build.sh
   
   # Or manually
   docker build -t resume-analyzer .
   docker run -d -p 8000:8000 --name resume-analyzer-container resume-analyzer
   ```

3. **Test the API**:
   ```bash
   curl http://localhost:8000/health
   ```

### Option 2: Local Python Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd resume-analyzer-ai
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Download spaCy model**:
   ```bash
   python -m spacy download en_core_web_md
   ```

## Usage

### Starting the Server

```bash
python app.py
```

The API will be available at `http://localhost:8000`

### API Documentation

- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### API Endpoints

#### 1. Health Check
```bash
GET /health
```

#### 2. Get Available Skills
```bash
GET /skills
```

#### 3. Analyze Resume Only
```bash
POST /analyze-resume-only
```
- **Body**: Form data with `resume_file` (PDF)
- **Response**: Resume skills, top terms, and AI analysis

#### 4. Analyze Resume with Job Description
```bash
POST /analyze
```
- **Body**: Form data with:
  - `resume_file` (PDF)
  - `job_description` (text)
  - `required_skills` (optional array)
- **Response**: Complete analysis including matching scores

### Example Usage

#### Using curl:

```bash
# Health check
curl http://localhost:8000/health

# Get skills
curl http://localhost:8000/skills

# Analyze resume only
curl -X POST "http://localhost:8000/analyze-resume-only" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "resume_file=@path/to/resume.pdf"

# Analyze with job description
curl -X POST "http://localhost:8000/analyze" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "resume_file=@path/to/resume.pdf" \
     -F "job_description=We are looking for a Python developer with AWS experience..." \
     -F "required_skills=Python" \
     -F "required_skills=AWS"
```

#### Using Python:

```python
import requests

# Analyze resume with job description
files = {'resume_file': open('resume.pdf', 'rb')}
data = {
    'job_description': 'We are looking for a Python developer...',
    'required_skills': ['Python', 'AWS', 'Docker']
}

response = requests.post('http://localhost:8000/analyze', files=files, data=data)
result = response.json()

print(f"Skills Match: {result['skills_match_percentage']}%")
print(f"Similarity Score: {result['similarity_score']}")
```

## Response Format

### Analyze Response
```json
{
  "resume_skills": ["python", "aws", "docker"],
  "jd_skills": ["python", "java", "aws"],
  "matched_skills": ["python", "aws"],
  "missing_skills": ["java"],
  "skills_match_percentage": 66.67,
  "similarity_score": 0.27,
  "resume_top_terms": [
    {"term": "python", "score": 0.1849},
    {"term": "aws", "score": 0.1643}
  ],
  "jd_top_terms": [
    {"term": "experience", "score": 0.2947},
    {"term": "python", "score": 0.2210}
  ],
  "llm_analysis": "The ideal candidate should have hands-on experience..."
}
```

## Configuration

### Skills List
Edit `skills.json` to customize the skills that are analyzed:

```json
{
  "skills": [
    "Python", "Java", "Spring Boot", "AWS", "Docker",
    "Kubernetes", "React", "Node.js", "PostgreSQL"
  ]
}
```

### Models
The API uses Hugging Face models:
- **Summarization**: `facebook/bart-large-cnn`
- **Text Generation**: `gpt2` (fallback)

## Development

### Running Tests
```bash
python test_api.py
```

### Project Structure
```
resume-analyzer-ai/
├── app.py                 # FastAPI application
├── resume_analyzer.py     # Core analysis logic
├── extract_text.py        # Original script (backward compatibility)
├── test_api.py           # API test script
├── requirements.txt      # Dependencies
├── skills.json          # Skills configuration
├── job_desc.txt         # Sample job description
└── README.md            # This file
```

## Technologies Used

- **FastAPI**: Modern, fast web framework for building APIs
- **spaCy**: Natural language processing
- **scikit-learn**: Machine learning (TF-IDF, cosine similarity)
- **Transformers**: Hugging Face models for AI analysis
- **PyPDF2**: PDF text extraction
- **Uvicorn**: ASGI server

## License

This project is open source and available under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 🚀 Deployment

### Quick Deploy to Cloud

Use the deployment script for easy cloud deployment:

```bash
# Deploy to different platforms
./deploy.sh local      # Local Docker deployment
./deploy.sh aws        # Deploy to AWS
./deploy.sh gcp        # Deploy to Google Cloud
./deploy.sh azure      # Deploy to Azure
./deploy.sh heroku     # Deploy to Heroku
```

### Manual Cloud Deployment

#### AWS (ECS/App Runner)
```bash
# Build and push to ECR
aws ecr create-repository --repository-name resume-analyzer
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker build -t resume-analyzer .
docker tag resume-analyzer:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/resume-analyzer:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/resume-analyzer:latest
```

#### Google Cloud Run
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT-ID/resume-analyzer
gcloud run deploy resume-analyzer --image gcr.io/PROJECT-ID/resume-analyzer --platform managed --allow-unauthenticated
```

#### Heroku
```bash
# Deploy with Heroku Container Registry
heroku container:login
heroku container:push web
heroku container:release web
```

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Support

For issues and questions, please open an issue on GitHub.