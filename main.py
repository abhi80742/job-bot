import yaml
import schedule
import time
from dotenv import load_dotenv

from scraper.linkedin_scraper import scrape_linkedin
from parser.jd_parser import fetch_jd_text, parse_jd
from parser.scorer import score_job
from resume.tailor import tailor_resume, generate_cover_letter
from resume.pdf_generator import generate_pdf
from submitter.form_filler import submit_application          # ← NEW
from tracker.db import (init_db, is_duplicate,
                        log_application, get_all_applications)

load_dotenv()

with open("config.yaml") as f:
    cfg = yaml.safe_load(f)


def human_review(jd: dict, score: dict) -> bool:
    print(f"\n{'='*58}")
    print(f"  Role    : {jd.get('role_title')} @ {jd.get('company')}")
    print(f"  Location: {jd.get('location')}  |  Remote: {jd.get('remote')}")
    print(f"  Score   : {score['score']}%  |  Exp OK: {score['exp_ok']}")
    print(f"  Matched : {', '.join(score['matched']) or 'none'}")
    print(f"  Missing : {', '.join(score['missing']) or 'none'}")
    print(f"  Summary : {jd.get('summary', 'N/A')}")
    print(f"{'='*58}")
    ans = input("  Apply to this job? (y/n): ").strip().lower()
    return ans == "y"


def show_dashboard(conn):
    rows = get_all_applications(conn)
    if not rows:
        print("\n  No applications tracked yet.\n")
        return
    print(f"\n{'─'*65}")
    print(f"  {'Company':<22} {'Role':<22} {'Score':>5}  Status")
    print(f"{'─'*65}")
    for r in rows:
        print(f"  {str(r[0]):<22} {str(r[1]):<22} {r[2]:>4}%  {r[3]}")
    print(f"{'─'*65}\n")


def run_pipeline():
    print("\n" + "="*58)
    print("  Job Bot  |  Karne Abhishek  |  Hyderabad")
    print("="*58)

    conn = init_db()
    from scraper.naukri_scraper import scrape_naukri

    print("\n  Checking LinkedIn...")
    linkedin_jobs = scrape_linkedin(
        cfg["job_search"]["keywords"],
        cfg["job_search"]["location"]
    )

    print("\n  Checking Naukri...")
    naukri_jobs = scrape_naukri(
        cfg["job_search"]["keywords"],
        cfg["job_search"]["location"]
    )

    jobs = linkedin_jobs + naukri_jobs
    print(f"\n  Total: LinkedIn={len(linkedin_jobs)} | Naukri={len(naukri_jobs)}")

    for job in jobs:
        print(f"\n  Checking: {job['title']} @ {job['company']}")

        if is_duplicate(conn, job["url"]):
            print("  Already seen — skipping")
            continue

        raw_text  = fetch_jd_text(job["url"])
        parsed_jd = parse_jd(raw_text)
        if not parsed_jd:
            print("  Could not parse — skipping")
            continue

        result = score_job(
            parsed_jd, cfg["skills"], cfg["experience_years"]
        )
        print(f"  Match: {result['score']}%")

        if not result["should_apply"]:
            print("  Below threshold — skipping")
            continue

        if not human_review(parsed_jd, result):
            print("  Skipped by you")
            continue

        # ── Resume tailoring & PDF ────────────────────────────────────────
        print("  Tailoring resume with AI...")
        tailored_cv  = tailor_resume(parsed_jd)
        cover_letter = generate_cover_letter(parsed_jd)
        pdf_path     = generate_pdf(
            tailored_cv, cover_letter,
            parsed_jd.get("company", job["company"]),
            parsed_jd.get("role_title", job["title"])
        )
        print(f"  PDF saved: {pdf_path}")

        # ── Auto-fill & human-review gate ─────────────────────────────────
        print("  Launching browser to fill application form...")
        result_sub = submit_application(
            url      = job["url"],
            pdf_path = pdf_path,
            jd       = parsed_jd,
            cfg      = cfg,
        )
        sub_status = result_sub.get("status", "unknown")
        print(f"  Submission status: {sub_status}")

        # ── Log to DB ─────────────────────────────────────────────────────
        log_application(
            conn,
            parsed_jd.get("company", job["company"]),
            parsed_jd.get("role_title", job["title"]),
            job["url"],
            result["score"],
            pdf_path,
        )
        print(f"  Done — PDF: {pdf_path}  |  Status: {sub_status}")

    show_dashboard(conn)
    conn.close()


if __name__ == "__main__":
    run_pipeline()
    schedule.every(cfg["schedule_hours"]).hours.do(run_pipeline)
    while True:
        schedule.run_pending()
        time.sleep(60)