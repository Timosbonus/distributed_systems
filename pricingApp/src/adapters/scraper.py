from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re


class Scraper:
    def __init__(self):
        pass

    def scrape_price(self, url: str) -> float | None:
        pass

    def scrape_offers(self, html_content: str) -> List[Dict[str, any]]:
        """
        Parse idealo HTML and extract all offers with prices and sellers.
        Returns list of dicts with 'price' and 'seller' keys.
        """
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

    def find_cheapest_offer(self, html_content: str) -> Dict[str, any] | None:
        """
        Find the cheapest offer from the HTML.
        Returns dict with 'price' and 'seller' keys.
        """
        offers = self.scrape_offers(html_content)
        if not offers:
            return None
        
        cheapest = min(offers, key=lambda x: x['price'])
        return cheapest
