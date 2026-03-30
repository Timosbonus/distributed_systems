#!/usr/bin/env python3
import random
import re
import time
from pathlib import Path

SAMPLE_SHOP_DIR = Path(__file__).parent
HTML_FILES = list(SAMPLE_SHOP_DIR.glob("*.html"))

def random_price(min_val=50, max_val=200):
    return random.randint(min_val, max_val)

def update_prices():
    for html_file in HTML_FILES:
        content = html_file.read_text(encoding="utf-8")
        
        def replace_price(match):
            old_price = match.group(1)
            new_price = random_price()
            return f'€{new_price}'
        
        new_content = re.sub(r'€(\d+)', replace_price, content)
        
        html_file.write_text(new_content, encoding="utf-8")
        print(f"Updated prices in {html_file.name}")

def main():
    print("Price Randomizer started...")
    print(f"Watching {len(HTML_FILES)} HTML files")
    print("Press Ctrl+C to stop")
    
    while True:
        update_prices()
        time.sleep(30)

if __name__ == "__main__":
    main()
