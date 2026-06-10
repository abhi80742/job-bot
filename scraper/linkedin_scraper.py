import requests
from bs4 import BeautifulSoup

def scrape_linkedin(keywords: str, location: str) -> list:
    results = []
    try:
        # LinkedIn public RSS feed — no login needed
        url = (
            f"https://www.linkedin.com/jobs/search/?keywords="
            f"{keywords.replace(' ', '%20')}"
            f"&location={location.replace(' ', '%20')}"
            f"&f_TPR=r86400&position=1&pageNum=0"
        )
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        cards = soup.find_all("div", class_="base-card")
        print(f"  Found {len(cards)} LinkedIn jobs")

        for card in cards[:15]:
            try:
                title   = card.find("h3", class_="base-search-card__title")
                company = card.find("h4", class_="base-search-card__subtitle")
                link    = card.find("a", class_="base-card__full-link")
                if title and company and link:
                    results.append({
                        "title":   title.get_text(strip=True),
                        "company": company.get_text(strip=True),
                        "url":     link.get("href", "").split("?")[0],
                        "source":  "linkedin"
                    })
            except Exception as e:
                continue

    except Exception as e:
        print(f"  LinkedIn error: {e}")

    return results