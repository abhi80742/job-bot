import requests
from bs4 import BeautifulSoup

def scrape_naukri(keywords: str, location: str) -> list:
    results = []
    try:
        keyword_url  = keywords.replace(" ", "-").lower()
        location_url = location.replace(" ", "-").lower()
        url = f"https://www.naukri.com/{keyword_url}-jobs-in-{location_url}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        cards = soup.find_all("article", class_="jobTuple")
        if not cards:
            cards = soup.find_all("div", class_="srp-jobtuple-wrapper")
        print(f"  Found {len(cards)} Naukri jobs")

        for card in cards[:15]:
            try:
                title   = card.find("a", class_="title")
                company = card.find("a", class_="subTitle")
                if not company:
                    company = card.find("span", class_="comp-name")
                if title:
                    results.append({
                        "title":   title.get_text(strip=True),
                        "company": company.get_text(strip=True) if company else "Unknown",
                        "url":     title.get("href", ""),
                        "source":  "naukri"
                    })
            except Exception as e:
                continue

    except Exception as e:
        print(f"  Naukri error: {e}")

    return results