from typing import Type, Dict, List
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from langchain_community.llms import OpenAI, Ollama
import litellm
import time
import re
import json
import csv
import os


print(__name__)
class FetchResearchSeleniumInput(BaseModel):
    """Input schema for FetchResearchSelenium."""
    search: str = Field(..., description="Search terms for Reddit (e.g., 'large language models'). search MUST be a single string enclosed in double quotes, like this: \"{search}\"")

class FetchResearchSelenium(BaseTool):
    name: str = "FetchResearchSelenium"
    description: str = (
        "This tool fetches Reddit posts. "
        "Provide ONLY the search term enclosed in double quotes. "        
    )
    args_schema: Type[BaseModel] = FetchResearchSeleniumInput

    def _run(self, search: str) -> List[Dict[str, str]]:

        max_retries = 2
        attempts = 0

        try:
            driver = webdriver.Chrome()
            wait = WebDriverWait(driver, 10)  # Maximum wait time of 10 seconds
            # Navigate to Reddit
            driver.get("https://www.reddit.com/")
            shadow_host1 = wait.until(EC.element_to_be_clickable((By.TAG_NAME, "reddit-search-large")))
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "reddit-search-large")))
            shadow_host1 = wait.until(EC.presence_of_element_located((By.TAG_NAME, "reddit-search-large")))
            print("shadow host1: ", shadow_host1)
            shadow_host1.click()    
            shadow_host1.send_keys(search) 
            shadow_host1.send_keys(Keys.RETURN)             



            try:
                # Find all post elements
                post_elements = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[data-testid="post-title"]'))
                )
                print("post elements: ", post_elements)
                # for post_check in post_elements:
                #     print("post: ", post_check)
                
                # Extract data from each post element
                titles = []
                urls = []
                for post_element in post_elements:
                    try:
                        # Extract the title using the more specific selector                
                        title = post_element.get_attribute('aria-label')  # Get the full title from aria-label
                        print(f"aria-label: {title}")  # Print the extracted title
                        print(f"Type of title: {type(titles)}")  # Print the type of title
                        
                        href = post_element.get_attribute("href")  # Get the link from href                
                        print(f"aria-label: {href}")  # Print the extracted title
                        print(f"Type of title: {type(href)}")  # Print the type of title
                        titles.append(title)
                        urls.append(href)

                    except Exception as e:
                        print(f"Error extracting data from post element: {e}")

                # Close the browser
                driver.quit()

                print(f"titles: {titles}")
                print(f"Type of urls {type(titles)}")  # Print the type of urls
                print(f"URLS: {urls}")
                print(f"Type of urls {type(urls)}")  # Print the type of urls
                #posts = dict(zip(titles, urls))
                posts = [{"title": title, "url": url} for title, url in zip(titles, urls)]
                
                
                result = json.dumps(posts)
                
                filename = "posts_dump.csv"
                try:
                    #Writing to CSV File
                    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
                        #create csv writer object
                        csvwriter = csv.writer(csvfile)
                        
                        #write Headers
                        csvwriter.writerow(["Post Title", "URL"])
                        
                        #write data rows
                        for post in posts:
                            csvwriter.writerow([post['title'], post['url']])
                    print(f"Data written to {filename}")
                    
                    #writing to JSON
                    # Writing to JSON file
                    json_dump = "json_dump.json"

                    if os.path.exists(json_dump):
                        with open(json_dump, 'r') as f:
                            existing_data = json.load(f)
                            if not isinstance(existing_data, list):
                                existing_data = []
                    else:
                        existing_data = []

                    existing_data.extend(posts)

                    with open(json_dump, 'w') as jsonfile:
                        json.dump(existing_data, jsonfile, indent=4)

                    print(f"Data written to {json_dump}")

                except Exception as ee:
                    print(f"Failed to write to JSON file: {ee}")

                return posts  # Return the list of dictionaries
            
            except Exception as ee:
                max_retries = 2
                attempts = 0
                driver.quit()
                if attempts == max_retries:
                    print(f"Failed to fetch data after multiple retries: {ee}")
                    driver.quit()
                attempts += 1
                print(f"Error encountered: {ee}. Retrying...")
                time.sleep(2)
                driver.quit()

        except Exception as eee:
            print(f"Failed to initial driver.get() or send_keys:  {eee}")
            driver.quit()  
            
class FetchCommentsInput(BaseModel):
    """Input schema for FetchComments."""
    URL: str = Field(..., description="URL returned from using the JSONSearchTool. The URL should be in standard https format as a human would normally type into the browser")

class FetchComments(BaseTool):
    name: str = "FetchComments"
    description: str = (
        "This accepts a URL in string format as an argument. It uses the Selenium webdriver to access the webpage and the scrapes html elements for comments"
        "It returns a list of dictionaries with keyword pairs with a generic example being {'username': 'reddit username'; 'comment_text': 'comment text'}"      
    )
    args_schema: Type[BaseModel] = FetchResearchSeleniumInput

    def _run(self, URL: str) -> List[Dict[str, str]]:

        max_retries = 2
        attempts = 0

        try:
            driver = webdriver.Chrome()
            wait = WebDriverWait(driver, 10)  # Maximum wait time of 10 seconds
            # Navigate to Reddit
            driver.get(URL)
            shadow_host1 = wait.until(EC.element_to_be_clickable((By.TAG_NAME, "reddit-search-large")))
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "reddit-search-large")))
            shadow_host1 = wait.until(EC.presence_of_element_located((By.TAG_NAME, "reddit-search-large")))
            print("shadow host1: ", shadow_host1)
            shadow_host1.click()    
            shadow_host1.send_keys(search) 
            shadow_host1.send_keys(Keys.RETURN) 
        except Exception as eee:
            print(f"Failed to initial driver.get() or send_keys:  {eee}")
            driver.quit() 