import asyncio
import csv
import time
from playwright.async_api import async_playwright

OUTPUT_FILE = "trustpilot_reviews.csv"
URL_TEMPLATE = "https://uk.trustpilot.com/review/ukstoragecompany.co.uk?page={}"

async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Set a real browser user agent
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
        })

        all_reviews = []

        for page_number in range(1, 3):  # Adjust number of pages here
            url = URL_TEMPLATE.format(page_number)
            print(f"Scraping: {url}")
            await page.goto(url, timeout=60000)

            try:
                # Wait for container instead of just article.review
                await page.wait_for_selector("section.styles_reviewsContainer__1QdOY", timeout=60000)
            except Exception:
                print(f"No reviews found on page {page_number} — possible block or selector change")
                continue

            reviews = await page.query_selector_all("article")
            print(f"Found {len(reviews)} reviews on page {page_number}")

            for review in reviews:
                name = await review.query_selector_eval("span.consumer-information__name", "el => el.textContent") if await review.query_selector("span.consumer-information__name") else ""
                location = await review.query_selector_eval("span.consumer-information__location", "el => el.textContent") if await review.query_selector("span.consumer-information__location") else ""
                date = await review.query_selector_eval("time", "el => el.textContent") if await review.query_selector("time") else ""
                rating = await review.query_selector_eval("div.star-rating", "el => el.getAttribute('data-service-review-rating')") if await review.query_selector("div.star-rating") else ""
                title = await review.query_selector_eval("h2", "el => el.textContent") if await review.query_selector("h2") else ""
                body = await review.query_selector_eval("p", "el => el.textContent") if await review.query_selector("p") else ""

                all_reviews.append([name.strip(), location.strip(), date.strip(), rating.strip(), title.strip(), body.strip()])

            time.sleep(5)  # Delay between pages

        # Save to CSV
        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Location", "Date", "Rating", "Title", "Body"])
            writer.writerows(all_reviews)

        print(f"Saved {len(all_reviews)} reviews to {OUTPUT_FILE}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape())
