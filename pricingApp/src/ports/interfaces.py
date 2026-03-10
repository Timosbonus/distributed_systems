from abc import ABC, abstractmethod
from typing import Protocol, List, Dict


class PricePort(Protocol):
    def scrape_price(self, url: str) -> float | None:
        ...

    def scrape_offers(self, html_content: str) -> List[Dict[str, any]]:
        ...

    def find_cheapest_offer(self, html_content: str) -> Dict[str, any] | None:
        ...


class DatabasePort(Protocol):
    def get_session(self):
        ...

    def create_all(self):
        ...
