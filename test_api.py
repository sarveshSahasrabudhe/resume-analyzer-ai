#!/usr/bin/env python3
"""
Test script for the Resume Analyzer API
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_root():
    """Test root endpoint"""
    print("Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_skills():
    """Test skills endpoint"""
    print("Testing skills endpoint...")
    response = requests.get(f"{BASE_URL}/skills")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_analyze_resume_only():
    """Test analyze resume only endpoint"""
    print("Testing analyze resume only endpoint...")
    
    # You would need to provide a PDF file here
    # For now, this is just a template
    print("Note: This endpoint requires a PDF file upload")
    print("Example usage:")
    print("""
    files = {'resume_file': open('path/to/resume.pdf', 'rb')}
    response = requests.post(f"{BASE_URL}/analyze-resume-only", files=files)
    """)
    print()

def test_analyze_with_jd():
    """Test analyze with job description endpoint"""
    print("Testing analyze with job description endpoint...")
    
    # You would need to provide a PDF file and job description here
    # For now, this is just a template
    print("Note: This endpoint requires a PDF file upload and job description")
    print("Example usage:")
    print("""
    files = {'resume_file': open('path/to/resume.pdf', 'rb')}
    data = {
        'job_description': 'Your job description here...',
        'required_skills': ['Python', 'Java', 'AWS']
    }
    response = requests.post(f"{BASE_URL}/analyze", files=files, data=data)
    """)
    print()

def main():
    """Run all tests"""
    print("=== Resume Analyzer API Tests ===\n")
    
    try:
        test_health()
        test_root()
        test_skills()
        test_analyze_resume_only()
        test_analyze_with_jd()
        
        print("✅ All basic tests completed!")
        print("\n📖 API Documentation available at: http://localhost:8000/docs")
        print("🔍 Interactive API explorer at: http://localhost:8000/redoc")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API server")
        print("Make sure the FastAPI server is running on http://localhost:8000")
        print("Start it with: python app.py")

if __name__ == "__main__":
    main()
