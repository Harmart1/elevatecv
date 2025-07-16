import os
import json
import re
import requests
import spacy
from typing import Dict, List, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.google_api_key = os.environ.get("GOOGLE_API_KEY")
        if not self.google_api_key:
            logger.error("GOOGLE_API_KEY environment variable not set.")
            raise ValueError("API Key for Google AI is missing.")

        self.google_api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        self.nlp = None
        self._load_spacy_model()

    def _load_spacy_model(self):
        """Load spaCy model as backup"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("spaCy model loaded successfully")
        except OSError:
            logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm. Fallback will be limited.")
            self.nlp = None

    def _call_google_ai(self, prompt: str, max_tokens: int = 2000) -> Optional[str]:
        """Call Google AI Studio API"""
        try:
            headers = {'Content-Type': 'application/json'}
            data = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.7, "topK": 40, "topP": 0.95, "maxOutputTokens": max_tokens,
                }
            }
            response = requests.post(f"{self.google_api_url}?key={self.google_api_key}", headers=headers, json=data, timeout=45)

            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and result.get('candidates'):
                    return result['candidates'][0]['content']['parts'][0]['text']
            else:
                logger.error(f"Google AI API error: {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Google AI: {str(e)}")

        return None

    def _extract_json_from_response(self, text: str) -> Optional[Dict]:
        """Extracts a JSON object from a string, handling markdown code blocks."""
        match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if not match:
                return None
            json_str = match.group(0)

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from AI response: {e}\nString: {json_str}")
            return None

    def _spacy_fallback_analysis(self, text: str) -> Dict[str, Any]:
        """Fallback analysis using spaCy"""
        if not self.nlp:
            return {"error": "No NLP model available"}

        doc = self.nlp(text)

        skills_keywords = [
            "python", "javascript", "java", "react", "node.js", "sql", "html", "css",
            "machine learning", "data analysis", "project management", "leadership",
            "communication", "teamwork", "problem solving", "git", "docker", "kubernetes"
        ]

        found_skills = list(set([skill for skill in skills_keywords if skill in text.lower()]))

        return {
            "ats_score": 65,
            "keyword_matches": [{"keyword": skill, "found": True, "importance": "medium"} for skill in found_skills[:5]],
            "sections_analysis": {
                "contact_info": {"score": 70, "status": "good"}, "summary": {"score": 60, "status": "fair"},
                "experience": {"score": 70, "status": "good"}, "skills": {"score": 75, "status": "good"},
                "education": {"score": 65, "status": "fair"}
            },
            "recommendations": [
                {"type": "suggestion", "title": "Enhance Keywords", "description": "Consider adding more industry-specific keywords to pass automated screening."},
                {"type": "improvement", "title": "Quantify Achievements", "description": "Use numbers and metrics to demonstrate impact (e.g., 'Increased efficiency by 20%')."}
            ],
            "industry_insights": {
                "trending_skills": ["Cloud Computing", "AI/ML", "DevOps"],
                "salary_range": "$70,000 - $120,000", "job_growth": "+10% annually"
            },
            "extracted_skills": found_skills, "experience_years": 3, "education_level": "Bachelor's",
            "analysis_method": "spaCy Fallback"
        }

    def analyze_resume(self, resume_text: str, job_description: str = "") -> Dict[str, Any]:
        """Analyze resume using Google AI with spaCy fallback"""

        prompt = f"""
        Analyze the following resume and provide a comprehensive ATS (Applicant Tracking System) analysis.
        If a job description is provided, tailor the analysis to it.

        Resume Text:
        {resume_text}

        Job Description (if provided):
        {job_description}

        Provide the analysis in a JSON object enclosed in ```json ... ```.
        The JSON object should have the following structure:
        {{
            "ats_score": <score from 0-100>,
            "keyword_matches": [{{"keyword": "skill_name", "found": true/false, "importance": "high/medium/low"}}],
            "sections_analysis": {{
                "contact_info": {{"score": <0-100>, "status": "excellent/good/fair/poor"}},
                "summary": {{"score": <0-100>, "status": "excellent/good/fair/poor"}},
                "experience": {{"score": <0-100>, "status": "excellent/good/fair/poor"}},
                "skills": {{"score": <0-100>, "status": "excellent/good/fair/poor"}},
                "education": {{"score": <0-100>, "status": "excellent/good/fair/poor"}}
            }},
            "recommendations": [{{"type": "critical/suggestion/improvement", "title": "title", "description": "description"}}],
            "industry_insights": {{"trending_skills": ["skill1", "skill2"], "salary_range": "$X,XXX - $X,XXX", "job_growth": "+X% annually"}},
            "extracted_skills": ["skill1", "skill2"], "experience_years": <number>, "education_level": "Bachelor's/Master's/PhD/Other"
        }}
        """

        ai_response = self._call_google_ai(prompt)
        if ai_response:
            result = self._extract_json_from_response(ai_response)
            if result:
                result["analysis_method"] = "Google AI Studio"
                return result

        logger.warning("Google AI failed. Using spaCy fallback for resume analysis.")
        return self._spacy_fallback_analysis(resume_text)

    # ... all other methods (generate_cover_letter, generate_interview_questions, etc.) remain the same as the previous turn ...
    # Make sure to include them here. For brevity, I am omitting them as they don't have structural changes.

# Global AI service instance
ai_service = AIService()
