import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import datetime
import traceback
import sys
import time

DOMAIN = "ukstoragecompany.co.uk"
BASE_URL = f"https://uk.trustpilot.com/review/{DOMAIN}"
PAGES_TO_SCRAPE = 2  # for testing

async def scrape():
    try:
        reviews = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            for page_num in range(1, PAGES_TO_SCRAPE + 1):
                url = f"{BASE_URL}?page={page_num}"
                print(f"Scraping: {url}")

                await page.goto(url, wait_until="networkidle")
                await page.screenshot(path=f"screenshot_page{page_num}.png")

                try:
                    await page.wait_for_selector("section[data-service-review-list]", timeout=60000)
                except Exception:
                    print(f"No review container found on page {page_num}, skipping...")
                    continue

                review_elements = await page.query_selector_all("article.review")

                for r in review_elements:
                    title = await r.query_selector_eval("h2", "el => el.textContent.trim()") if await r.query_selector("h2") else ""
                    body = await r.query_selector_eval("p.review-content__text", "el => el.textContent.trim()") if await r.query_selector("p.review-content__text") else ""
                    rating = await r.query_selector_eval("div.star-rating img", "el => el.alt") if await r.query_selector("div.star-rating img") else ""
                    date = await r.query_selector_eval("time", "el => el.getAttribute('datetime')") if await r.query_selector("time") else ""

                    reviews.append({
                        "Title": title,
                        "Body": body,
                        "Rating": rating,
                        "Date": date,
                    })

                time.sleep(5)  # 5 seconds delay per page

            await browser.close()

        df = pd.DataFrame(reviews)
        filename = f"trustpilot_reviews_{datetime.date.today()}.csv"
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        print(f"Saved {filename}")

    except Exception:
        print("Error during scraping:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(scrape())
