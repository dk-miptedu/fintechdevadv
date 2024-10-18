import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '..', 'src')
sys.path.append(src_dir)

import unittest
from aiogram.types import ReplyKeyboardMarkup
from main_menu.MenuStructure import generate_menu, get_terminal_points, find_parent_key, all_integers, sorted_list, menu_structure, COMEBACK_BTN


class TestMenuStructure(unittest.TestCase):
    
    def test_generate_menu_main(self):
        # Test case for the main menu
        result = generate_menu("main_menu")
        self.assertIsInstance(result, ReplyKeyboardMarkup)
        self.assertEqual(len(result.keyboard[0]), 3)  # 3 buttons in main_menu
        self.assertEqual(result.keyboard[0][0].text, "Банк-Крипто")  # Accessing .text instead of ['text']
    
    def test_generate_menu_submenu(self):
        # Test case for a submenu
        result = generate_menu("Банк-Крипто")
        self.assertIn(COMEBACK_BTN, [button.text for button in result.keyboard[0]])  # Accessing .text instead of ['text']
    
    def test_get_terminal_points(self):
        # Test case for terminal points
        terminal_points = get_terminal_points(menu_structure, "main_menu")
        self.assertIn("Купить за RUB", terminal_points)
        self.assertIn("Список продавцов", terminal_points)
        self.assertNotIn("Банк-Крипто", terminal_points)  # It should not be a terminal point
    
    def test_find_parent_key(self):
        # Test case for finding a parent key
        self.assertEqual(find_parent_key(menu_structure, "Купить за RUB"), "Банк-Крипто")
        self.assertEqual(find_parent_key(menu_structure, "Криптобиржи"), "Списки активов")
    
    def test_all_integers(self):
        # Test cases for all_integers function
        self.assertTrue(all_integers(["1", "2", "3"]))
        self.assertFalse(all_integers(["1", "a", "3"]))
    
    def test_sorted_list(self):
        # Test case for sorted_list function
        data = ["item:5,other", "item:3,other", "item:9,other"]
        sorted_data = sorted_list(data, reverse=True)
        self.assertEqual(sorted_data[0], "item:9,other")
        sorted_data_asc = sorted_list(data, reverse=False)
        self.assertEqual(sorted_data_asc[0], "item:3,other")

if __name__ == "__main__":
    unittest.main(verbosity=2)
