import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, List


class Scraper:
    def parse_price(self, text: str) -> float:
        text = text.replace("€", "").replace("â\x82¬", "").strip()
        return float(text)

    async def fetch_and_scrape(self, url: str, excluded_sellers: List[str] = None) -> Optional[Dict]:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        pokemon_container = soup.select_one(".pokemon")
        if not pokemon_container:
            return None

        pokemon_name = pokemon_container.select_one("h2").text.strip()

        cheapest = None

        for offer in pokemon_container.select(".offer"):
            trainer = offer.select_one(".trainer").text.strip()
            
            if excluded_sellers and trainer in excluded_sellers:
                continue
                
            price = self.parse_price(offer.select_one(".price").text)

            if cheapest is None or price < cheapest["price"]:
                cheapest = {
                    "pokemon": pokemon_name,
                    "seller": trainer,
                    "price": price,
                    "source": url
                }

        return cheapest