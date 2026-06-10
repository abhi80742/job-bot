import google.generativeai as genai
import json
import os
import time
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash") 

def fetch_jd_text(url: str) -> str:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:4000]
    except Exception as e:
        print(f"  Could not fetch page: {e}")
        return ""

def parse_jd(raw_text: str) -> dict:
    if not raw_text.strip():
        return {}

    prompt = f"""Extract job info as JSON with these exact keys:
role_title, company, required_skills (list), preferred_skills (list),
experience_years (integer), location, remote (boolean),
summary (max 2 sentences)

Return ONLY valid JSON. No markdown. No explanation.

Job Description:
{raw_text}"""

    try:
        time.sleep(4)           # 4 sec gap = max 15 RPM, well within free tier (15 RPM limit)
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except Exception as e:
        print(f"  Parse error: {e}")
        return {}