from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup


try:
    # Set up WebDriver
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    # Open the webpage
    driver.get("https://uww.org/athletes-results")

    # Wait for the page to load
    time.sleep(2)

    try:
        selected_elements = driver.find_elements(By.CSS_SELECTOR, '.tab-name>.tab-text')
        desired_texts = {'57 kg', '61 kg', '65 kg', '70 kg', '74 kg', '79 kg', '86 kg', '92 kg', '97 kg', '125 kg'}

        # Filter the elements by their text content
        weight_class_buttons = [element for element in selected_elements if element.text in desired_texts]

        for weight_class_button in weight_class_buttons:

            weight_class_button.click()
            # time.sleep(5)  # Wait for new content to load



            # # Get the page source and parse it with BeautifulSoup
            # page_source = driver.page_source
            # soup = BeautifulSoup(page_source, 'html.parser')

            # # Example: Find all athlete names
            # athlete_names = soup.find_all('div', class_='athlete-name')
            # for name in athlete_names:
            #     print(name.text)


        # # Extract and print the text inside <span> elements
        # for item in list_items:
        #     span = item.find('span', class_='tab-text')
        #     if span:
        #         print(span.text)



    except Exception as e:
        print(f"Error: {e}")

    # Scrape content
    try:
        athletes = driver.find_elements(By.CLASS_NAME, 'athlete-name')
        for athlete in athletes:
            print(athlete.text)
    except Exception as e:
        print(f"Error: {e}")

    # Close the WebDriver
    driver.quit()







finally:
    driver.quit()