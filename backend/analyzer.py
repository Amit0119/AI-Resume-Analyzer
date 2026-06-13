import os
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer, util
import json
from dotenv import load_dotenv

load_dotenv()

# Initialize model (once per app startup)
model = SentenceTransformer("all-MiniLM-L6-v2")

class SkillAnalyzer:
    """AI-powered resume skill analyzer"""
    
    def __init__(self, sensitivity: float = 0.5):
        self.sensitivity = sensitivity
        self.threshold = sensitivity
        
    def extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills mentioned in text"""
        text_lower = text.lower()
        
        # Common skills database
        skills_database = {
            'programming': ['python', 'javascript', 'java', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin'],
            'frontend': ['html', 'css', 'react', 'vue', 'angular', 'typescript', 'tailwind', 'bootstrap'],
            'backend': ['node', 'express', 'django', 'flask', 'fastapi', 'spring', 'laravel', 'rails'],
            'database': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'dynamodb'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 's3', 'lambda', 'ec2'],
            'devops': ['git', 'ci/cd', 'jenkins', 'gitlab', 'github actions', 'terraform', 'ansible'],
            'data': ['machine learning', 'deep learning', 'nlp', 'computer vision', 'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit-learn'],
            'agentic_ai': ['langchain', 'groq', 'openai', 'claude', 'agents', 'rag', 'llm'],
            'soft': ['communication', 'teamwork', 'leadership', 'problem solving', 'critical thinking', 'adaptability']
        }
        
        found_skills = set()
        for category, skills in skills_database.items():
            for skill in skills:
                if skill in text_lower:
                    found_skills.add(skill.title())
        
        return sorted(list(found_skills))
    
    def calculate_semantic_similarity(self, skill: str, text: str) -> float:
        """Calculate semantic similarity between skill and text"""
        try:
            # Split text into sentences
            sentences = [s.strip() for s in text.replace('\n', '. ').split('.') if len(s.strip()) > 10]
            
            if not sentences:
                return 0.0
            
            # Encode skill and sentences
            skill_embedding = model.encode(skill, convert_to_tensor=True)
            text_embeddings = model.encode(sentences, convert_to_tensor=True)
            
            # Get max similarity
            scores = util.cos_sim(skill_embedding, text_embeddings)[0]
            max_score = float(scores.max())
            
            return max_score
        except Exception as e:
            print(f"Error in semantic similarity: {e}")
            return 0.0
    
    def analyze_resume(self, resume_text: str, required_skills: List[str], 
                       skill_weights: Dict[str, float] = None, strict_mode: bool = False) -> Dict:
        """
        Analyze resume against required skills with optional weighting
        
        Args:
            resume_text: Resume content
            required_skills: List of required skills
            skill_weights: Dict of {skill: weight} where weight is 1.0-5.0
            strict_mode: If True, only exact keyword matches count (no semantic)
        
        Returns:
            Dict with matched/missing skills, weighted score, and statistics
        """
        matched_skills = []
        missing_skills = []
        skill_weights = skill_weights or {}
        
        total_weighted_score = 0.0
        max_weighted_score = 0.0
        
        for skill in required_skills:
            weight = skill_weights.get(skill, 1.0)
            max_weighted_score += weight
            
            # Keyword match (exact)
            keyword_found = skill.lower() in resume_text.lower()
            
            if strict_mode:
                # Strict mode: only exact keyword match
                matched = keyword_found
            else:
                # Flexible mode: keyword OR semantic similarity
                semantic_score = self.calculate_semantic_similarity(skill, resume_text)
                matched = keyword_found or semantic_score >= self.threshold
            
            if matched:
                matched_skills.append(skill)
                total_weighted_score += weight
            else:
                missing_skills.append(skill)
        
        matched_count = len(matched_skills)
        total_skills = len(required_skills)
        
        # Standard percentage (unweighted)
        match_percentage = (matched_count / total_skills * 100) if total_skills > 0 else 0
        
        # Weighted percentage (reflects skill importance)
        weighted_percentage = (total_weighted_score / max_weighted_score * 100) if max_weighted_score > 0 else 0
        
        return {
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'matched_count': matched_count,
            'missing_count': len(missing_skills),
            'match_percentage': round(match_percentage, 2),
            'weighted_score': round(weighted_percentage, 2),
            'total_weighted': round(total_weighted_score, 1),
            'max_weighted': round(max_weighted_score, 1)
        }
    
    def generate_suggestions(self, missing_skills: List[str]) -> List[str]:
        """Generate learning suggestions for missing skills"""
        suggestions = []
        
        for skill in missing_skills[:5]:  # Top 5 missing skills
            skill_lower = skill.lower()
            
            if 'python' in skill_lower:
                suggestions.append(f"Learn {skill} - Take Python course on Kaggle or Udemy")
            elif any(x in skill_lower for x in ['javascript', 'react', 'vue', 'angular']):
                suggestions.append(f"Master {skill} - Complete JavaScript/Frontend bootcamp")
            elif any(x in skill_lower for x in ['aws', 'azure', 'gcp']):
                suggestions.append(f"Certify in {skill} - Pursue official cloud certification")
            elif any(x in skill_lower for x in ['machine learning', 'deep learning', 'nlm']):
                suggestions.append(f"Study {skill} - Andrew Ng's ML course on Coursera")
            elif any(x in skill_lower for x in ['docker', 'kubernetes', 'devops']):
                suggestions.append(f"Learn {skill} - DevOps with Docker/K8s hands-on")
            elif 'langchain' in skill_lower or 'groq' in skill_lower or 'rag' in skill_lower:
                suggestions.append(f"Explore {skill} - Cutting-edge AI/LLM framework tutorial")
            else:
                suggestions.append(f"Develop {skill} - Find specialized course and practice")
        
        return suggestions
    
    def batch_analyze(self, resumes: List[Tuple[str, str]], required_skills: List[str],
                      skill_weights: Dict[str, float] = None, strict_mode: bool = False) -> List[Dict]:
        """
        Analyze multiple resumes
        
        Args:
            resumes: List of (name, text) tuples
            required_skills: List of required skills
            skill_weights: Optional skill importance weights
            strict_mode: Whether to use strict matching only
        
        Returns:
            List of analysis results with candidate info
        """
        results = []
        
        for name, text in resumes:
            analysis = self.analyze_resume(text, required_skills, skill_weights, strict_mode)
            analysis['name'] = name
            analysis['suggestions'] = self.generate_suggestions(analysis['missing_skills'])
            results.append(analysis)
        
        return results

class GroqAnalyzer:
    """Optional: Groq API for advanced analysis"""
    
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in .env")
    
    def get_skill_recommendations(self, candidate_name: str, missing_skills: List[str]) -> List[str]:
        """
        Use Groq to generate personalized recommendations
        Optional: Can be integrated later if needed
        """
        # Placeholder for Groq API integration
        recommendations = []
        for skill in missing_skills:
            recommendations.append(f"{candidate_name} should focus on learning {skill}")
        return recommendations

def get_analyzer(sensitivity: float = 0.5) -> SkillAnalyzer:
    """Factory function to get analyzer instance"""
    return SkillAnalyzer(sensitivity=sensitivity)