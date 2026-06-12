# 🤖 Job Bot — AI-Powered Job Application Automation

> Scrapes LinkedIn & Naukri, scores job matches with AI, tailors your resume, and tracks every application — fully automated.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![Gemini](https://img.shields.io/badge/Google_Gemini-2.0_Flash-orange?logo=google&logoColor=white)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey?logo=sqlite)
![BeautifulSoup](https://img.shields.io/badge/Scraper-BeautifulSoup4-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🎯 What It Does

Most job seekers manually copy-paste resumes, write cover letters from scratch, and lose track of where they applied. Job Bot automates all of that.

**One command. Fully automated pipeline:**

```
Scrape Jobs → Parse JD with AI → Score Match → Tailor Resume → Generate Cover Letter → Track in DB
```

---

## ✨ Features

- 🔍 **Multi-platform scraping** — LinkedIn + Naukri simultaneously
- 🧠 **AI-powered JD parsing** — extracts role, skills, experience, location using Gemini 2.0
- 📊 **Smart job scoring** — matches your skills against required skills, filters low matches
- 📝 **Resume tailoring** — rewrites your master resume for each specific job
- ✉️ **Cover letter generation** — personalized cover letter per job application
- 🗄️ **SQLite tracking** — never apply to the same job twice, full history
- ⏱️ **Rate-limit aware** — built-in delays to stay within Gemini free tier (15 RPM)

---

## 🏗️ Architecture

```
Job_Bot/
│
├── main.py                  ← Entry point, orchestrates the pipeline
│
├── scraper/
│   ├── linkedin_scraper.py  ← Scrapes LinkedIn job listings
│   └── naukri_scraper.py    ← Scrapes Naukri job listings
│
├── parser/
│   ├── jd_parser.py         ← Gemini AI: extracts structured data from JD
│   └── scorer.py            ← Scores job match % against your skills
│
├── resume/
│   ├── tailor.py            ← Gemini AI: tailors resume per job
│   ├── pdf_generator.py     ← Generates PDF resume output
│   └── master_resume.txt    ← Your base resume (plain text)
│
├── submitter/
│   └── form_filler.py       ← Auto form filling (WIP)
│
├── db.py                    ← SQLite: tracks all applications
├── config.yaml              ← Job search config (role, location, skills)
└── outputs/                 ← Generated resumes + cover letters
```

---

## ⚙️ How It Works — Step by Step

**1. Scrape** — Bot searches LinkedIn and Naukri for your target role and collects job listings.

**2. Parse** — For each job, Gemini 2.0 Flash reads the job description and extracts structured JSON: role title, company, required skills, experience years, location.

**3. Score** — Your skills are compared against required skills. Only jobs with 60%+ match proceed. This saves API quota and focuses on quality applications.

**4. Tailor** — For matched jobs, Gemini rewrites your master resume to highlight relevant skills and mirror the JD's language — 100% truthful, just reordered.

**5. Cover Letter** — A personalized cover letter is generated mentioning the specific role, company, and your matching skills.

**6. Track** — Everything is saved to SQLite: job title, company, match score, status, timestamp.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- Google Gemini API key (free at [aistudio.google.com](https://aistudio.google.com))

### Installation

```bash
# Clone the repo
git clone https://github.com/abhi80742/Job_Bot.git
cd Job_Bot

# Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Configuration

Edit `config.yaml` to set your job preferences:

```yaml
role: "Full Stack Developer"
location: "Hyderabad"
skills:
  - Python
  - React
  - Node.js
  - SQL
experience_years: 1
```

Update `resume/master_resume.txt` with your resume in plain text.

### Run

```bash
python main.py
```

---

## 📋 Requirements

```
google-generativeai
beautifulsoup4
requests
python-dotenv
sqlite3
reportlab
pyyaml
```

Install all: `pip install -r requirements.txt`

---

## 🔐 Environment Variables

Create a `.env` file (never commit this):

```
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## 📌 Current Limitations

- LinkedIn scraping works on public job listings only (no login required)
- Gemini free tier: 15 requests/minute — bot handles this with built-in delays
- Auto form submission (`form_filler.py`) is still in development
- Naukri scraper may need cookie refresh periodically

---

## 🛣️ Roadmap

- [ ] Streamlit dashboard to view tracked applications
- [ ] Email alerts for high-match jobs (80%+)
- [ ] Indeed + Internshala scraper
- [ ] Auto form submission via Selenium
- [ ] Resume PDF auto-attachment

---

## 👨‍💻 Author

**Karne Abhishek (Sunny)**
Associate Software Engineer | Full Stack Developer
📍 Hyderabad, Telangana

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://linkedin.com/in/your-profile)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?logo=github)](https://github.com/abhi80742)

---

## 📄 License

MIT License — feel free to use, modify, and share.