#!/usr/bin/env python3
"""
Script to scrape wheat production data from Wikipedia and save as CSV
"""

import pandas as pd
import requests
from io import StringIO

def scrape_wheat_production_table():
    """
    Scrapes the wheat production table from Wikipedia and saves it as CSV
    """
    url = "https://en.wikipedia.org/wiki/List_of_countries_by_wheat_production"

    print(f"Fetching data from: {url}")

    try:
        # Set a user agent to avoid 403 errors
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Fetch the webpage
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Parse all tables from the page
        tables = pd.read_html(StringIO(response.text))

        print(f"Found {len(tables)} table(s) on the page")

        # The main table is typically the first or largest one
        # Let's find the table with wheat production data
        main_table = None
        for i, table in enumerate(tables):
            # Look for tables with production-related columns
            if any('production' in str(col).lower() or 'tonnes' in str(col).lower()
                   for col in table.columns):
                main_table = table
                print(f"Using table {i} (shape: {table.shape})")
                break

        if main_table is None and len(tables) > 0:
            # If we couldn't find by column name, use the largest table
            main_table = max(tables, key=lambda x: x.shape[0] * x.shape[1])
            print(f"Using largest table (shape: {main_table.shape})")

        if main_table is not None:
            # Clean up column names if needed
            main_table.columns = [str(col).strip() for col in main_table.columns]

            # Save to CSV
            output_file = "wheat_production_data.csv"
            main_table.to_csv(output_file, index=False, encoding='utf-8')

            print(f"\nSuccess! Data saved to '{output_file}'")
            print(f"Table shape: {main_table.shape[0]} rows × {main_table.shape[1]} columns")
            print(f"\nColumn names:")
            for col in main_table.columns:
                print(f"  - {col}")
            print(f"\nFirst few rows:")
            print(main_table.head())

            return main_table
        else:
            print("Error: Could not find any tables on the page")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return None
    except Exception as e:
        print(f"Error processing the data: {e}")
        return None

if __name__ == "__main__":
    scrape_wheat_production_table()
