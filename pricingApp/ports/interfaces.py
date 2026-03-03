from abc import ABC, abstractmethod
from typing import Protocol


class PricePort(Protocol):
    def scrape_price(self, url: str) -> float | None:
        ...


class DatabasePort(Protocol):
    def get_session(self):
        ...

    def create_all(self):
        ...
