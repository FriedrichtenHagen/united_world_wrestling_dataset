from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import logging

def scrape_athlete_urls():
    '''
    First all athletes and their respective page urls are scraped. This is the basis for scraping each athlete page.
    '''
    try:
        # Set up WebDriver
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

        # Open the webpage
        driver.get("https://uww.org/athletes-results")
        driver.fullscreen_window()
        # Wait for the page to load
        time.sleep(2)

        try:
            # go throught the three existing wrestling styles: Freestyle, Greco-Roman, Women's Wrestling
            wrestling_styles = ['Freestyle', 'Greco-Roman', 'Womens Wrestling']
            wrestling_stye_buttons = driver.find_elements(By.CSS_SELECTOR, '.select-list>.list-item')
                        
            # create list of athlete entries
            list_of_athletes = []

            for index, wrestling_style in enumerate(wrestling_styles):
                driver.execute_script("arguments[0].click();", wrestling_stye_buttons[index])

                logging.debug(f'Currently working on: {wrestling_style}')
                

                selected_elements = driver.find_elements(By.CSS_SELECTOR, '.tab-name>.tab-text')
            
                # filter for the weight class buttons
                weight_class_buttons = selected_elements[1:11]

                # weight class
                for index, weight_class_button in enumerate(weight_class_buttons):
                    current_weight_class = weight_class_buttons[index].text

                    current_wrestling_style = wrestling_style
                    # extract the athlete names and urls
                    # weight_class_button.click()
                    driver.execute_script("arguments[0].click();", weight_class_button)
                    # time.sleep(5)

                    ## athletes
                    # top three athletes 
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
                            'current_wrestling_style': current_wrestling_style,
                            'weight_class': current_weight_class,
                            'ranking': ranking,
                            'full_name': full_name,
                            'url': url
                        }
                        list_of_athletes.append(athlete_entry)
                    # all other athletes of the weight class
                    # we first need to click all 'Load More' buttons so that all athletes are visible
                    try:
                        # as long as there is a button to click:
                        while driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Load More']"):
                            load_more_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Load More']")
                            driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
                            # Wait until the button with aria-label 'Load More' is present and clickable
                            load_more_button = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Load More']"))
                            )
                            # Click the button
                            driver.execute_script("arguments[0].click();", load_more_button)
                            print("Button clicked successfully.")
                            time.sleep(1)
                    except Exception as e:
                        print(f"An error occurred while clicking the button: {e}")
                        break

                    # extract all the other athletes
                    all_other_athletes = driver.find_elements(By.CSS_SELECTOR, '.table-body>a.table-row')
                    for other_athlete in all_other_athletes:
                        # Find all child elements of the parent
                        ranking = other_athlete.find_element(By.CSS_SELECTOR, '.table-data.rank>.text').text
                        # first_name = other_athlete.find_element(By.CSS_SELECTOR, '.full-name>.fname').text
                        # last_name = other_athlete.find_element(By.CSS_SELECTOR, '.full-name>.lname').text
                        # Extract the full name
                        full_name_element = other_athlete.find_element(By.CSS_SELECTOR, 'div.table-info h3.fullname.name')
                        full_name = full_name_element.text.replace('\n', ' ')

                        # Extract the country
                        country_element = other_athlete.find_element(By.CSS_SELECTOR, 'div.country span.text')
                        country = country_element.text
                        # country = other_athlete.find_element(By.CSS_SELECTOR, '.table-data.player.country>.text').text
                        url = other_athlete.get_attribute('href')
                        athlete_entry = {
                            'current_wrestling_style': current_wrestling_style,
                            'weight_class': current_weight_class,
                            'ranking': ranking,
                            'full_name': full_name,
                            'url': url
                        }
                        list_of_athletes.append(athlete_entry)
                        logging.info(f'Athlete number {len(list_of_athletes)} scraped successfully.')


            df = pd.DataFrame(list_of_athletes)

            # save list to csv
            df.to_csv('data/athlete_urls.csv', index=False)
            print(f"CSV file has been created with {df.shape[0]} rows")

        except Exception as e:
            print(f"Error: {e}")

            # Close the WebDriver
            driver.quit()
    finally:
        driver.quit()


if __name__ == "__main__":
    scrape_athlete_urls()