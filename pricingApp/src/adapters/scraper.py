from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re
import asyncio
from playwright.async_api import async_playwright


class Scraper:
    def __init__(self):
        self.playwright = None
        self.browser = None

    async def _get_browser(self):
        if self.browser is None:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)
        return self.browser

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def fetch_page(self, url: str) -> Optional[str]:
        """Fetch HTML content using Playwright browser."""
        try:
            browser = await self._get_browser()
            page = await browser.new_page()
            
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Wait a bit for dynamic content
            await page.wait_for_timeout(2000)
            
            content = await page.content()
            await page.close()
            
            return content
        except Exception as e:
            print(f"Error fetching {url} with Playwright: {e}")
            return None

    def fetch_page_sync(self, url: str) -> Optional[str]:
        """Synchronous wrapper for fetch_page."""
        try:
            return asyncio.run(self.fetch_page(url))
        except Exception as e:
            print(f"Error in fetch_page_sync: {e}")
            return None

    async def scrape_price_async(self, url: str) -> Optional[float]:
        """Scrape price using Playwright."""
        html_content = await self.fetch_page(url)
        if not html_content:
            return None
        
        cheapest = await self.find_cheapest_offer_async(html_content)
        return cheapest['price'] if cheapest else None

    def scrape_price(self, url: str) -> Optional[float]:
        """Synchronous wrapper for scrape_price_async."""
        try:
            return asyncio.run(self.scrape_price_async(url))
        except Exception as e:
            print(f"Error in scrape_price: {e}")
            return None

    async def scrape_offers_async(self, html_content: str) -> List[Dict[str, any]]:
        """Parse idealo HTML and extract all offers with prices and sellers."""
        soup = BeautifulSoup(html_content, 'html.parser')
        offers = []

        offer_items = soup.find_all('li', class_='productOffers-listItem')

        for item in offer_items:
            try:
                price_elem = item.find('a', class_='productOffers-listItemOfferPrice')
                if not price_elem:
                    continue
                
                price_text = price_elem.get_text(strip=True)
                price_match = re.search(r'[\d.,]+', price_text.replace(',', '.'))
                if not price_match:
                    continue
                
                price = float(price_match.group().replace(',', ''))
                
                shop_elem = item.find('a', class_='productOffers-listItemOfferShopV2LogoLink')
                seller = None
                if shop_elem:
                    seller = shop_elem.get('data-shop-name', None)
                    if seller:
                        seller = seller.replace(' - Shop aus München', '').replace(' - Shop aus Berlin', '').strip()
                
                if not seller:
                    shop_name_elem = item.find('div', class_='productOffers-listItemOfferShopV2MarketPlaceMerchantName')
                    if shop_name_elem:
                        seller = shop_name_elem.get_text(strip=True)
                
                if seller and price:
                    offers.append({
                        'price': price,
                        'seller': seller
                    })
            except Exception as e:
                continue

        return offers

    def scrape_offers(self, html_content: str) -> List[Dict[str, any]]:
        """Synchronous wrapper."""
        return asyncio.run(self.scrape_offers_async(html_content))

    async def find_cheapest_offer_async(self, html_content: str) -> Optional[Dict[str, any]]:
        """Find the cheapest offer from the HTML."""
        offers = await self.scrape_offers_async(html_content)
        if not offers:
            return None
        
        cheapest = min(offers, key=lambda x: x['price'])
        return cheapest

    def find_cheapest_offer(self, html_content: str) -> Optional[Dict[str, any]]:
        """Synchronous wrapper."""
        return asyncio.run(self.find_cheapest_offer_async(html_content))

    async def fetch_and_scrape(self, url: str) -> Optional[Dict[str, any]]:
        """Fetch URL and return cheapest offer."""
        html_content = await self.fetch_page(url)
        if not html_content:
            return None
        return await self.find_cheapest_offer_async(html_content)

    def fetch_and_scrape_sync(self, url: str) -> Optional[Dict[str, any]]:
        """Synchronous wrapper."""
        return asyncio.run(self.fetch_and_scrape(url))
