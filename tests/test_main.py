
import unittest
from unittest.mock import patch, MagicMock, mock_open
from src.main import *
from src.consts import MAIN_LINK

class TestMain(unittest.TestCase):

    @patch('main.requests.get')
    def test_extract_pkmn_links(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = '<html></html>'
        
        with patch('main.links_list_metadata', return_value={'001': f"{MAIN_LINK}/wiki/Bulbasaur_(Genetic_Apex_1)"}):
            result = extract_pkmn_links()
            self.assertEqual(result, {'001': f"{MAIN_LINK}/wiki/Bulbasaur_(Genetic_Apex_1)"})

    @patch('main.extract_each_pkmn_metadata', return_value={'Name': 'Bulbasaur', 'HP': '60', 'Type': 'Grass'})
    @patch('main.csv.writer')
    @patch('builtins.open', new_callable=mock_open)
    def test_write_metadata(self, mock_file, mock_writer, mock_extract_metadata):
        metadata_list = [('001', {'Name': 'Bulbasaur', 'HP': '60', 'Type': 'Grass'})]
        write_metadata(metadata_list)
        
        mock_file().write.assert_called()  # Check that the CSV write was invoked

if __name__ == '__main__':
    unittest.main()
