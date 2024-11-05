import requests
import os
import csv
from bs4 import BeautifulSoup
from datetime import datetime
from multiprocessing import Pool, cpu_count

# Constant for the main link prefix
MAIN_LINK = "https://bulbapedia.bulbagarden.net"

def links_list_metadata(html_content):
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

def extract_pkmn_links():
    url = "https://bulbapedia.bulbagarden.net/wiki/Genetic_Apex_(TCG_Pocket)"
    response = requests.get(url)
    pokemon_links = []

    if response.status_code == 200:
        html_content = response.text
        pokemon_links = links_list_metadata(html_content)

        csv_filepath = 'data/main_list.csv'
        save_to_csv(pokemon_links, csv_filepath)

        for number, link in pokemon_links.items():
            print(f"{number}: {link}")
    else:
        print(f"Failed to fetch the page. Status code: {response.status_code}")
    return pokemon_links


def extract_each_pkmn_metadata(url):
    """
    Extracts metadata for a Pokémon card from a given URL.
    
    Args:
    url (str): The URL of the Pokémon card page.
    
    Returns:
    dict: A dictionary containing the card's metadata.
    """
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch the page. Status code: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    metadata = {}

    # Extracting name
    name_tag = soup.find('div', class_='infobox-title-en')
    metadata['Name'] = name_tag.text.strip() if name_tag else 'N/A'

    # Extracting HP
    hp_row = soup.find('th', string='HP')
    metadata['HP'] = hp_row.find_next('td').text.strip() if hp_row else 'N/A'

    # Extracting Type
    type_row = soup.find('th', string='Type')
    metadata['Type'] = type_row.find_next('td').text.strip() if type_row else 'N/A'

    # Extracting image link
    image_tag = soup.find('a', class_='image')
    metadata['Image Link'] = image_tag['href'] if image_tag else 'N/A'

    # Extracting weaknesses
    weaknesses_section = soup.find('div', string='weakness')
    if weaknesses_section:
        weakness_img = weaknesses_section.find_next('img')
        metadata['Weakness'] = weakness_img['alt'] if weakness_img else 'N/A'

    # Extracting attack details
    attack_divs = soup.find_all('div', class_='roundy', style='display: flow-root; border: 2px solid #106C2F; background-color: #6AC588; max-width: 500px')
    metadata['Attacks'] = []
    for attack_div in attack_divs:
        attack_info = {
            'Name': attack_div.find('div', style='flex: 1').text.strip() if attack_div.find('div', style='flex: 1') else 'N/A',
            'Damage': attack_div.find('div', style='flex: 0 0 50px; font-size: 1.25rem').text.strip() if attack_div.find('div', style='flex: 0 0 50px; font-size: 1.25rem') else 'N/A',
            'Description': attack_div.find('div', lang='ja').text.strip() if attack_div.find('div', lang='ja') else 'N/A',
            'Energy Required': [img['alt'] for img in attack_div.find_all('img') if 'alt' in img.attrs]
        }
        metadata['Attacks'].append(attack_info)

    print(metadata)
    return metadata

# def write_metadata(metadata, pkmn):
#     """
#     Writes the metadata of a Pokémon to a CSV file.
#
#     Args:
#     metadata (dict): The metadata dictionary for a Pokémon card.
#     pkmn (str): The Pokémon number.
#     """
#     csv_filepath = 'data/metadata_list.csv'
#     os.makedirs(os.path.dirname(csv_filepath), exist_ok=True)
#
#     # Check if the CSV file exists to determine if we need to write the header
#     write_header = not os.path.isfile(csv_filepath)
#
#     with open(csv_filepath, mode='a', newline='', encoding='utf-8') as file:
#         writer = csv.writer(file)
#
#         # Write header if the file is being created for the first time
#         if write_header:
#             writer.writerow(['Number', 'Name', 'HP', 'Type', 'Image Link', 'Weakness', 'Attacks'])
#
#         # Convert attack details into a string format for CSV storage
#         attack_details = "; ".join(
#             f"{attack['Name']} (Damage: {attack['Damage']}, Description: {attack['Description']}, Energy: {', '.join(attack['Energy Required'])})"
#             for attack in metadata.get('Attacks', [])
#         )
#
#         # Write the metadata row
#         writer.writerow([
#             pkmn,
#             metadata.get('Name', 'N/A'),
#             metadata.get('HP', 'N/A'),
#             metadata.get('Type', 'N/A'),
#             MAIN_LINK + metadata.get('Image Link', 'N/A') if metadata.get('Image Link', 'N/A') != 'N/A' else 'N/A',
#             metadata.get('Weakness', 'N/A'),
#             attack_details
#         ])

def write_metadata(metadata_list):
    """
    Writes multiple metadata dictionaries to a CSV file.
    
    Args:
    metadata_list (list): A list of tuples containing the Pokémon number and its metadata.
    """
    csv_filepath = 'data/metadata_list.csv'
    os.makedirs(os.path.dirname(csv_filepath), exist_ok=True)
    
    # Check if the CSV file exists to determine if we need to write the header
    write_header = not os.path.isfile(csv_filepath)
    
    with open(csv_filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Write header if the file is being created for the first time
        if write_header:
            writer.writerow(['Number', 'Name', 'HP', 'Type', 'Image Link', 'Weakness', 'Attacks'])
        
        for pkmn, metadata in metadata_list:
            # Convert attack details into a string format for CSV storage
            attack_details = "; ".join(
                f"{attack['Name']} (Damage: {attack['Damage']}, Description: {attack['Description']}, Energy: {', '.join(attack['Energy Required'])})"
                for attack in metadata.get('Attacks', [])
            )
            
            # Write the metadata row
            writer.writerow([
                pkmn,
                metadata.get('Name', 'N/A'),
                metadata.get('HP', 'N/A'),
                metadata.get('Type', 'N/A'),
                MAIN_LINK + metadata.get('Image Link', 'N/A') if metadata.get('Image Link', 'N/A') != 'N/A' else 'N/A',
                metadata.get('Weakness', 'N/A'),
                attack_details
            ])

def extract_metadata_parallel(pokemon_links):
    """
    Extracts metadata for multiple Pokémon in parallel using multiprocessing.
    
    Args:
    pokemon_links (dict): A dictionary mapping Pokémon numbers to their page links.
    
    Returns:
    list: A list of tuples containing the Pokémon number and its metadata.
    """
    with Pool(cpu_count()) as pool:
        results = pool.starmap(extract_each_pkmn_metadata, [(link,) for link in pokemon_links.values()])
    
    return [(pkmn, metadata) for pkmn, metadata in zip(pokemon_links.keys(), results) if metadata]

if __name__ == "__main__":
    pkmns = extract_pkmn_links()
    if pkmns:
        metadata_list = extract_metadata_parallel(pkmns)
        write_metadata(metadata_list)
        # metadata = extract_each_pkmn_metadata(link)
        # write_metadata(metadata, pkmn)
