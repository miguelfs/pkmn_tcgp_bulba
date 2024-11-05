
import unittest
from unittest.mock import patch, mock_open, MagicMock
from src.functions import *
from src.consts import MAIN_LINK

class TestFunctions(unittest.TestCase):

    @patch('functions.BeautifulSoup')
    def test_links_list_metadata(self, mock_soup):
        # Mocking BeautifulSoup and its behavior
        mock_table = MagicMock()
        mock_row = MagicMock()
        mock_row.find.return_value = MagicMock(text='001/226')
        mock_row.find_all.return_value = [mock_row]
        mock_table.find_all.return_value = [mock_row]
        mock_soup.return_value.find.return_value = mock_table
        
        html_content = '<html></html>'  # Placeholder HTML content
        result = links_list_metadata(html_content)
        
        expected_result = {'001': f"{MAIN_LINK}/wiki/Bulbasaur_(Genetic_Apex_1)"}
        self.assertEqual(result, expected_result)

    @patch('builtins.open', new_callable=mock_open)
    def test_save_to_csv(self, mock_file):
        data = {'001': f"{MAIN_LINK}/wiki/Bulbasaur_(Genetic_Apex_1)"}
        save_to_csv(data, 'test.csv')
        
        mock_file().write.assert_called()  # Check that write was called

    @patch('functions.requests.get')
    @patch('functions.BeautifulSoup')
    def test_extract_each_pkmn_metadata(self, mock_soup, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = '<html></html>'
        
        # Mocking metadata extraction
        mock_soup.return_value.find.side_effect = [
            MagicMock(text='Bulbasaur'),  # Name
            MagicMock(),  # HP row
            MagicMock(text='60'),  # HP value
            MagicMock(),  # Type row
            MagicMock(text='Grass'),  # Type value
            MagicMock()  # Image tag
        ]
        
        url = f"{MAIN_LINK}/wiki/Bulbasaur_(Genetic_Apex_1)"
        result = extract_each_pkmn_metadata(url)
        
        expected_result = {
            'Name': 'Bulbasaur',
            'HP': '60',
            'Type': 'Grass',
            'Image Link': 'N/A',
            'Weakness': 'N/A',
            'Attacks': []
        }
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()
