import requests
import os
import csv
from multiprocessing import Pool, cpu_count
from src.functions import *
from src.consts import *

# Constant for the main link prefix

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
