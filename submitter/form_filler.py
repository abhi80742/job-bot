"""
form_filler.py  —  Playwright-based job application submitter
Supports: LinkedIn Easy Apply, Naukri Apply, Generic fallback
Mode: Fill form → pause → wait for your manual final click
"""

import os
import time
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PWTimeout


# ── helpers ──────────────────────────────────────────────────────────────────

def _profile_from_config(cfg: dict) -> dict:
    """Flatten config.yaml into a flat profile dict."""
    return {
        "name":     cfg.get("your_name", ""),
        "email":    cfg.get("your_email", ""),
        "phone":    cfg.get("your_phone", ""),
        "location": cfg.get("location", ""),
    }


def _detect_portal(url: str) -> str:
    url = url.lower()
    if "linkedin.com" in url:
        return "linkedin"
    if "naukri.com" in url:
        return "naukri"
    return "generic"


async def _safe_fill(page, selector: str, value: str, timeout: int = 4000):
    """Fill a field if it exists, silently skip if not found."""
    try:
        await page.wait_for_selector(selector, timeout=timeout)
        await page.fill(selector, value)
    except PWTimeout:
        pass


async def _safe_click(page, selector: str, timeout: int = 4000):
    try:
        await page.wait_for_selector(selector, timeout=timeout)
        await page.click(selector)
    except PWTimeout:
        pass


# ── LinkedIn Easy Apply ───────────────────────────────────────────────────────

async def _apply_linkedin(page, profile: dict, pdf_path: str, jd: dict):
    print("  [LinkedIn] Looking for Easy Apply button...")

    # Click Easy Apply
    try:
        await page.wait_for_selector(
            "button.jobs-apply-button, button[aria-label*='Easy Apply']",
            timeout=8000
        )
        await page.click(
            "button.jobs-apply-button, button[aria-label*='Easy Apply']"
        )
        await page.wait_for_timeout(2000)
    except PWTimeout:
        print("  [LinkedIn] Easy Apply button not found — may require manual apply")
        return False

    # Fill contact info in modal
    await _safe_fill(page, "input[id*='phoneNumber']", profile["phone"])
    await _safe_fill(page, "input[id*='city']", profile["location"])

    # Upload resume PDF if file input exists
    try:
        file_input = await page.query_selector("input[type='file']")
        if file_input and pdf_path and Path(pdf_path).exists():
            await file_input.set_input_files(pdf_path)
            print(f"  [LinkedIn] Resume uploaded: {pdf_path}")
            await page.wait_for_timeout(1500)
    except Exception as e:
        print(f"  [LinkedIn] Resume upload skipped: {e}")

    # Step through multi-page modal (Next buttons)
    for step in range(8):
        next_btn = await page.query_selector(
            "button[aria-label='Continue to next step'], "
            "button[aria-label='Review your application']"
        )
        if next_btn:
            await next_btn.click()
            await page.wait_for_timeout(1500)
        else:
            break

    print("  [LinkedIn] Form filled ✅ — Review modal open. Click 'Submit application' when ready.")
    return True


# ── Naukri Apply ─────────────────────────────────────────────────────────────

async def _apply_naukri(page, profile: dict, pdf_path: str, jd: dict):
    print("  [Naukri] Looking for Apply button...")

    try:
        await page.wait_for_selector(
            "button#apply-button, a.apply-button, button[class*='apply']",
            timeout=8000
        )
        await page.click(
            "button#apply-button, a.apply-button, button[class*='apply']"
        )
        await page.wait_for_timeout(2000)
    except PWTimeout:
        print("  [Naukri] Apply button not found")
        return False

    # Fill fields if a form appears
    await _safe_fill(page, "input[name='name'], input[placeholder*='Name']", profile["name"])
    await _safe_fill(page, "input[name='email'], input[type='email']", profile["email"])
    await _safe_fill(page, "input[name='mobile'], input[placeholder*='Mobile']", profile["phone"])

    # Upload resume
    try:
        file_input = await page.query_selector("input[type='file']")
        if file_input and pdf_path and Path(pdf_path).exists():
            await file_input.set_input_files(pdf_path)
            print(f"  [Naukri] Resume uploaded: {pdf_path}")
            await page.wait_for_timeout(1500)
    except Exception as e:
        print(f"  [Naukri] Resume upload skipped: {e}")

    print("  [Naukri] Form filled ✅ — Please review and click the final Submit button.")
    return True


