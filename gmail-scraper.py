import aiohttp
import asyncio
import re
from bs4 import BeautifulSoup

# List of user agents for scraping
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'
]

async def fetch_emails_from_page(session, url, user_agent):
    headers = {'User-Agent': user_agent}
    try:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text()
            emails = set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}', text))
            return emails
    except aiohttp.ClientError as e:
        print(f"Error fetching {url}: {e}")
        return set()

async def scrape_emails(base_url):
    all_emails = set()
    max_pages = 50  # Change to scrape 50 pages
    semaphore = asyncio.Semaphore(10)

    async def fetch_page(page):
        url = f"{base_url}&first={page}"
        user_agent = USER_AGENTS[page % len(USER_AGENTS)]
        async with semaphore:
            emails = await fetch_emails_from_page(session, url, user_agent)
            if emails:
                all_emails.update(emails)
                print(f"Scraped page {page + 1}: Found {len(emails)} emails")
            else:
                print(f"Page {page + 1}: No emails found")
            await asyncio.sleep(0.1)

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_page(page) for page in range(max_pages)]
        await asyncio.gather(*tasks)

    return all_emails

def run_scraper(url):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    emails = loop.run_until_complete(scrape_emails(url))
    loop.close()
    return sorted(emails)

def main():
    url = input("Enter the base URL: ")
    if not url:
        print("Input Error: Please enter a URL.")
        return

    print("Scraping in progress...")
    emails = run_scraper(url)
    print("Scraping complete.")
    if emails:
        print("\nScraped Emails:\n" + "\n".join(emails))
    else:
        print("No emails found.")

if __name__ == "__main__":
    main()
