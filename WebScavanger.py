import os
import json
import time
import random
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from fake_useragent import UserAgent
from urllib.parse import urlparse, parse_qs
import re

logging.basicConfig(
    filename='webscavanger.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class WebScavanger:
    def __init__(self):
        self.results = {
            'pdf': [],
            'docx': [],
            'xlsx': [],
            'ppt': [],
            'zip': [],
            'rar': [],
            'exe': [],
            'iso': [],
            'dmg': [],
            'apk': [],
            'other': []
        }
        self.ua = UserAgent()
        self.setup_browser()

    def setup_browser(self):
        """Setup Chrome browser with optimized settings"""
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_argument('--silent')
        chrome_options.add_argument('--disable-javascript')
        chrome_options.add_argument('--disable-images')
        chrome_options.add_argument('--disable-cookies')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-popups')
        chrome_options.add_argument('--disable-geolocation')
        chrome_options.add_argument('--disable-media-stream')
        chrome_options.add_argument(f'user-agent={self.ua.random}')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.set_page_load_timeout(10)
        self.wait = WebDriverWait(self.driver, 5)

    def search_google(self, query, num_pages=3):
        """Search Google with optimized performance"""
        try:
            for page in range(num_pages):
                start = page * 10
                url = f'https://www.google.com/search?q={query}&start={start}'
                logging.info(f"Searching Google: {url}")
                
                self.driver.get(url)
                time.sleep(random.uniform(1, 2))
                
                results = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-hveid]')
                if not results:
                    logging.warning("No results found on Google")
                    break
                    
                for result in results:
                    try:
                        link = result.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                        if link and not link.startswith('https://www.google.com'):
                            self.process_link(link)
                    except NoSuchElementException:
                        continue
                        
        except Exception as e:
            logging.error(f"Error in Google search: {str(e)}")

    def search_bing(self, query, num_pages=3):
        """Search Bing with optimized performance"""
        try:
            for page in range(num_pages):
                start = page * 10
                url = f'https://www.bing.com/search?q={query}&first={start}'
                logging.info(f"Searching Bing: {url}")
                
                self.driver.get(url)
                time.sleep(random.uniform(1, 2))
                
                results = self.driver.find_elements(By.CSS_SELECTOR, 'li.b_algo')
                if not results:
                    logging.warning("No results found on Bing")
                    break
                    
                for result in results:
                    try:
                        link = result.find_element(By.CSS_SELECTOR, 'h2 a').get_attribute('href')
                        if link:
                            self.process_link(link)
                    except NoSuchElementException:
                        continue
                        
        except Exception as e:
            logging.error(f"Error in Bing search: {str(e)}")

    def process_link(self, url):
        """Process link with optimized validation"""
        try:
            if not url or not isinstance(url, str):
                return

            if not re.match(r'^https?://', url):
                return
                
            parsed = urlparse(url)
            if not parsed.netloc:
                return
                
            path = parsed.path.lower()
            if path.endswith('.pdf'):
                self.results['pdf'].append(url)
            elif path.endswith('.docx'):
                self.results['docx'].append(url)
            elif path.endswith('.xlsx'):
                self.results['xlsx'].append(url)
            elif path.endswith(('.ppt', '.pptx')):
                self.results['ppt'].append(url)
            elif path.endswith('.zip'):
                self.results['zip'].append(url)
            elif path.endswith('.rar'):
                self.results['rar'].append(url)
            elif path.endswith('.exe'):
                self.results['exe'].append(url)
            elif path.endswith('.iso'):
                self.results['iso'].append(url)
            elif path.endswith('.dmg'):
                self.results['dmg'].append(url)
            elif path.endswith('.apk'):
                self.results['apk'].append(url)
            else:
                self.results['other'].append(url)
                
        except Exception as e:
            logging.error(f"Error processing link {url}: {str(e)}")

    def save_results(self):
        """Save results with timestamp"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'webscavanger_results_{timestamp}.json'
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            logging.info(f"Results saved to {filename}")
            print(f"\nResults saved to {filename}")
        except Exception as e:
            logging.error(f"Error saving results: {str(e)}")
            print("\nError saving results")

    def close(self):
        """Close browser"""
        try:
            self.driver.quit()
        except Exception as e:
            logging.error(f"Error closing browser: {str(e)}")

def main():
    print("\nWeb Scavanger by Mohcine Otmane")
    print("Starting WebScavanger...")
    
    try:
        query = input("\nEnter your search query: ").strip()
        if not query:
            print("Search query cannot be empty")
            return
            
        num_pages = input("Enter number of pages to search (default: 3): ").strip()
        num_pages = int(num_pages) if num_pages.isdigit() else 3
        
        print("\nStarting search...")
        print("This may take a few minutes...")
        
        scraper = WebScavanger()
        
        scraper.search_google(query, num_pages)
        scraper.search_bing(query, num_pages)
        
        scraper.save_results()
        
        print("\nSearch completed!")
        print("\nResults summary:")
        for category, links in scraper.results.items():
            print(f"{category.upper()}: {len(links)} links found")
            
    except KeyboardInterrupt:
        print("\nSearch interrupted by user")
        logging.info("Search interrupted by user")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        logging.error(f"Error in main: {str(e)}")
    finally:
        if 'scraper' in locals():
            scraper.close()

if __name__ == "__main__":
    main() 