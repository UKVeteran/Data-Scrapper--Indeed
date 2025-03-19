from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os
from webdriver_manager.chrome import ChromeDriverManager
import time
import random

def scrape_indeed(job_title, location, num_pages=1):
    job_title = job_title.replace(' ', '+')
    location = location.replace(' ', '+')
    base_url = 'https://www.indeed.com/jobs'
    
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    
    # To avoid detection, we'll use a random User-Agent header
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36 Edge/17.17134'
    ]
    user_agent = random.choice(user_agents)
    chrome_options.add_argument(f"user-agent={user_agent}")
    
    # Set up Chrome WebDriver (use webdriver_manager to automatically manage ChromeDriver)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    job_listings = []
    
    for page in range(0, num_pages * 10, 10):
        url = f'{base_url}?q={job_title}&l={location}&start={page}'
        driver.get(url)
        
        # Wait for the page to load and for the job cards to become visible
        try:
            job_cards_element = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.jobsearch-SerpJobCard'))
            )
        except Exception as e:
            print(f"Error loading page: {e}")
            continue
        
        job_cards = driver.find_elements(By.CSS_SELECTOR, '.jobsearch-SerpJobCard')
        
        if len(job_cards) == 0:
            print(f"No job cards found on page {page // 10 + 1}.")
        
        for job_card in job_cards:
            try:
                title = job_card.find_element(By.CSS_SELECTOR, 'h2.title').text.strip()
            except:
                title = 'N/A'
            
            try:
                company = job_card.find_element(By.CSS_SELECTOR, '.company').text.strip()
            except:
                company = 'N/A'
            
            try:
                location = job_card.find_element(By.CSS_SELECTOR, '.location').text.strip()
            except:
                location = 'N/A'
            
            try:
                summary = job_card.find_element(By.CSS_SELECTOR, '.summary').text.strip()
            except:
                summary = 'N/A'
            
            job_listings.append({'Title': title, 'Company': company, 'Location': location, 'Summary': summary})
        
        print(f"Page {page // 10 + 1} parsed, found {len(job_listings)} job listings so far.")
    
    # Check if any job listings were found
    if not job_listings:
        print("No job listings found. Please check the HTML structure or the query.")
    
    # Set the file path to save the CSV
    save_path = r'C:\Users\jau19\Downloads\Data Scrapper\indeed_jobs.csv'
    
    # Ensure the directory exists before saving the file
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    df = pd.DataFrame(job_listings)
    
    if not df.empty:  # Ensure data is not empty before saving
        df.to_csv(save_path, index=False)
        print(f'Scraping complete. Data saved to {save_path}')
    else:
        print("No data to save.")
    
    # Close the browser
    driver.quit()

# Example
scrape_indeed('Administrator', 'Kent', num_pages=2)
