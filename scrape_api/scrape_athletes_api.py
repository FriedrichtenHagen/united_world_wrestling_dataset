import requests
import pandas as pd
from datetime import datetime

# https://uww.org/apiv3/getrankinglist/api/rankings/current/seniors/fs/86?page=3

def scrape_athletes():
    wrestling_style_acronyms = ['fs', 'gr', 'ww']
    freestyle_weight_classes = [57, 61, 65, 70, 74, 79, 86, 92, 97, 124]
    greco_roman_weight_classes = [55, 60, 63, 67, 72, 77, 82, 87, 97, 130]
    womens_wrestling_weight_classes = [50, 53, 55, 57, 59, 62, 65, 68, 72, 76]
    
    all_athlete_listings = []

    for wrestling_style_acronym in wrestling_style_acronyms:
        print(wrestling_style_acronym)

        if wrestling_style_acronym == 'fs':
            current_weight_classes = freestyle_weight_classes
        elif wrestling_style_acronym == 'gr':
            current_weight_classes = greco_roman_weight_classes
        elif wrestling_style_acronym == 'ww':
            current_weight_classes = womens_wrestling_weight_classes
        for current_weight_class in current_weight_classes:
            url = f"https://uww.org/apiv3/getrankinglist/api/rankings/current/seniors/{wrestling_style_acronym}/{current_weight_class}"

            # Make the API call
            response = requests.get(url)

            # Check if the request was successful
            if response.status_code == 200:
                # Parse the JSON response
                data = response.json()
                
                # Extract the 'items' from the 'content' key
                items = data.get("content", {}).get("hydramember", [])
                # add event items to list
                all_athlete_listings.extend(items)

            else:
                print(f"Failed to retrieve data: {response.status_code}")


    # Convert the 'items' list into a DataFrame
    df = pd.json_normalize(all_athlete_listings)
    # Display the DataFrame
    print(df.head())
    df.to_csv('data/athletes.csv', index=False)
    print(f"CSV file has been created with {df.shape[0]} rows")


if __name__ == "__main__":
    scrape_athletes()