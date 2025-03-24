import requests
import json
import time
from typing import Dict, List
import logging
from datetime import datetime
import re
import random
from urllib.parse import urlparse, quote, unquote
import concurrent.futures
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import undetected_chromedriver as uc
import os
from bs4 import BeautifulSoup
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('webscavanger.log'),
        logging.StreamHandler()
    ]
)

class WebScavanger:
    def __init__(self):
        self.visited_urls = set()
        self.drive_links = {
            'documents': [],
            'images': [],
            'videos': [],
            'audio': [],
            'archives': [],
            'spreadsheets': [],
            'presentations': [],
            'pdfs': [],
            'other': []
        }
        
        self.search_engines = {
            'google': {
                'url': 'https://www.google.com/search',
                'params': {'start': ''},
                'pagination': lambda x: x * 10,
                'max_retries': 3
            },
            'bing': {
                'url': 'https://www.bing.com/search',
                'params': {'first': ''},
                'pagination': lambda x: x * 10 + 1,
                'max_retries': 3
            }
        }
        
        self.initialize_driver()
        
    def initialize_driver(self):
        try:
            options = uc.ChromeOptions()
            options.add_argument('--start-maximized')
            options.add_argument('--disable-popup-blocking')
            options.add_argument('--disable-notifications')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument(f'user-agent={UserAgent().random}')
            
            self.driver = uc.Chrome(options=options)
            self.driver.set_page_load_timeout(30)
            logging.info("Chrome driver initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize Chrome driver: {str(e)}")
            raise

    def categorize_link(self, url: str) -> str:
        url = url.lower()
        if 'pdf' in url:
            return 'pdfs'
        elif any(ext in url for ext in ['.doc', '.docx', '.txt', '.rtf']):
            return 'documents'
        elif any(ext in url for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']):
            return 'images'
        elif any(ext in url for ext in ['.mp4', '.avi', '.mov', '.wmv']):
            return 'videos'
        elif any(ext in url for ext in ['.mp3', '.wav', '.ogg', '.m4a']):
            return 'audio'
        elif any(ext in url for ext in ['.zip', '.rar', '.7z', '.tar', '.gz']):
            return 'archives'
        elif any(ext in url for ext in ['.xls', '.xlsx', '.csv']):
            return 'spreadsheets'
        elif any(ext in url for ext in ['.ppt', '.pptx']):
            return 'presentations'
        else:
            return 'other'

    def is_valid_link(self, url: str) -> bool:
        try:
            url = unquote(url)
            url = url.split('&')[0]
            url = url.split('#')[0]
            
            if any(x in url.lower() for x in ['login', 'signup', 'register', 'account', 'profile']):
                return False
                
            file_extensions = [
                '.pdf', '.doc', '.docx', '.txt', '.rtf',
                '.jpg', '.jpeg', '.png', '.gif', '.bmp',
                '.mp4', '.avi', '.mov', '.wmv',
                '.mp3', '.wav', '.ogg', '.m4a',
                '.zip', '.rar', '.7z', '.tar', '.gz',
                '.xls', '.xlsx', '.csv',
                '.ppt', '.pptx'
            ]
            
            has_valid_extension = any(ext in url.lower() for ext in file_extensions)
            
            file_hosting_domains = [
                'drive.google.com', 'dropbox.com', 'mediafire.com',
                'mega.nz', 'rapidshare.com', '4shared.com',
                'scribd.com', 'slideshare.net', 'academia.edu',
                'researchgate.net', 'archive.org', 'github.com',
                'sourceforge.net', 'bitbucket.org'
            ]
            
            is_file_hosting = any(domain in url.lower() for domain in file_hosting_domains)
            
            return has_valid_extension or is_file_hosting
            
        except Exception as e:
            logging.error(f"Error validating URL {url}: {str(e)}")
            return False

    def handle_captcha(self) -> bool:
        try:
            captcha_indicators = [
                "g-recaptcha",
                "recaptcha",
                "captcha",
                "I'm not a robot",
                "verify you're a human"
            ]
            
            page_source = self.driver.page_source.lower()
            if any(indicator.lower() in page_source for indicator in captcha_indicators):
                logging.warning("CAPTCHA detected! Waiting for manual intervention...")
                WebDriverWait(self.driver, 300).until(
                    lambda driver: not any(indicator.lower() in driver.page_source.lower() 
                                         for indicator in captcha_indicators)
                )
                logging.info("CAPTCHA solved successfully!")
                return True
            return True
        except TimeoutException:
            logging.error("CAPTCHA solving timeout!")
            return False
        except Exception as e:
            logging.error(f"Error handling CAPTCHA: {str(e)}")
            return False

    def search_with_selenium(self, engine_name: str, query: str, page: int) -> List[dict]:
        engine = self.search_engines[engine_name]
        retries = 0
        
        while retries < engine['max_retries']:
            try:
                url = f"{engine['url']}?q={quote(query)}&{list(engine['params'].keys())[0]}={engine['pagination'](page)}"
                logging.info(f"Accessing URL: {url}")
                self.driver.get(url)
                
                try:
                    WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-hveid]" if engine_name == 'google' else "li.b_algo"))
                    )
                except TimeoutException:
                    logging.warning("Timeout waiting for search results, trying to proceed anyway")
                
                if not self.handle_captcha():
                    retries += 1
                    time.sleep(random.uniform(5, 10))
                    continue
                
                last_height = self.driver.execute_script("return document.body.scrollHeight")
                while True:
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(3)
                    new_height = self.driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
                
                selector = "div[data-hveid]" if engine_name == 'google' else "li.b_algo"
                search_results = self.driver.find_elements(By.CSS_SELECTOR, selector)
                logging.info(f"Found {len(search_results)} search results on page {page + 1}")
                
                found_links = []
                for result in search_results:
                    try:
                        links = result.find_elements(By.TAG_NAME, "a")
                        for link in links:
                            href = link.get_attribute('href')
                            if href and self.is_valid_link(href):
                                logging.info(f"Found valid link: {href}")
                                if href not in self.visited_urls:
                                    self.visited_urls.add(href)
                                    try:
                                        main_window = self.driver.current_window_handle
                                        
                                        self.driver.execute_script(f'window.open("{href}", "_blank");')
                                        time.sleep(3)
                                        
                                        new_window = self.driver.window_handles[-1]
                                        self.driver.switch_to.window(new_window)
                                        
                                        try:
                                            WebDriverWait(self.driver, 10).until(
                                                EC.presence_of_element_located((By.TAG_NAME, "body"))
                                            )
                                            
                                            page_source = self.driver.page_source
                                            soup = BeautifulSoup(page_source, 'html.parser')
                                            
                                            title = soup.title.string if soup.title else "Untitled"
                                            description = ""
                                            meta_desc = soup.find('meta', {'name': 'description'})
                                            if meta_desc:
                                                description = meta_desc.get('content', '')
                                            
                                            category = self.categorize_link(href)
                                            found_links.append({
                                                'url': href,
                                                'title': title,
                                                'description': description,
                                                'category': category,
                                                'source': engine_name,
                                                'timestamp': datetime.now().isoformat()
                                            })
                                            
                                        except Exception as e:
                                            logging.error(f"Error processing page {href}: {str(e)}")
                                        
                                        finally:
                                            self.driver.close()
                                            self.driver.switch_to.window(main_window)
                                            
                                    except Exception as e:
                                        logging.error(f"Error opening link {href}: {str(e)}")
                                        continue
                                        
                    except Exception as e:
                        logging.error(f"Error processing search result: {str(e)}")
                        continue
                
                return found_links
                
            except Exception as e:
                logging.error(f"Error during search on {engine_name}: {str(e)}")
                retries += 1
                time.sleep(random.uniform(5, 10))
                continue
        
        return []

    def search_drive_links(self, query: str, num_pages: int = 3) -> Dict[str, List[dict]]:
        for engine_name in self.search_engines:
            for page in range(num_pages):
                try:
                    found_links = self.search_with_selenium(engine_name, query, page)
                    for link in found_links:
                        category = link['category']
                        if category in self.drive_links:
                            self.drive_links[category].append(link)
                except Exception as e:
                    logging.error(f"Error searching on {engine_name} page {page + 1}: {str(e)}")
                    continue
                
                time.sleep(random.uniform(3, 7))
        
        return self.drive_links

    def save_to_json(self, filename: str = 'webscavanger_results.json'):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.drive_links, f, indent=4, ensure_ascii=False)
            logging.info(f"Results saved to {filename}")
        except Exception as e:
            logging.error(f"Error saving results to {filename}: {str(e)}")

    def __del__(self):
        try:
            if hasattr(self, 'driver'):
                self.driver.quit()
        except Exception as e:
            logging.error(f"Error closing driver: {str(e)}")

def main():
    try:
        print("Web Scavanger by Mohcine Otmane")
        print("Starting WebScavanger...")
        scraper = WebScavanger()
        
        query = input("Enter your search query: ")
        num_pages = int(input("Enter number of pages to search (default: 3): ") or "3")
        
        print(f"\nSearching for: {query}")
        print(f"Number of pages: {num_pages}")
        print("Please Wait...\n")
        
        results = scraper.search_drive_links(query, num_pages)
        
        print("\nSearch completed!")
        print("\nResults by category:")
        for category, links in results.items():
            print(f"\n{category.upper()}: {len(links)} links found")
            for link in links[:5]:
                print(f"- {link['title']}")
                print(f"  URL: {link['url']}")
                if link['description']:
                    print(f"  Description: {link['description'][:100]}...")
                print()
        
        scraper.save_to_json()
        print(f"\nDetailed results saved to webscavanger_results.json")
        
    except Exception as e:
        logging.error(f"Critical error in main: {str(e)}")
        print(f"\nAn error occurred: {str(e)}")
    finally:
        print("\nPress Enter to exit...")
        input()

if __name__ == "__main__":
    main() 