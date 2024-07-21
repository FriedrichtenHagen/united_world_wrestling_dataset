from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup
import pandas as pd
import json

try:
    # Set up WebDriver
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    # Open the webpage
    driver.get("https://uww.org/athletes-results")
    driver.fullscreen_window()
    # Wait for the page to load
    time.sleep(2)

    try:
        selected_elements = driver.find_elements(By.CSS_SELECTOR, '.tab-name>.tab-text')
        weight_classes_in_kg = ['57 kg', '61 kg', '65 kg', '70 kg', '74 kg', '79 kg', '86 kg', '92 kg', '97 kg', '125 kg']

        # Filter the elements by their text content
        weight_class_buttons = [element for element in selected_elements if element.text in weight_classes_in_kg]

        # create list of athlete entries
        list_of_athletes = []

        # weight class
        for index, weight_class_button in enumerate(weight_class_buttons):
            current_weight_class = weight_classes_in_kg[index]
            # extract the athlete names and urls
            weight_class_button.click()
            # time.sleep(5)

            

            # athletes
            top_three_athletes = driver.find_elements(By.CSS_SELECTOR, '.card-list>a.card-item')
            for top_three_athlete in top_three_athletes:
                text = top_three_athlete.text
                parts = text.split('\n')
                ranking = parts[0]
                # we don't need the athlete information, since we will extract that from the athlete pages
                full_name = parts[1] + parts[2]
                full_name = ' '.join(parts[1:-2])
                # points = parts[3].split(' ')[0]
                # nation = parts[4]
                url = top_three_athlete.get_attribute('href')

                athlete_entry = {
                    'weight_class': current_weight_class,
                    'ranking': ranking,
                    'full_name': full_name,
                    'url': url
                }
                list_of_athletes.append(athlete_entry)

        df = pd.DataFrame(list_of_athletes)

        # save list to csv
        df.to_csv('data/athlete_urls.csv', index=False)
        print("CSV file has been created.")

    except Exception as e:
        print(f"Error: {e}")

    # Close the WebDriver
    driver.quit()
finally:
    driver.quit()