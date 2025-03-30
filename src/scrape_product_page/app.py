import json
import logging
import os
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def setup_chrome_driver():
    chrome_binary = os.getenv("CHROME_BINARY", "/opt/bin/chrome-linux64/chrome")
    driver_path = os.getenv("DRIVER_PATH", "/opt/bin/chromedriver-linux64/chromedriver")
    
    chrome_options = Options()
    chrome_options.binary_location = chrome_binary
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")

    # Initialize WebDriver
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def scrape_product_page(url):
    driver = setup_chrome_driver()
    
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
        )
        time.sleep(5)
        
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        for svg_tag in soup.body.find_all('svg'):
                svg_tag.decompose()

        for script_tag in soup.body.find_all('script'):
            script_tag.decompose()

        for style_tag in soup.body.find_all('style'):
            style_tag.decompose()

        for img_tag in soup.body.find_all('img'):
            img_tag.decompose()

        return soup.body.get_text(separator=' ', strip=True)
    except Exception as e:
        logger.error(f"Error scraping URL {url}: {str(e)}")
        raise e
    finally:
        driver.quit()


def lambda_handler(event, context):
    logger.info('Received event: %s', json.dumps(event))

    if "url" not in event:
        err_msg = "URL not provided"
        logger.error(err_msg)
        raise ValueError(err_msg)

    url = event.get("url")
    
    time.sleep(600)
    try:
        body_content = scrape_product_page(url)
        logger.info('Time remaining: %d second(s)', (context.get_remaining_time_in_millis() / 1000))
        return {
            "body_content": body_content
        }
    except Exception as e:
        logger.error(f"Failed to scrape product page {str(e)}")
        raise e
    
