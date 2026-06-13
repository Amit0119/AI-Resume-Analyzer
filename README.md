# AI Resume Analyzer - Professional Edition v2.0

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green?style=flat-square)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

## 🚀 Overview

A professional-grade, AI-powered resume analysis system that automatically extracts, compares, and ranks candidates based on job requirements. Features intelligent skill matching, semantic similarity analysis, and comprehensive statistical insights.

### Key Features

✨ **Intelligent Skill Matching**
- Semantic-based similarity analysis
- Case-insensitive matching
- Support for multiple skill variations
- Configurable matching sensitivity (0.3-0.9)

📊 **Comprehensive Analytics**
- Multi-candidate comparison charts
- Skills radar visualization
- Detailed skills matrix
- Statistical aggregation
- Candidate ranking by match score

🔒 **Professional & Secure**
- Comprehensive input validation
- File size limits (10MB per file)
- PDF corruption detection
- Secure file processing
- CORS-enabled API

🎨 **Modern User Interface**
- Dark theme with professional design
- Responsive layout (desktop & mobile)
- Real-time file validation
- Drag-and-drop support
- Interactive visualizations

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Minimum 2GB RAM for processing

## 🔧 Installation & Setup

### 1. Clone the Project

```bash
git clone <repository-url>
cd resume-analyzer
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment (Optional)

Create a `.env` file in the project root:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=False
RELOAD=True

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# File Upload Settings
MAX_FILE_SIZE=10485760  # 10MB in bytes
MAX_FILES=50
MAX_PAGES=50

# Analysis Settings
DEFAULT_SENSITIVITY=0.5
MIN_RESUME_LENGTH=100
MIN_JOB_DESC_LENGTH=10
```

### 5. Start the Server

```bash
# Development (with auto-reload)
python app.py

# Production (with Gunicorn)
gunicorn app:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

The server will start on `http://localhost:8000`

### 6. Access the Application

Open your browser and navigate to:
```
http://localhost:8000
```

## 📖 Usage Guide

### Basic Workflow

1. **Enter Job Description**
   - Navigate to the Settings panel (left sidebar)
   - Enter required skills, one per line
   - Example: Python, React.js, AWS, Docker, PostgreSQL
   - Be specific for better results

2. **Upload Resumes**
   - Click on the upload zone or drag-and-drop PDF files
   - Supported format: PDF only
   - Maximum 10MB per file
   - Supports up to 50 files at once

3. **Adjust Matching Sensitivity**
   - Use the slider in Settings (0.3 = Lenient, 0.9 = Strict)
   - Lower values accept partial matches
   - Higher values require exact matches

4. **Run Analysis**
   - Click "Analyze Resumes" button
   - Processing time depends on file size (typically 5-30 seconds)
   - Monitor progress with loading indicator

5. **Review Results**
   - **Overview Cards**: Quick statistics and best candidate
   - **Bar Chart**: Visual comparison of match percentages
   - **Radar Chart**: Skill-by-skill comparison
   - **Skills Matrix**: Detailed table of matched/missing skills

### Advanced Features

#### Sensitivity Configuration

- **0.3 (Lenient)**: Accepts partial matches and variations
  - Example: "JS" matches "JavaScript"
  - Best for: Quick screening, loose matching
  
- **0.5 (Balanced)** [DEFAULT]: Standard matching with some flexibility
  - Best for: General resume screening
  
- **0.9 (Strict)**: Requires exact or very similar matches
  - Best for: Specialized roles, critical skills

#### Skill Definition

Use specific technical skills:
- Programming Languages: Python, JavaScript, Java, C++, Go, Rust
- Frameworks: React, Vue, Angular, Django, Flask, FastAPI
- Databases: PostgreSQL, MongoDB, Redis, DynamoDB
- Cloud Platforms: AWS, Azure, GCP, Heroku
- DevOps: Docker, Kubernetes, Jenkins, GitLab CI/CD
- AI/ML: Machine Learning, TensorFlow, PyTorch, NLP

## 🏗️ Project Structure

```
resume-analyzer/
├── frontend/                 # React Frontend
│   ├── index.html           # Main HTML
│   ├── script.js            # Frontend logic (13KB, professional)
│   └── style.css            # Professional styling
│
├── backend/                 # FastAPI Backend
│   ├── main.py             # FastAPI app initialization
│   ├── analyzer.py         # Core analysis engine
│   ├── database.py         # Database operations
│   ├── models.py           # Pydantic models
│   ├── utils.py            # Utility functions
│   └── routes/
│       ├── analyze.py      # Resume analysis endpoint
│       ├── history.py      # History endpoint
│       └── compare.py      # Comparison endpoint
│
├── database/                # SQLite database
│   └── analyzer.db
│
├── requirements.txt         # Python dependencies
├── app.py                  # WSGI entry point
├── config.py               # Configuration
└── README.md               # This file
```

## 🔌 API Endpoints

### POST /api/analyze

