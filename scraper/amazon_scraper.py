import requests
from bs4 import BeautifulSoup
import re
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
from urllib.parse import urlparse, parse_qs

class AmazonScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'),
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def extract_asin_from_url(self, url):
        """Extract ASIN from Amazon URL"""
        # Method 1: Check URL path for /dp/ pattern
        match = re.search(r'/dp/([A-Z0-9]{10})', url)
        if match:
            return match.group(1)
        
        # Method 2: Check URL path for /gp/product/ pattern
        match = re.search(r'/gp/product/([A-Z0-9]{10})', url)
        if match:
            return match.group(1)
        
        # Method 3: Check query parameters
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        if 'asin' in query_params:
            return query_params['asin'][0]
        
        return None
    
    def scrape_with_requests(self, url):
        """Scrape using requests and BeautifulSoup (faster but may be blocked)"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract product info
            product_info = self._extract_product_info(soup)
            
            # Add random delay to avoid detection
            time.sleep(random.uniform(1, 3))
            
            return product_info
            
        except Exception as e:
            print(f"Request scraping failed: {e}")
            return None
    
    def scrape_with_selenium(self, url):
        """Scrape using Selenium (slower but more reliable)"""
        driver = None
        try:
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument(f'--user-agent={self.headers["User-Agent"]}')
            
            # Setup driver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Load page
            driver.get(url)
            
            # Wait for price element to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Get page source and parse
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            product_info = self._extract_product_info(soup)
            
            return product_info
            
        except Exception as e:
            print(f"Selenium scraping failed: {e}")
            return None
        finally:
            if driver:
                driver.quit()
    
    def scrape_product(self, url):
        """Main scraping method - tries requests first, then Selenium"""
        # Try requests first (faster)
        result = self.scrape_with_requests(url)
        
        # If requests fails, try Selenium
        if not result or not result.get('price'):
            print("Falling back to Selenium...")
            result = self.scrape_with_selenium(url)
        
        return result
    
    def _extract_product_info(self, soup):
        """Extract product information from BeautifulSoup object"""
        product_info = {
            'name': None,
            'price': None,
            'image_url': None,
            'availability': None
        }
        
        # Extract product name
        name_selectors = [
            '#productTitle',
            '.product-title',
            'h1.a-size-large',
            'h1'
        ]
        
        for selector in name_selectors:
            element = soup.select_one(selector)
            if element:
                product_info['name'] = element.get_text(strip=True)
                break
        
        # Extract price
        price_selectors = [
            '.a-price-whole',
            '.a-offscreen',
            '.a-price .a-offscreen',
            '#priceblock_dealprice',
            '#priceblock_ourprice',
            '#tp_price_block_total_price_ww',
            '.a-price-range .a-offscreen'
        ]
        
        for selector in price_selectors:
            elements = soup.select(selector)
            for element in elements:
                price_text = element.get_text(strip=True)
                price = self._parse_price(price_text)
                if price:
                    product_info['price'] = price
                    break
            if product_info['price']:
                break
        
        # Extract main product image
        image_selectors = [
            '#landingImage',
            '.a-dynamic-image',
            '#imgBlkFront',
            '.item-image-canvas img'
        ]
        
        for selector in image_selectors:
            element = soup.select_one(selector)
            if element:
                image_url = element.get('src') or element.get('data-src')
                if image_url:
                    product_info['image_url'] = image_url
                    break
        
        # Extract availability
        availability_selectors = [
            '#availability span',
            '.a-color-success',
            '.a-color-price'
        ]
        
        for selector in availability_selectors:
            element = soup.select_one(selector)
            if element:
                availability_text = element.get_text(strip=True).lower()
                if any(word in availability_text for word in ['in stock', 'available', 'ships']):
                    product_info['availability'] = 'In Stock'
                elif any(word in availability_text for word in ['out of stock', 'unavailable']):
                    product_info['availability'] = 'Out of Stock'
                break
        
        return product_info
    
    def _parse_price(self, price_text):
        """Parse price from text string"""
        if not price_text:
            return None
        
        # Remove currency symbols and extract numbers
        price_text = re.sub(r'[^\d.,]', '', price_text)
        
        # Handle different decimal separators
        if ',' in price_text and '.' in price_text:
            # Assume comma is thousand separator
            price_text = price_text.replace(',', '')
        elif ',' in price_text:
            # Could be decimal separator (European format)
            if price_text.count(',') == 1 and len(price_text.split(',')[1]) <= 2:
                price_text = price_text.replace(',', '.')
            else:
                price_text = price_text.replace(',', '')
        
        try:
            return float(price_text)
        except ValueError:
            return None
