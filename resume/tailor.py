import google.generativeai as genai
import os
import time
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")  

def load_master_resume() -> str:
    with open("resume/master_resume.txt", "r", encoding="utf-8") as f:
        return f.read()

def tailor_resume(parsed_jd: dict) -> str:
    master = load_master_resume()
    prompt = f"""You are a professional resume writer helping Karne Abhishek
get a job as {parsed_jd.get('role_title')} at {parsed_jd.get('company')}.

Rewrite the resume below:
- Highlight these required skills: {parsed_jd.get('required_skills', [])}
- Mirror the language and keywords from the job description
- Keep all facts 100% truthful, only rephrase and reorder existing content
- Output clean plain text only. No markdown. No asterisks.

Master Resume:
{master}"""

    try:
        time.sleep(4)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"  Tailor error: {e}")
        return master

def generate_cover_letter(parsed_jd: dict) -> str:
    prompt = f"""Write a professional cover letter for Karne Abhishek applying for:
Role: {parsed_jd.get('role_title')} at {parsed_jd.get('company')}
Required skills: {parsed_jd.get('required_skills', [])}

Background:
- Full Stack Developer with Python and JavaScript experience
- Currently Associate Software Engineer at Crestonix Global Solution
- BSc Computer Science, Osmania University (75%, June 2024)
- Certifications in Full Stack Web Dev and Python Programming

Rules:
- Under 200 words. Professional and confident tone.
- Do NOT start with "I am excited to apply" or similar filler phrases."""

    try:
        time.sleep(4)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"  Cover letter error: {e}")
        return ""