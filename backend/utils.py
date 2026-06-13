"""
Utility functions for resume analysis
- PDF extraction with error handling
- File validation
- Skill extraction and processing
- Text cleaning and normalization
"""

from typing import List, Dict, Optional
from PyPDF2 import PdfReader
import io
import logging

logger = logging.getLogger(__name__)

# Configuration constants
MAX_PDF_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_FILE_PAGES = 50
MIN_RESUME_TEXT_LENGTH = 100

def validate_pdf_file(filename: str, file_content: Optional[bytes] = None) -> tuple[bool, str]:
    """
    Comprehensive PDF file validation
    
    Args:
        filename: Name of the file
        file_content: File bytes content
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check file extension
    if not filename.lower().endswith('.pdf'):
        return False, f"Invalid file format. Expected PDF, got {filename.split('.')[-1]}"
    
    # Check file size
    if file_content and len(file_content) > MAX_PDF_SIZE:
        size_mb = len(file_content) / (1024 * 1024)
        return False, f"File size {size_mb:.2f}MB exceeds maximum allowed size of 10MB"
    
    # Check minimum file size (empty files are suspicious)
    if file_content and len(file_content) < 100:
        return False, "File appears to be empty or corrupted"
    
    return True, ""

def extract_text_from_pdf(pdf_content: bytes) -> tuple[str, Optional[str]]:
    """
    Extract text from PDF with comprehensive error handling
    
    Args:
        pdf_content: PDF file bytes
    
    Returns:
        Tuple of (extracted_text, error_message)
    """
    try:
        # Validate input
        if not pdf_content:
            return "", "PDF content is empty"
        
        # Create PDF reader
        pdf_reader = PdfReader(io.BytesIO(pdf_content))
        
        # Check if PDF has pages
        if len(pdf_reader.pages) == 0:
            return "", "PDF has no pages to extract text from"
        
        # Extract text from all pages
        full_text = ""
        page_count = 0
        
        for page_num, page in enumerate(pdf_reader.pages):
            # Safety check for too many pages
            if page_num >= MAX_FILE_PAGES:
                logger.warning(f"PDF has more than {MAX_FILE_PAGES} pages, stopping extraction")
                break
            
            try:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"
                    page_count += 1
            except Exception as e:
                logger.warning(f"Error extracting text from page {page_num + 1}: {str(e)}")
                continue
        
        # Check if we extracted any text
        if not full_text.strip():
            return "", "No text could be extracted from the PDF. It may be a scanned image."
        
        # Check minimum text length
        if len(full_text.strip()) < MIN_RESUME_TEXT_LENGTH:
            return "", "Extracted text is too short. Resume may be incomplete."
        
        logger.info(f"Successfully extracted text from {page_count} pages ({len(full_text)} characters)")
        return full_text.strip(), None
        
    except Exception as e:
        error_msg = f"PDF extraction error: {str(e)}"
        logger.error(error_msg)
        return "", error_msg

def extract_candidate_name_from_pdf(text: str) -> str:
    """
    Extract candidate name from resume text
    
    Args:
        text: Resume text content
    
    Returns:
        Extracted name or "Unknown Candidate"
    """
    try:
        # Defensive: handle None or non-string
        if not text or not isinstance(text, str):
            return "Unknown Candidate"
        
        lines = text.split('\n')
        
        # Look in first 10 lines for a name
        for line in lines[:10]:
            line = line.strip()
            
            # Skip empty lines and very long lines
            if not line or len(line) > 80:
                continue
            
            # Check if line looks like a name (2-5 words, all capitalized)
            words = line.split()
            if 2 <= len(words) <= 5:
                # Check if it starts with capital letters
                if all(word[0].isupper() for word in words if len(word) > 0):
                    # Additional check: not too many numbers
                    if sum(1 for c in line if c.isdigit()) < 3:
                        return line
        
        # Fallback to first non-empty line that looks reasonable
        for line in lines[:20]:
            line = line.strip()
            if line and len(line) < 80 and any(c.isalpha() for c in line):
                return line
        
        return "Unknown Candidate"
        
    except Exception as e:
        logger.warning(f"Error extracting name: {str(e)}")
        return "Unknown Candidate"

def clean_text(text: str) -> str:
    """
    Clean and normalize text for processing
    
    Args:
        text: Raw text
    
    Returns:
        Cleaned lowercase text
    """
    # Remove extra whitespace
    text = ' '.join(text.split())
    # Convert to lowercase
    return text.lower()

def calculate_similarity(list1: List[str], list2: List[str]) -> float:
    """
    Calculate Jaccard similarity between two lists
    
    Args:
        list1: First list of items
        list2: Second list of items
    
    Returns:
        Similarity score (0-1)
    """
    if not list1 or not list2:
        return 0.0 if list1 or list2 else 1.0
    
    # Convert to sets for comparison
    set1 = set(item.lower().strip() for item in list1)
    set2 = set(item.lower().strip() for item in list2)
    
    # Calculate Jaccard similarity
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    
    return intersection / union if union > 0 else 0.0

def format_skill_name(skill: str) -> str:
    """
    Format skill name for display
    
    Args:
        skill: Raw skill name
    
    Returns:
        Properly formatted skill name
    """
    # Capitalize each word
    return ' '.join(word.capitalize() for word in skill.split())

def get_skills_from_description(job_description: str, max_skills: int = 15) -> List[str]:
    """
    Extract relevant skills from job description text
    
    Args:
        job_description: Job description text
        max_skills: Maximum number of skills to extract
    
    Returns:
        List of extracted skills
    """
    # Comprehensive skill keywords database
    skill_keywords = {
        'programming_languages': [
            'python', 'javascript', 'typescript', 'java', 'c++', 'c#', 'php', 
            'ruby', 'go', 'rust', 'swift', 'kotlin', 'scala', 'perl'
        ],
        'frontend': [
            'react', 'vue', 'angular', 'html', 'css', 'tailwind', 'bootstrap',
            'webpack', 'babel', 'nextjs', 'svelte', 'jquery'
        ],
        'backend': [
            'node', 'express', 'django', 'flask', 'fastapi', 'spring', 'rails',
            'laravel', 'asp.net', 'gin', 'echo', 'fiber'
        ],
        'database': [
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            'dynamodb', 'firebase', 'cassandra', 'mariadb', 'oracle'
        ],
        'cloud': [
            'aws', 'azure', 'gcp', 'heroku', 'netlify', 'vercel', 'digital ocean',
            'linode', 'vultr', 'ibm cloud'
        ],
        'devops': [
            'docker', 'kubernetes', 'git', 'jenkins', 'gitlab', 'github', 'ci/cd',
            'terraform', 'ansible', 'prometheus', 'grafana', 'gitlab-ci'
        ],
        'ai_ml': [
            'machine learning', 'deep learning', 'nlp', 'computer vision',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',
            'keras', 'opencv'
        ],
        'agentic_ai': [
            'langchain', 'groq', 'openai', 'claude', 'agents', 'rag', 'llm',
            'embeddings', 'vector databases', 'prompt engineering'
        ],
        'tools': [
            'git', 'docker', 'jira', 'slack', 'figma', 'vscode', 'postman',
            'datadog', 'newrelic', 'splunk', 'kibana'
        ],
        'soft_skills': [
            'leadership', 'communication', 'problem solving', 'teamwork',
            'project management', 'agile', 'scrum'
        ]
    }
    
    # Convert job description to lowercase for matching
    job_desc_lower = job_description.lower()
    found_skills = set()
    
    # Search for each skill in the job description
    for category, skills in skill_keywords.items():
        for skill in skills:
            if skill.lower() in job_desc_lower:
                found_skills.add(format_skill_name(skill))
    
    # Return top max_skills sorted alphabetically
    return sorted(list(found_skills))[:max_skills]

def generate_report_text(analysis_results: Dict) -> str:
    """
    Generate a professional text report from analysis results
    
    Args:
        analysis_results: Analysis results dictionary
    
    Returns:
        Formatted report text
    """
    from datetime import datetime
    
    report = "=" * 70 + "\n"
    report += "AI RESUME ANALYZER - PROFESSIONAL ANALYSIS REPORT\n"
    report += "=" * 70 + "\n\n"
    
    report += f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}\n"
    report += f"Report Version: 2.0\n\n"
    
    # Overall Statistics
    report += "OVERALL STATISTICS\n"
    report += "-" * 70 + "\n"
    
    candidates = analysis_results.get('candidates', [])
    stats = analysis_results.get('statistics', {})
    
    report += f"Total Resumes Analyzed: {len(candidates)}\n"
    report += f"Average Match Score: {stats.get('average_score', 0):.1%}\n"
    report += f"Most Matched Skill: {stats.get('most_matched_skill', 'N/A')}\n"
    report += f"Least Matched Skill: {stats.get('least_matched_skill', 'N/A')}\n"
    report += f"Total Unique Skills Required: {stats.get('total_unique_skills', 0)}\n\n"
    
    # Candidate Details
    report += "CANDIDATE DETAILS\n"
    report += "-" * 70 + "\n\n"
    
    for idx, candidate in enumerate(candidates, 1):
        report += f"CANDIDATE #{idx}: {candidate['name']}\n"
        report += f"  Match Score: {candidate['matched_count']}/15 ({candidate['match_percentage']:.1f}%)\n"
        
        matched = candidate.get('matched_skills', [])
        missing = candidate.get('missing_skills', [])
        
        report += f"  Matched Skills ({len(matched)}): {', '.join(matched) if matched else 'None'}\n"
        report += f"  Missing Skills ({len(missing)}): {', '.join(missing) if missing else 'None'}\n"
        
        suggestions = candidate.get('suggestions', [])
        if suggestions:
            report += f"  Recommendations:\n"
            for i, suggestion in enumerate(suggestions[:3], 1):
                report += f"    {i}. {suggestion}\n"
        
        report += "\n"
    
    report += "=" * 70 + "\n"
    report += "END OF REPORT\n"
    report += "=" * 70 + "\n"
    
    return report

def estimate_reading_time(text: str) -> int:
    """
    Estimate reading time in minutes
    
    Args:
        text: Text content
    
    Returns:
        Estimated reading time in minutes
    """
    words = len(text.split())
    reading_speed = 200  # Average reading speed in words per minute
    minutes = max(1, round(words / reading_speed))
    return minutes
