import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

file_path = 'data/athlete_urls.csv'

# Open the CSV file
with open(file_path, mode='r', newline='') as file:
    # Create a CSV reader
    csv_reader = csv.reader(file)
    
    # skip the header
    next(csv_reader)

    list_of_athlete_data = []
    try:
        # Set up headless Chrome WebDriver
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

        for row in csv_reader:
            print(row[3])
            athlete_page_url = row[3]
            
            # Set up WebDriver
            driver.get(athlete_page_url)
            try:
                # Use WebDriverWait to wait for elements to be present
                first_name = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.name.fname'))
                ).text                
                last_name = driver.find_element(By.CSS_SELECTOR, '.name.lname').text
                card_meta_values = driver.find_elements(By.CSS_SELECTOR, '.card-meta-value')
                country = card_meta_values[0].text
                age = card_meta_values[1].text
                weight = card_meta_values[2].text
                style = card_meta_values[3].text
                ranking = card_meta_values[4].text

                biography = driver.find_element(By.CSS_SELECTOR, '.content-wrap').text

                athlete_data = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'country': country,
                    'age': age,
                    'weight': weight,
                    'style': style,
                    'ranking': ranking,
                    'biography': biography,
                }
                print(athlete_data)
                # uww records
                list_of_athlete_data.append(athlete_data)


            except Exception as e:
                print(f"Error: {e}")
        if list_of_athlete_data:
            df = pd.DataFrame(list_of_athlete_data)
            df.to_csv('data/athletes.csv', index=False)
            print(f"CSV file has been created with {df.shape[0]} rows")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        driver.quit()
