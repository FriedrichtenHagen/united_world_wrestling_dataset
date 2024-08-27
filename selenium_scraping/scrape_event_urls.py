from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import StaleElementReferenceException

import time
import pandas as pd
import logging
from selenium.webdriver.chrome.options import Options

def safe_find_elements(context, by, value, retries=3, delay=1):
    for i in range(retries):
        try:
            elements = context.find_elements(by, value)
            return elements
        except StaleElementReferenceException:
            if i < retries - 1:
                time.sleep(delay)
            else:
                raise

def scrape_event_urls():
    '''
    First all events and their respective page urls are scraped. This is the basis for scraping each event page.
    '''
    driver = None
    try:
        # Set up WebDriver

        chrome_options = Options()
        chrome_options.add_argument("--disable-search-engine-choice-screen")
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

        # Open the webpage
        driver.get("https://uww.org/events")
        driver.fullscreen_window()
        # Wait for the page to load
        time.sleep(2)

        try:
            # we will scrape all tournaments (all types, all styles, all ages, all tournaments) for each year

            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.waf-select-box')))

            event_select_boxes = driver.find_elements(By.CSS_SELECTOR, '.waf-select-box')
            year_select_box = event_select_boxes[4]
            year_select_options = year_select_box.find_elements(By.CSS_SELECTOR, '.select-list .list-item button')
                            
            # click the select box to open drop down menu of years
            driver.execute_script("arguments[0].click();", year_select_box)  
            driver.execute_script("arguments[0].classList.add('active');", year_select_box)         
            
            # this list saves all event information
            list_of_events = []

            # year
            for year_index in range(len(year_select_options)):
                print('test')
                year_select_options = year_select_box.find_elements(By.CSS_SELECTOR, '.select-list .list-item button')
                driver.execute_script("arguments[0].click();", year_select_options[year_index])
                print('test2')
                year = year_select_options[year_index].text
                print(f'Currently scraping year: {year}')
                
                monthly_tables = driver.find_elements(By.CSS_SELECTOR, '.table-wrapper')

                # month
                for month_index, month in enumerate(monthly_tables):
                    try:
                        month_and_year = month.find_element(By.CSS_SELECTOR, 'h3.table-title').text.split()
                    except:
                        month_and_year = ['NA', 'NA']

                    # Example usage
                    try:
                        # time.sleep(1)
                        events_in_month = safe_find_elements(month, By.CSS_SELECTOR, 'a.table-row')[1:]
                        # events_in_month = month.find_elements(By.CSS_SELECTOR, 'a.table-row')[1:]
                    except StaleElementReferenceException:
                        events_in_month = safe_find_elements(month, By.CSS_SELECTOR, 'a.table-row')[1:]

                    for event_index, event_link in enumerate(events_in_month):
                        event_url = event_link.get_attribute('href')
                        try:
                            day_and_month = event_link.find_element(By.CSS_SELECTOR, '.date').text.split('-')
                            start_day_digit = day_and_month[0]
                            end_day_digit = day_and_month[1]
                        except:
                            # events that are only one day
                            start_day_digit = day_and_month[0]
                            end_day_digit = day_and_month[0]
                        try:
                            tournament = event_link.find_element(By.CSS_SELECTOR, '.series span.text').text
                        except:
                            tournament = 'not available'
                        try:
                            location = event_link.find_element(By.CSS_SELECTOR, '.place span.text').text
                        except:
                            location = 'not available'
                        try:
                            type_of_tournament = event_link.find_element(By.CSS_SELECTOR, '.event span.text').text
                        except:
                            type_of_tournament = 'not available'
                        try:
                            age_group = event_link.find_element(By.CSS_SELECTOR, '.category span.text').text
                        except:
                            age_group = 'not available'
                        try:
                            wrestling_style = event_link.find_element(By.CSS_SELECTOR, '.style span.text').text
                        except:
                            wrestling_style = 'not available'
                        try:
                            extra_div = event_link.find_element(By.CSS_SELECTOR, '.extra')
                            link_element = extra_div.find_element(By.TAG_NAME, 'a')
                            extra_information_url = link_element.get_attribute('href')
                        except:
                            extra_information_url = 'not available'

                        event_information = {
                            'event_url': event_url,
                            'start_day': start_day_digit,
                            'end_day': end_day_digit,
                            'month': month_and_year[0],
                            'year': month_and_year[1],
                            'tournament': tournament,
                            'location': location,
                            'type_of_tournament': type_of_tournament,
                            'age_group': age_group,
                            'wrestling_style': wrestling_style,
                            'extra_information_pdf': extra_information_url,
                        }
                        print(event_information)
                        print('The above dict is from:')
                        print(f'event index: {event_index}')
                        print(f'month index: {month_index}')
                        print(f'year index: {year_index}')
                        list_of_events.append(event_information)
                    
            df = pd.DataFrame(list_of_events)

            # save list to csv
            df.to_csv('data/event.csv', index=False)
            print(f"CSV file has been created with {df.shape[0]} rows")

        except Exception as e:
            # print(f"Error: {e}")
            logging.exception('An error occured.')
            # Close the WebDriver
            driver.quit()
    finally:
        driver.quit()


if __name__ == "__main__":
    scrape_event_urls()