import sqlite3
import os
from contextlib import contextmanager
from typing import Optional, List, Dict
from datetime import datetime

DATABASE_PATH = os.path.join(os.path.dirname(__file__), '../database/analyzer.db')

def init_db():
    """Initialize database with tables"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Analyses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_description TEXT NOT NULL,
            num_resumes INTEGER NOT NULL,
            average_score REAL NOT NULL,
            best_candidate TEXT NOT NULL,
            best_score INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Candidates table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            matched_count INTEGER NOT NULL,
            missing_count INTEGER NOT NULL,
            match_percentage REAL NOT NULL,
            matched_skills TEXT NOT NULL,
            missing_skills TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (analysis_id) REFERENCES analyses(id)
        )
    ''')
    
    conn.commit()
    conn.close()

@contextmanager
def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def save_analysis(job_description: str, results: Dict) -> int:
    """Save analysis to database"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        candidates = results['candidates']
        best_candidate = max(candidates, key=lambda x: x['matched_count'])
        avg_score = sum(c['matched_count'] for c in candidates) / len(candidates)
        
        cursor.execute('''
            INSERT INTO analyses 
            (job_description, num_resumes, average_score, best_candidate, best_score)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            job_description,
            len(candidates),
            avg_score,
            best_candidate['name'],
            best_candidate['matched_count']
        ))
        
        analysis_id = cursor.lastrowid
        
        # Insert candidates
        for candidate in candidates:
            cursor.execute('''
                INSERT INTO candidates
                (analysis_id, name, matched_count, missing_count, match_percentage, 
                 matched_skills, missing_skills)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                analysis_id,
                candidate['name'],
                candidate['matched_count'],
                candidate['missing_count'],
                candidate['match_percentage'],
                ','.join(candidate['matched_skills']),
                ','.join(candidate['missing_skills'])
            ))
        
        conn.commit()
        return analysis_id

def get_all_analyses(limit: int = 50) -> List[Dict]:
    """Get all analyses from database"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM analyses 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        return [dict(row) for row in cursor.fetchall()]

def get_analysis_with_candidates(analysis_id: int) -> Optional[Dict]:
    """Get analysis with all its candidates"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM analyses WHERE id = ?', (analysis_id,))
        analysis = cursor.fetchone()
        
        if not analysis:
            return None
        
        cursor.execute('''
            SELECT * FROM candidates WHERE analysis_id = ? 
            ORDER BY matched_count DESC
        ''', (analysis_id,))
        candidates = [dict(row) for row in cursor.fetchall()]
        
        # Parse skills back to lists
        for candidate in candidates:
            candidate['matched_skills'] = candidate['matched_skills'].split(',') if candidate['matched_skills'] else []
            candidate['missing_skills'] = candidate['missing_skills'].split(',') if candidate['missing_skills'] else []
        
        return {
            'analysis': dict(analysis),
            'candidates': candidates
        }

def delete_analysis(analysis_id: int) -> bool:
    """Delete analysis and its candidates"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM candidates WHERE analysis_id = ?', (analysis_id,))
        cursor.execute('DELETE FROM analyses WHERE id = ?', (analysis_id,))
        conn.commit()
        return cursor.rowcount > 0

def search_analyses(query: str) -> List[Dict]:
    """Search analyses by candidate name or job description"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT a.* FROM analyses a
            LEFT JOIN candidates c ON a.id = c.analysis_id
            WHERE c.name LIKE ? OR a.job_description LIKE ?
            ORDER BY a.created_at DESC
        ''', (f'%{query}%', f'%{query}%'))
        return [dict(row) for row in cursor.fetchall()]

# Initialize database on import
if not os.path.exists(DATABASE_PATH):
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    init_db()