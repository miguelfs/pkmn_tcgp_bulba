import requests
import os
import csv
from bs4 import BeautifulSoup
from datetime import datetime

# Constant for the main link prefix
MAIN_LINK = "https://bulbapedia.bulbagarden.net"

def extract_pokemon_links(html_content):
    """
    Extracts a map of Pokémon numbers and their hyperlinks from a provided HTML content.
    
    Args:
    html_content (str): The HTML content containing the Pokémon table.
    
    Returns:
    dict: A dictionary mapping Pokémon numbers (e.g., '001') to their full hyperlinks.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    pokemon_map = {}

    # Find the specific <table> containing the card list
    table = soup.find('table', {'style': 'display: table; border-collapse: separate; margin-left: -2px; width: calc(100% + 4px)'})
    
    if not table:
        print("Card table not found in the HTML content.")
        return pokemon_map

    rows = table.find_all('tr')[1:]  # Skip the header row
    print('Amount of rows:', len(rows))  # Print the number of rows found

    for row in rows:
        number_cell = row.find('td')
        link_cell = row.find('a', href=True)

        if number_cell and link_cell:
            number = number_cell.text.split('/')[0].strip()  # Get only the Pokémon number
            href = link_cell['href']
            full_link = MAIN_LINK + href
            pokemon_map[number] = full_link

    return pokemon_map


def save_to_csv(data, filepath):
    """
    Saves the given data to a CSV file.
    
    Args:
    data (dict): A dictionary containing Pokémon numbers and their links.
    filepath (str): The file path to save the CSV.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Number', 'Link', 'Added At', 'Did Fetch'])  # Write the header row
        for number, link in data.items():
            added_at = datetime.now().isoformat()
            did_fetch = False
            writer.writerow([number, link, added_at, did_fetch])

if __name__ == "__main__":
    url = "https://bulbapedia.bulbagarden.net/wiki/Genetic_Apex_(TCG_Pocket)"
    response = requests.get(url)

    if response.status_code == 200:
        html_content = response.text
        pokemon_links = extract_pokemon_links(html_content)

        csv_filepath = 'data/main_list.csv'
        save_to_csv(pokemon_links, csv_filepath)

        for number, link in pokemon_links.items():
            print(f"{number}: {link}")
    else:
        print(f"Failed to fetch the page. Status code: {response.status_code}")
