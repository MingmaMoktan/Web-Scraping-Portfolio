import asyncio
import requests
from crawl4ai import AsyncWebCrawler

# 1. PASTE YOUR WEBHOOK URL HERE
# Use the IP address 172.30.164.146 if localhost doesn't work
WEBHOOK_URL = "http://172.30.164.146:8080/api/v1/webhooks/YOUR_UNIQUE_ID"

async def main():
    print("🚀 Starting the crawler...")
    
    # 2. Initialize the crawler
    async with AsyncWebCrawler(verbose=True) as crawler:
        # We'll scrape a specific site as a test
        url = "https://www.nbcnews.com/business"
        result = await crawler.arun(url=url)
        
        if result.success:
            print(f"✅ Successfully scraped: {url}")
            
            # 3. Prepare the data for Activepieces
            # We send a 'payload' (a dictionary) which Activepieces converts to JSON
            payload = {
                "source": "My WSL Scraper",
                "title": "NBC Business News",
                "url": url,
                "content": result.markdown[:2000]  # Sending the first 2000 chars of clean text
            }
            
            # 4. Send the data to your Activepieces Trigger
            try:
                response = requests.post(WEBHOOK_URL, json=payload)
                if response.status_code == 200:
                    print("💎 Data successfully sent to Activepieces!")
                else:
                    print(f"⚠️ Sent, but got status code: {response.status_code}")
            except Exception as e:
                print(f"❌ Failed to connect to Webhook: {e}")
                
        else:
            print(f"❌ Scrape failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(main())