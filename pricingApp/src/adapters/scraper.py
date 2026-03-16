import requests
from bs4 import BeautifulSoup
from typing import Dict


class Scraper:
    """
    A simple scraper for Pokémon offers from local HTML pages or URLs.
    Implements `fetch_and_scrape(url)` for compatibility with PricingService.
    """

    def __init__(self):
        pass

    @staticmethod
    def parse_price(text: str) -> float:
        """
        Convert price string like "€95" to float 95.0
        Handles various encoding issues with Euro symbol
        """
        text = text.replace("€", "").replace("â\x82¬", "").strip()
        return float(text)

    async def fetch_and_scrape(self, url: str) -> Dict:
        """
        Fetch the page and return the cheapest offer in the following format:
        {
            "pokemon": "Charmander",
            "seller": "Hannes",
            "price": 90.0,
            "source": url
        }
        """
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
            price = self.parse_price(offer.select_one(".price").text)

            if cheapest is None or price < cheapest["price"]:
                cheapest = {
                    "pokemon": pokemon_name,
                    "seller": trainer,
                    "price": price,
                    "source": url
                }

        return cheapest

    async def close(self):
        """
        Placeholder for async interface. Nothing to close for requests/BS4.
        """
        pass