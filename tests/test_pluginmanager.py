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
from pluginplayer_shell import PluginPlayerShell

#kivy button for instance
from kivy.uix.button import Button


class TestPluginManager(unittest.TestCase):

    def test_plugin_import_from_shell(self):
        """Tests the manual loading of a module
        """
        #get a new shell
        player = PluginPlayerShell()

        #check if plugin is loaded
        self.assertEqual(
            len(player.plugin_manager.saved_plugins), 1,
            "Failed to import pluginplay examples through test shell")
        
        #check if the module dictionary has been loaded
        self.assertEqual(
            len(player.run_manager.module_dict), 3, 
            "Failed to load pluginplayer_examples's three modules in the module dictionary"
        )

    def test_delete_plugins(self):
        """Test deleting of a plugin
        """
        #get a new shell
        player = PluginPlayerShell()

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
        
    def test_clone(self):
        """Test cloning of a module
        """
        


if __name__ == "__main__":
    unittest.main()
