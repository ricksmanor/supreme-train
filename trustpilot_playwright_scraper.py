import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import datetime
import traceback
import sys

DOMAIN = "ukstoragecompany.co.uk"
BASE_URL = f"https://uk.trustpilot.com/review/{DOMAIN}"
PAGES_TO_SCRAPE = 3  # Adjust number of pages to scrape

async def scrape():
    try:
        reviews = []

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            for page_num in range(1, PAGES_TO_SCRAPE + 1):
                url = f"{BASE_URL}?page={page_num}"
                print(f"Scraping: {url}")
                await page.goto(url)
                await page.wait_for_selector("article.review")

                review_elements = await page.query_selector_all("article.review")

                for r in review_elements:
                    title = await r.query_selector_eval("h2", "el => el.textContent.trim()") or ""
                    body = await r.query_selector_eval("p.review-content__text", "el => el.textContent.trim()") or ""
                    rating = await r.query_selector_eval("div.star-rating img", "el => el.alt") or ""
                    date = await r.query_selector_eval("time", "el => el.getAttribute('datetime')") or ""

                    reviews.append({
                        "Title": title,
                        "Body": body,
                        "Rating": rating,
                        "Date": date,
                    })

            await browser.close()

        df = pd.DataFrame(reviews)
        filename = f"trustpilot_reviews_{datetime.date.today()}.xlsx"
        df.to_excel(filename, index=False)
        print(f"Saved {filename}")

    except Exception:
        print("Error during scraping:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(scrape())
