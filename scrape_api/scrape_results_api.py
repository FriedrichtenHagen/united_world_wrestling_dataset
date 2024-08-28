import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import StaleElementReferenceException

def load_checkpoint():
    if os.path.exists('last_processed.txt'):
        with open('last_processed.txt', 'r') as file:
            return int(file.read().strip())
    return 0

def save_checkpoint(index):
    with open('last_processed.txt', 'w') as file:
        file.write(str(index))

def click_element_with_retry(driver, element, retries=3):
    for attempt in range(retries):
        try:
            element.click()
            return
        except StaleElementReferenceException:
            print(f"Retrying click for stale element. Attempt {attempt + 1}")
            # Optionally, re-locate the element if needed
            element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, element)))
    raise Exception("Failed to click the element after several retries.")        

def scrape_results():
    df = pd.read_csv('data/athletes.csv')

    person_ids = df['person.id']
    person_displayname_fullnames = df['person.displayname.fullname']

    # Load progress
    start_index = load_checkpoint()

    # Load previously saved data if exists
    if os.path.exists('data/matches.csv'):
        match_result_list = pd.read_csv('data/matches.csv').to_dict('records')
    else:
        match_result_list = []

    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
    chrome_options.add_argument("--disable-search-engine-choice-screen")
    chrome_options.add_argument("--disable-gpu")  # Disable GPU for faster performance
    chrome_options.add_argument("--disable-extensions")  # Disable extensions

    # Initialize the WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Loop through each row (athlete page) starting from the last processed index
        for row_index in range(start_index, len(person_ids)):
            id = person_ids[row_index]
            fullname_hyphen_separated = person_displayname_fullnames[row_index].strip().replace(' ', '-').lower()
            url = f'https://uww.org/athletes-results/{fullname_hyphen_separated}-{id}-profile'
            print(f'Processing {url}')

            driver.get(url)
            wait = WebDriverWait(driver, 10)  # 10 seconds timeout

            xpath = "//li[contains(@class, 'tab-name')]//button[contains(@class, 'tab-anchor')]//span[text()='Results']/.."            
            try:
                tab_element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                click_element_with_retry(driver, tab_element)
            except Exception as e:
                print(f"Error while clicking tab: {e}")
                continue  # Skip to next athlete

            tabs_container_groups = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.tabs-container-group')))

            for group in tabs_container_groups:
                year = group.find_element(By.CSS_SELECTOR, 'h3.tabs-container-title').text.strip()
                
                tabs_container_contents = group.find_elements(By.CSS_SELECTOR, 'div.tabs-container-content')
                for tabs_container_content in tabs_container_contents:
                    tournament_name = tabs_container_content.find_element(By.CSS_SELECTOR, '.waf-accordion-title .card-info .text').text
                    metas = tabs_container_content.find_elements(By.CSS_SELECTOR, '.waf-accordion-title .meta')
                    tournament_country = metas[0].text
                    tournament_month_year = metas[1].text
                    tournament_weight_class = metas[2].text

                    button_btn_link = tabs_container_content.find_element(By.CSS_SELECTOR, 'button.btn-link')
                    driver.execute_script("arguments[0].scrollIntoView(true);", button_btn_link)
                    driver.execute_script("arguments[0].click();", button_btn_link)

                    accordion_panel_content_items = driver.find_elements(By.CSS_SELECTOR, '.waf-accordion-panel .content-item')
                    for match in accordion_panel_content_items:
                        wrestler_a = match.find_element(By.CSS_SELECTOR, 'div.card-item.card-a')
                        name_a = wrestler_a.find_element(By.CSS_SELECTOR, 'span.card-label').text.strip().title()
                        image_a = wrestler_a.find_element(By.CSS_SELECTOR, 'img').get_attribute('src')
                        score_a = wrestler_a.find_element(By.CSS_SELECTOR, 'div.card-number').text.strip()

                        wrestler_b = match.find_element(By.CSS_SELECTOR, 'div.card-item.card-b')
                        name_b = wrestler_b.find_element(By.CSS_SELECTOR, 'span.card-label').text.strip().title()
                        image_b = wrestler_b.find_element(By.CSS_SELECTOR, 'img').get_attribute('src')
                        score_b = wrestler_b.find_element(By.CSS_SELECTOR, 'div.card-number').text.strip()

                        result = match.find_element(By.CSS_SELECTOR, 'div.card-status span.text.status').text.strip()

                        match_information = {
                            'wrestler_a': name_a,
                            'wrestler_b': name_b,
                            'score_a': score_a,
                            'score_b': score_b,
                            'match_result': result,
                            'image_a': image_a,
                            'image_b': image_b,
                            'tournament_name': tournament_name,
                            'tournament_weight_class': tournament_weight_class,
                            'tournament_country': tournament_country,
                            'tournament_month_year': tournament_month_year,
                        }
                        match_result_list.append(match_information)

            # Save progress after each athlete
            save_checkpoint(row_index)
            if row_index % 5 == 0:  # Save every 5 athletes
                df = pd.DataFrame(match_result_list)
                df.to_csv('data/matches.csv', index=False)
                print(f"Saved progress at athlete {row_index}")

    finally:
        driver.quit()

    # Final save after all athletes are processed
    df = pd.DataFrame(match_result_list)
    df.to_csv('data/matches.csv', index=False)
    print("Final data saved.")

if __name__ == "__main__":
    scrape_results()