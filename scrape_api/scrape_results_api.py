import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time


# generate athlete urls from athletes.csv
def scrape_results():
    df = pd.read_csv('data/athletes.csv')
    print(df.head())

    person_ids = df['person.id']
    person_displayname_fullnames = df['person.displayname.fullname']
    print(person_ids,person_displayname_fullnames)

    # loop through each row
    for row_index, id in enumerate(person_ids):
        fullname_hyphen_separated = person_displayname_fullnames[row_index].strip().replace(' ', '-').lower()
        url = f'https://uww.org/athletes-results/{fullname_hyphen_separated}-{id}-profile'
        print(url)

        try:
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)

            # Initialize the WebDriver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.get(url)

            # Wait for the page to load
            time.sleep(5)  # Adjust this sleep time if needed

            # Use XPath to find the element containing text 'Results'
            xpath = "//li[contains(@class, 'tab-name')]//button[contains(@class, 'tab-anchor')]//span[text()='Results']/.."
            tab_element = driver.find_element(By.XPATH, xpath)
            tab_element.click()

            # Wait for content to be dynamically loaded
            time.sleep(2)  # Adjust if needed depending on the load time

            # tabs-container-group
            tabs_container_groups = driver.find_elements(By.CSS_SELECTOR, '.tabs-container-group')
            for group in tabs_container_groups:
                # Extract the title
                year = group.find_element(By.CSS_SELECTOR, 'h3.tabs-container-title').text.strip()
                print(f"Year: {year}")
                
                # tabs-container-content
                tabs_container_contents = group.find_elements(By.CSS_SELECTOR, 'div.tabs-container-content')
                for tabs_container_content in tabs_container_contents:
                    
                    # content-item: each item is on result listing
                    content_items = tabs_container_content.find_elements(By.CSS_SELECTOR, 'div.content-item')
                    for content_item in content_items:
                        tournament_name = content_item.find_element(By.CSS_SELECTOR, '.text').text
                        metas = content_item.find_elements(By.CSS_SELECTOR, '.meta')
                        tournament_country = metas[0].text
                        tournament_month_year = metas[1].text
                        tournament_weight_class = metas[2].text

                        # after extracting the tournament details it is time to get the matches of that tournament






                    print(tabs_container_groups)
                    for i, element in enumerate(tabs_container_groups):
                        print(f"Element {i + 1}:")
                        print(element.get_attribute('outerHTML'))
                        print("-" * 50)


        finally:
            # Close the browser
            driver.quit()





if __name__ == "__main__":
    scrape_results()