# ── Generic Fallback ──────────────────────────────────────────────────────────

async def _apply_generic(page, profile: dict, pdf_path: str, jd: dict):
    print("  [Generic] Attempting generic form fill...")

    # Common name fields
    for sel in ["input[name='name']", "input[id*='name']", "input[placeholder*='Name']",
                "input[autocomplete='name']"]:
        await _safe_fill(page, sel, profile["name"])

    # Email
    for sel in ["input[type='email']", "input[name='email']", "input[id*='email']"]:
        await _safe_fill(page, sel, profile["email"])

    # Phone
    for sel in ["input[type='tel']", "input[name='phone']", "input[name='mobile']",
                "input[id*='phone']", "input[placeholder*='Phone']"]:
        await _safe_fill(page, sel, profile["phone"])

    # Location / City
    for sel in ["input[name='location']", "input[name='city']", "input[id*='location']",
                "input[placeholder*='Location']", "input[placeholder*='City']"]:
        await _safe_fill(page, sel, profile["location"])

    # Resume upload
    try:
        file_input = await page.query_selector("input[type='file']")
        if file_input and pdf_path and Path(pdf_path).exists():
            await file_input.set_input_files(pdf_path)
            print(f"  [Generic] Resume uploaded: {pdf_path}")
            await page.wait_for_timeout(1500)
    except Exception as e:
        print(f"  [Generic] Resume upload skipped: {e}")

    print("  [Generic] Form filled ✅ — Please review and click Submit when ready.")
    return True


# ── Main entry point ──────────────────────────────────────────────────────────

async def _run(url: str, pdf_path: str, jd: dict, cfg: dict):
    profile = _profile_from_config(cfg)
    portal  = _detect_portal(url)

    print(f"\n  Opening browser for: {portal.upper()} → {url}")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False, slow_mo=80)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            accept_downloads=True,
        )
        page = await context.new_page()

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(2000)
        except Exception as e:
            print(f"  Could not load page: {e}")
            await browser.close()
            return {"status": "error", "reason": str(e)}

        # Route to correct handler
        success = False
        if portal == "linkedin":
            success = await _apply_linkedin(page, profile, pdf_path, jd)
        elif portal == "naukri":
            success = await _apply_naukri(page, profile, pdf_path, jd)
        else:
            success = await _apply_generic(page, profile, pdf_path, jd)

        if not success:
            print("  Auto-fill could not complete. Browser left open for manual apply.")

        # ── HUMAN REVIEW GATE ─────────────────────────────────────────────
        print("\n" + "="*58)
        print("  BROWSER IS OPEN — review the filled form.")
        print("  Click the final SUBMIT button yourself when satisfied.")
        print("  Press ENTER here once you are done (submitted or skipped).")
        print("="*58)
        input("  >> Press ENTER to close browser: ")
        # ─────────────────────────────────────────────────────────────────

        await browser.close()

    return {"status": "submitted" if success else "manual", "url": url}


def submit_application(url: str, pdf_path: str, jd: dict, cfg: dict) -> dict:
    """
    Synchronous wrapper — call this from main.py.

    Args:
        url      : Job posting URL
        pdf_path : Path to the tailored resume PDF
        jd       : Parsed JD dict (from parse_jd)
        cfg      : Full config.yaml dict (needs your_name, email, phone, location)

    Returns:
        dict with 'status' key: 'submitted' | 'manual' | 'error'
    """
    return asyncio.run(_run(url, pdf_path, jd, cfg))