Analyze uploaded resumes against job description.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -F "files=@resume1.pdf" \
  -F "files=@resume2.pdf" \
  -F "job_description=Python Django AWS Docker PostgreSQL" \
  -F "sensitivity=0.5"
```

**Parameters:**
- `files` (required): PDF resume files
- `job_description` (required): Skills/requirements text
- `sensitivity` (optional): 0.3-0.9, default 0.5

**Response:**
```json
{
  "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
  "candidates": [
    {
      "name": "John Doe",
      "matched_count": 5,
      "missing_count": 2,
      "match_percentage": 71.4,
      "matched_skills": ["Python", "Django", "PostgreSQL"],
      "missing_skills": ["AWS", "Docker"],
      "suggestions": ["Learn AWS for career growth"]
    }
  ],
  "statistics": {
    "average_score": 0.64,
    "most_matched_skill": "Python",
    "least_matched_skill": "Docker",
    "total_unique_skills": 7
  },
  "timestamp": "2024-06-12T18:30:00.000Z"
}
```

### GET /api/status

Get API status and available endpoints.

```bash
curl "http://localhost:8000/api/status"
```

### GET /health

Health check endpoint.

```bash
curl "http://localhost:8000/health"
```

## 🎯 How It Works

### 1. PDF Processing

- Validates file type and size
- Detects PDF corruption
- Extracts text using PyPDF2
- Handles multi-page documents
- Validates text length

### 2. Skill Extraction

- Uses rule-based keyword matching
- Supports 80+ skill variations
- Case-insensitive matching
- Handles compound skills (e.g., "Machine Learning")

### 3. Similarity Analysis

- Implements Jaccard similarity algorithm
- Semantic-based matching
- Configurable sensitivity thresholds
- Calculates match percentages

### 4. Ranking & Statistics

- Ranks candidates by match percentage
- Calculates aggregate statistics
- Identifies most/least matched skills
- Generates improvement suggestions

## 📊 Analysis Metrics

- **Match Count**: Number of matched skills (max 15)
- **Match Percentage**: Proportion of matched skills (0-100%)
- **Average Score**: Mean match percentage across all candidates
- **Top Skill**: Most frequently matched skill
- **Least Matched**: Most commonly missing skill

## 🛡️ Error Handling

The system includes comprehensive error handling:

| Error | Description | Solution |
|-------|-------------|----------|
| File too large | > 10MB | Upload smaller files |
| Invalid format | Not PDF | Ensure files are PDF format |
| Empty PDF | No text extracted | Verify PDF contains readable text |
| No skills extracted | Job description too vague | Be more specific with skills |
| Server error | Backend crash | Check server logs, restart |

## 🔍 Troubleshooting

### PDF Upload Fails

1. **Check file size**: Must be ≤ 10MB
2. **Verify format**: Must be PDF
3. **Test file**: Try with different PDF file
4. **Browser cache**: Clear cache and try again

### No Results Returned

1. **Check job description**: Must be ≥ 10 characters
2. **Include specific skills**: Generic descriptions don't work
3. **Check browser console**: Press F12 for error messages
4. **Check server logs**: Look for detailed errors

### Slow Processing

1. **File size**: Large PDFs take longer
2. **Network**: Check internet connection
3. **Server load**: Multiple users may slow processing
4. **Browser**: Try different browser

## 📈 Performance Metrics

- **Single Resume**: ~1-2 seconds
- **10 Resumes**: ~5-10 seconds
- **50 Resumes**: ~20-40 seconds
- **Memory Usage**: ~500MB-2GB depending on file size

## 🔐 Security Considerations

✅ **What's Protected:**
- Input validation on all fields
- File type verification
- Size limits enforcement
- CORS protection
- SQL injection prevention

⚠️ **Best Practices:**
- Use HTTPS in production
- Keep dependencies updated
- Regular security audits
- Monitor server logs
- Implement rate limiting

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| FastAPI | 0.104+ | Web framework |
| Uvicorn | 0.24+ | ASGI server |
| PyPDF2 | 3.0.1 | PDF processing |
| Pydantic | 2.0+ | Data validation |
| Sentence-Transformers | Latest | NLP embeddings |
| PyTorch | Latest | Deep learning |

## 🚀 Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "app:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker"]
```

### Cloud Deployment (Heroku)

1. Add `Procfile`:
```
web: gunicorn app:app --worker-class uvicorn.workers.UvicornWorker
```

2. Deploy:
```bash
git push heroku main
```

### Environment Variables

Set in production:
```
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql://...
```

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open pull request

## 📧 Support

For issues, questions, or suggestions:
- Open an GitHub issue
- Contact: support@resumeanalyzer.dev
- Documentation: https://docs.resumeanalyzer.dev

## 🎓 Learn More

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PyPDF2 Guide](https://pypdf2.readthedocs.io/)
- [Semantic Similarity](https://en.wikipedia.org/wiki/Semantic_similarity)
- [Jaccard Index](https://en.wikipedia.org/wiki/Jaccard_index)

---

**Made with ❤️ by AI Resume Analyzer Team**

Version 2.0 | Last Updated: June 2024
