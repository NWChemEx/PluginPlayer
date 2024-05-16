# Copyright 2024 NWChemEx-Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#stop automatic kivy methods
from kivy.config import Config
# Set Kivy to dummy backend to prevent window creation
Config.set('graphics', 'backend', 'dummy')

# test_pluginplayer.py
import unittest
from pluginplayer_shell import getShell, getShellNoLoading
from pluginplay import Module

#kivy button for instance
from kivy.uix.button import Button


class TestPluginManager(unittest.TestCase):
    """Tests the functionality of the plugin_manager class"""

    def test_plugin_import_from_shell(self):
        """Tests the manual loading of a module
        """
        #get a new shell
        player = getShell()

        #check if plugin is loaded
        self.assertEqual(
            len(player.plugin_manager.saved_plugins), 1,
            "Failed to import pluginplay examples through test shell")
        
        #check if the module dictionary has been loaded
        self.assertEqual(
            len(player.run_manager.module_dict), 3, 
            "Failed to load pluginplayer_examples's three modules in the module dictionary"
        )
        self.assertEqual(
            len(player.mm.keys()), 3, "Failed to add modules into the module manager"
        )

    def test_import_plugins(self):
        """Tests the GUI loading of a plugin"""
        
        player = getShellNoLoading()
        
        #enter the class you want to import thats within the python path
        player.root.ids.file_path_input.text = "pluginplayer_examples"
        
        #click the submit button
        player.plugin_manager.plugin_loader()
        
        #check if plugin is loaded
        self.assertEqual(
            len(player.plugin_manager.saved_plugins), 1,
            "Failed to import pluginplay examples through test shell")
        
        #check if the module dictionary has been loaded
        self.assertEqual(
            len(player.run_manager.module_dict), 3, 
            "Failed to load pluginplayer_examples's three modules in the module dictionary"
        )
        self.assertEqual(
            len(player.mm.keys()), 3, "Failed to add modules into the module manager"
        )

        
        
    def test_delete_plugins(self):
        """Test deleting of a plugin
        """

        #get a new shell
        player = getShell()

        #Create button instance to delete the first plugin
        deleteButton = Button()
        deleteButton.id = '0'
        player.plugin_manager.delete_plugin(deleteButton)

        #attempt to delete the first plugin
        self.assertEqual(
            len(player.plugin_manager.saved_plugins), 0,
            "Failed to delete plugin")
        
        #check if the module dictionary has been cleared
        self.assertEqual(
            len(player.run_manager.module_dict), 0, 
            "Failed to delete pluginplayer_examples's three modules from the module dictionary"
        )
        self.assertEqual(
            len(player.mm.keys()), 0, "Failed to delete modules from the module manager"
        )
        
    def test_clone(self):
        """Tests the cloning of a module"""
        
        player = getShell()
        
        #create a button to make a clone of MultiplyBy1, first module of first plugin
        clone_button = Button()
        clone_button.id = "0 0"
        
        #create popup
        player.plugin_manager.duplicate_module(clone_button)
        
        #Set the name of the plugin we want
        player.plugin_manager.custom_declaration.text = "Duplicate"
        
        #Click a submit button, add a 0 to the id as we are not canceling
        clone_button.id = "0 0 0"
        player.plugin_manager.initiate_clone(clone_button)
        
        #Check the module has been imported as a 4th module
        self.assertTrue(isinstance(player.mm.at("Duplicate"), Module), "Did not add the duplicate to the module manager")
        

    
        


if __name__ == "__main__":
    unittest.main()
