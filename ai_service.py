import os
import json
import re
import requests
import spacy
from typing import Dict, List, Optional, Any
import logging
from bs4 import BeautifulSoup

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
                if 'candidates' in result and len(result['candidates']) > 0:
                    return result['candidates'][0]['content']['parts'][0]['text']
            else:
                logger.error(f"Google AI API error: {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Google AI: {str(e)}")

        return None

    def _extract_json_from_response(self, text: str) -> Optional[Dict]:
        """Extracts a JSON object from a string, handling markdown code blocks."""
        # Pattern to find JSON within ```json ... ```
        match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            # Fallback for plain JSON
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if not match:
                return None
            json_str = match.group(0)

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from AI response: {e}")
            logger.error(f"Problematic JSON string: {json_str}")
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

    def _research_company(self, company_name: str) -> str:
        """Research company using a search engine."""
        try:
            from googlesearch import search
        except ImportError:
            logger.warning("googlesearch library not found. Skipping company research.")
            return ""

        try:
            query = f"{company_name} company values mission"
            # get the first 3 results
            search_results = list(search(query, num=3, stop=3, pause=2))

            company_info = ""
            for url in search_results:
                try:
                    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    # Extract text from the body, limiting the length
                    text = soup.body.get_text(separator=' ', strip=True)
                    company_info += text[:1500] + "\n\n"
                except requests.exceptions.RequestException as e:
                    logger.warning(f"Could not fetch {url}: {e}")

            return company_info
        except Exception as e:
            logger.error(f"Error during company research: {e}")
            return ""

    def generate_cover_letter(self, resume_text: str, job_description: str, company_name: str = "", position_title: str = "") -> Dict[str, Any]:
        """Generate cover letter using Google AI"""

        company_research = self._research_company(company_name)

        prompt = f"""
        Generate a professional cover letter based on the following information.
        Resume/Background: {resume_text}
        Job Description: {job_description}
        Company Name: {company_name}
        Position Title: {position_title}
        Company Research (values, mission, etc.): {company_research}

        Create a compelling cover letter that highlights relevant experience, addresses job requirements, shows enthusiasm, and maintains a professional tone.
        Incorporate insights from the company research to show genuine interest.
        Format the response as a JSON object enclosed in ```json ... ```:
        {{
            "cover_letter": "full cover letter text",
            "key_points": ["point1", "point2", "point3"],
            "customization_tips": ["tip1", "tip2", "tip3"]
        }}
        """

        ai_response = self._call_google_ai(prompt)
        if ai_response:
            result = self._extract_json_from_response(ai_response)
            if result:
                result["generation_method"] = "Google AI Studio"
                return result

        logger.warning("Google AI failed. Using fallback for cover letter generation.")
        return {
            "cover_letter": f"Dear Hiring Manager,\n\nI am writing to express my interest in the {position_title or 'advertised'} position at {company_name or 'your company'}. Based on my experience detailed in my resume, I am confident I possess the skills to excel in this role.\n\nI am eager to learn more about this opportunity and discuss how I can contribute to your team.\n\nSincerely,\n[Your Name]",
            "key_points": ["State your interest clearly.", "Connect your experience to the role.", "End with a call to action."],
            "customization_tips": ["Address the hiring manager by name if possible.", "Mention one specific thing about the company that excites you."],
            "generation_method": "Fallback Template"
        }

    def generate_interview_questions(self, job_description: str, position_level: str = "mid") -> Dict[str, Any]:
        """Generate interview questions using Google AI"""

        prompt = f"""
        Generate comprehensive interview questions for the following job.
        Job Description: {job_description}
        Position Level: {position_level}

        Create questions in these categories: Technical, Behavioral, Situational, and Company Culture Fit.
        Format as a JSON object enclosed in ```json ... ```:
        {{
            "technical_questions": [{{"question": "text", "difficulty": "medium", "category": "technical"}}],
            "behavioral_questions": [{{"question": "text", "difficulty": "medium", "category": "behavioral"}}],
            "situational_questions": [{{"question": "text", "difficulty": "hard", "category": "situational"}}],
            "culture_questions": [{{"question": "text", "difficulty": "easy", "category": "culture"}}],
            "preparation_tips": ["tip1", "tip2", "tip3"]
        }}
        """

        ai_response = self._call_google_ai(prompt)
        if ai_response:
            result = self._extract_json_from_response(ai_response)
            if result:
                result["generation_method"] = "Google AI Studio"
                return result

        logger.warning("Google AI failed. Using fallback for interview questions.")
        return {
            "technical_questions": [{"question": "Describe your experience with key technologies in our job description.", "difficulty": "medium", "category": "technical"}],
            "behavioral_questions": [{"question": "Tell me about a challenging project you worked on.", "difficulty": "medium", "category": "behavioral"}],
            "situational_questions": [{"question": "How would you handle a tight deadline?", "difficulty": "medium", "category": "situational"}],
            "culture_questions": [{"question": "What kind of work environment do you thrive in?", "difficulty": "easy", "category": "culture"}],
            "preparation_tips": ["Research the company's mission and values.", "Prepare examples using the STAR method."],
            "generation_method": "Fallback Template"
        }

    def analyze_job_description(self, job_description: str) -> Dict[str, Any]:
        """Analyze job description using Google AI"""

        prompt = f"""
        Analyze the following job description and extract key information.
        Job Description: {job_description}

        Provide analysis in a JSON object enclosed in ```json ... ```:
        {{
            "required_skills": ["skill1", "skill2"], "preferred_skills": ["skill3", "skill4"],
            "experience_level": "entry/junior/mid/senior/executive", "education_requirements": "requirement",
            "key_responsibilities": ["responsibility1", "responsibility2"],
            "keywords_for_resume": ["keyword1", "keyword2"]
        }}
        """

        ai_response = self._call_google_ai(prompt, max_tokens=1500)
        if ai_response:
            result = self._extract_json_from_response(ai_response)
            if result:
                result["analysis_method"] = "Google AI Studio"
                return result

        logger.warning("Google AI failed. Using fallback for job description analysis.")
        skills = list(set([skill for skill in ["python", "javascript", "react", "sql", "aws"] if skill in job_description.lower()]))
        return {
            "required_skills": skills, "preferred_skills": ["teamwork", "communication"],
            "experience_level": "mid", "education_requirements": "Bachelor's degree preferred",
            "key_responsibilities": ["Develop and maintain web applications.", "Collaborate with teams."],
            "keywords_for_resume": skills, "analysis_method": "Simple Fallback"
        }

# Global AI service instance
ai_service = AIService()
