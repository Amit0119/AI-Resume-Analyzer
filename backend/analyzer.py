import os
from typing import List, Dict, Tuple
import json

class SkillAnalyzer:
    """Lightweight resume skill analyzer - keyword based"""
    
    def __init__(self, sensitivity: float = 0.5):
        self.sensitivity = sensitivity
        self.threshold = sensitivity
    
    def extract_skills_from_text(self, text: str) -> List[str]:
        text_lower = text.lower()
        skills_database = {
            'programming': ['python', 'javascript', 'java', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin'],
            'frontend': ['html', 'css', 'react', 'vue', 'angular', 'typescript', 'tailwind', 'bootstrap'],
            'backend': ['node', 'express', 'django', 'flask', 'fastapi', 'spring', 'laravel', 'rails'],
            'database': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'dynamodb'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 's3', 'lambda', 'ec2'],
            'devops': ['git', 'ci/cd', 'jenkins', 'gitlab', 'github actions', 'terraform', 'ansible'],
            'data': ['machine learning', 'deep learning', 'nlp', 'tensorflow', 'pytorch', 'pandas', 'numpy'],
            'soft': ['communication', 'teamwork', 'leadership', 'problem solving']
        }
        found_skills = set()
        for category, skills in skills_database.items():
            for skill in skills:
                if skill in text_lower:
                    found_skills.add(skill.title())
        return sorted(list(found_skills))

    def analyze_resume(self, resume_text: str, required_skills: List[str],
                      skill_weights: Dict[str, float] = None, strict_mode: bool = False) -> Dict:
        matched_skills = []
        missing_skills = []
        skill_weights = skill_weights or {}
        total_weighted_score = 0.0
        max_weighted_score = 0.0

        for skill in required_skills:
            weight = skill_weights.get(skill, 1.0)
            max_weighted_score += weight
            keyword_found = skill.lower() in resume_text.lower()
            if keyword_found:
                matched_skills.append(skill)
                total_weighted_score += weight
            else:
                missing_skills.append(skill)

        matched_count = len(matched_skills)
        total_skills = len(required_skills)
        match_percentage = (matched_count / total_skills * 100) if total_skills > 0 else 0
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
        suggestions = []
        for skill in missing_skills[:5]:
            skill_lower = skill.lower()
            if 'python' in skill_lower:
                suggestions.append(f"Learn {skill} - Take Python course on Kaggle or Udemy")
            elif any(x in skill_lower for x in ['javascript', 'react', 'vue']):
                suggestions.append(f"Master {skill} - Complete JavaScript/Frontend bootcamp")
            elif any(x in skill_lower for x in ['aws', 'azure', 'gcp']):
                suggestions.append(f"Certify in {skill} - Pursue official cloud certification")
            elif any(x in skill_lower for x in ['docker', 'kubernetes']):
                suggestions.append(f"Learn {skill} - DevOps hands-on practice")
            else:
                suggestions.append(f"Develop {skill} - Find specialized course and practice")
        return suggestions

    def batch_analyze(self, resumes: List[Tuple[str, str]], required_skills: List[str],
                     skill_weights: Dict[str, float] = None, strict_mode: bool = False) -> List[Dict]:
        results = []
        for name, text in resumes:
            analysis = self.analyze_resume(text, required_skills, skill_weights, strict_mode)
            analysis['name'] = name
            analysis['suggestions'] = self.generate_suggestions(analysis['missing_skills'])
            results.append(analysis)
        return results

def get_analyzer(sensitivity: float = 0.5) -> SkillAnalyzer:
    return SkillAnalyzer(sensitivity=sensitivity)