import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def scrape_results():
    df = pd.read_csv('data/athletes.csv')

    person_ids = df['person.id']
    person_displayname_fullnames = df['person.displayname.fullname']

    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
    chrome_options.add_argument("--disable-search-engine-choice-screen")
    chrome_options.add_argument("--disable-gpu")  # Disable GPU for faster performance
    chrome_options.add_argument("--disable-extensions")  # Disable extensions

    # Initialize the WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    match_result_list = []
    try:
        # loop through each row (athlete page)
        for row_index, id in enumerate(person_ids):
            fullname_hyphen_separated = person_displayname_fullnames[row_index].strip().replace(' ', '-').lower()
            url = f'https://uww.org/athletes-results/{fullname_hyphen_separated}-{id}-profile'
            print(url)


            driver.get(url)
            wait = WebDriverWait(driver, 10)  # 10 seconds timeout

            xpath = "//li[contains(@class, 'tab-name')]//button[contains(@class, 'tab-anchor')]//span[text()='Results']/.."            
            tab_element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            # tab_element = driver.find_element(By.XPATH, xpath)
            tab_element.click()

            # tabs-container-group
            # tabs_container_groups = driver.find_elements(By.CSS_SELECTOR, '.tabs-container-group')
            tabs_container_groups = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.tabs-container-group')))

            for group in tabs_container_groups:
                # Extract the title
                year = group.find_element(By.CSS_SELECTOR, 'h3.tabs-container-title').text.strip()
                print(f"Year: {year}")
                
                # tabs-container-content: each item is one tournament (including the results)
                tabs_container_contents = group.find_elements(By.CSS_SELECTOR, 'div.tabs-container-content')
                for tabs_container_content in tabs_container_contents:
                    
                    tournament_name = tabs_container_content.find_element(By.CSS_SELECTOR, '.waf-accordion-title .card-info .text').text
                    metas = tabs_container_content.find_elements(By.CSS_SELECTOR, '.waf-accordion-title .meta')
                    tournament_country = metas[0].text
                    tournament_month_year = metas[1].text
                    tournament_weight_class = metas[2].text

                    # after extracting the tournament details it is time to get the matches of that tournament
                    button_btn_link = tabs_container_content.find_element(By.CSS_SELECTOR, 'button.btn-link')
                    driver.execute_script("arguments[0].scrollIntoView(true);", button_btn_link)
                    # button_btn_link.click()
                    driver.execute_script("arguments[0].click();", button_btn_link)

                    # each accordion_panel_content_item is a match
                    accordion_panel_content_items = driver.find_elements(By.CSS_SELECTOR, '.waf-accordion-panel .content-item')
                    # accordion_panel_content_items = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.content-item')))
                    for match in accordion_panel_content_items:
                        # Extract details for Wrestler A
                        wrestler_a = match.find_element(By.CSS_SELECTOR, 'div.card-item.card-a')
                        name_a = wrestler_a.find_element(By.CSS_SELECTOR, 'span.card-label').text.strip().title()
                        image_a = wrestler_a.find_element(By.CSS_SELECTOR, 'img').get_attribute('src')
                        score_a = wrestler_a.find_element(By.CSS_SELECTOR, 'div.card-number').text.strip()

                        # Extract details for Wrestler B
                        wrestler_b = match.find_element(By.CSS_SELECTOR, 'div.card-item.card-b')
                        name_b = wrestler_b.find_element(By.CSS_SELECTOR, 'span.card-label').text.strip().title()
                        image_b = wrestler_b.find_element(By.CSS_SELECTOR, 'img').get_attribute('src')
                        score_b = wrestler_b.find_element(By.CSS_SELECTOR, 'div.card-number').text.strip()

                        # watch match url:

                        # Extract match result
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
                            'tournament_weight_class': tournament_weight_class,
                        }
                        # print(f'Athlete number {row_index}')
                        # print(match_information)
                        match_result_list.append(match_information)
    finally:
        # Close the browser after all athletes are processed
        driver.quit()

    # convert match_result_list to df
    df = pd.DataFrame(match_result_list)
    df.to_csv('data/matches.csv', index=False)




if __name__ == "__main__":
    scrape_results()