import requests
import pandas as pd
from datetime import datetime

# https://uww.org/apiv4/eventlisting?start_date=2015-01-01&end_date=2015-12-31

# 2014 - 2024
def scrape_events():
    start_year = 2014
    end_year = datetime.now().year
    year_difference = end_year - start_year
    print(year_difference)
    event_from_all_years = []

    for i in range(year_difference + 1):
        current_year = start_year + i
        print(current_year)

        # Define the URL for the API
        url = f"https://uww.org/apiv4/eventlisting?start_date={current_year}-01-01&end_date={current_year}-12-31"

        # Make the API call
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            
            # Extract the 'items' from the 'content' key
            items = data.get("content", {}).get("items", [])
            # add event items to list
            event_from_all_years.extend(items)

        else:
            print(f"Failed to retrieve data: {response.status_code}")


    # Convert the 'items' list into a DataFrame
    df = pd.json_normalize(event_from_all_years)
    # Display the DataFrame
    print(df.head())
    df.to_csv('data/events.csv', index=False)
    print(f"CSV file has been created with {df.shape[0]} rows")


if __name__ == "__main__":
    scrape_events()