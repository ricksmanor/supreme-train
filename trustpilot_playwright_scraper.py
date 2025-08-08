# trustpilot_scraper.py
import asyncio
import csv
import time
from playwright.async_api import async_playwright

URL = "https://uk.trustpilot.com/review/ukstoragecompany.co.uk"
PAGES_TO_SCRAPE = 2  # For testing
DELAY_SECONDS = 5    # Wait between pages

async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Prepare CSV
        with open("reviews.csv", mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Name", "Country", "Reviews Count", "Review Date", 
                "Rating", "Title", "Text", "Date of Experience"
            ])

            for page_num in range(1, PAGES_TO_SCRAPE + 1):
                url = f"{URL}?page={page_num}"
                print(f"Scraping: {url}")
                await page.goto(url, timeout=60000)
                await page.wait_for_selector("article.review", timeout=60000)
                time.sleep(DELAY_SECONDS)  # Give time for all content to load

                reviews = await page.query_selector_all("article.review")

                for r in reviews:
                    name = await r.query_selector_eval("span.typography_heading-xxs__QKBS8", "el => el.innerText") if await r.query_selector("span.typography_heading-xxs__QKBS8") else ""
                    country = await r.query_selector_eval("div.typography_body-m__xgxZ_.styles_consumerDetails__dlqRH > span", "el => el.innerText") if await r.query_selector("div.typography_body-m__xgxZ_.styles_consumerDetails__dlqRH > span") else ""
                    review_count = await r.query_selector_eval("div.typography_body-m__xgxZ_.styles_consumerDetails__dlqRH > a", "el => el.innerText") if await r.query_selector("div.typography_body-m__xgxZ_.styles_consumerDetails__dlqRH > a") else ""
                    review_date = await r.query_selector_eval("time.typography_body-m__xgxZ_.styles_dates__3_M8n", "el => el.innerText") if await r.query_selector("time.typography_body-m__xgxZ_.styles_dates__3_M8n") else ""
                    rating = await r.get_attribute("data-service-review-rating") or ""
                    title = await r.query_selector_eval("h2.typography_heading-s__f7029", "el => el.innerText") if await r.query_selector("h2.typography_heading-s__f7029") else ""
                    text = await r.query_selector_eval("p.typography_body-l__KUYFJ", "el => el.innerText") if await r.query_selector("p.typography_body-l__KUYFJ") else ""
                    date_experience = await r.query_selector_eval("p.typography_body-m__xgxZ_", "el => el.innerText") if await r.query_selector("p.typography_body-m__xgxZ_") else ""

                    writer.writerow([
                        name, country, review_count, review_date,
                        rating, title, text, date_experience
                    ])

                await page.screenshot(path=f"screenshot_page{page_num}.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape())
