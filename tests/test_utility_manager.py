#stop automatic kivy methods
from kivy.config import Config
# Set Kivy to dummy backend to prevent window creation
Config.set('graphics', 'backend', 'dummy')

# test_pluginplayer.py
import unittest
from pluginplayer_shell import PluginPlayerShell

#kivy button for instance
from kivy.uix.button import Button

#pluginplay_example types
from pluginplay_examples import PointCharge


import sys

class TestutilityManager(unittest.TestCase):

    def test_class_types(self):
        #get a new shell
        player = PluginPlayerShell.get_shell(self)



    def test_new_type(self):
        #get a new shell
        player = PluginPlayerShell.get_shell(self)
        
        #set the id for the back button
        backButton = Button()
        backButton.id = '0 0'

        player.utility_manager.custom_declaration_widget.text = 'pluginplay_examples PointCharge'
        
        #call the new_type function to add it to the list of types
        player.utility_manager.new_type(backButton, player)

        assert hasattr(sys.modules['__main__'], PointCharge.__name__), f"{PointCharge.__name__} doesn't exist in the main module after attempted import."
        self.assertEquals(player.utility_manager.imported_classes[0], "PointCharge", "Did not add to listed imported class types")

if __name__ == "__main__":
    unittest.main()
