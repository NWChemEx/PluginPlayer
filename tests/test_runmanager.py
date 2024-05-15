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

#pluginplay_examples
from pluginplayer_examples import Multiplier


class TestRunManager(unittest.TestCase):
    """Tests the functionality of the run manager"""

    def test_link_input(self):
        """Tests opening the add input button, and adding the inputs needed, checking the module manager that its been set
        """


    def test_link_property_type(self):
        """Tests opening the property type popup, adding a property type, checking that its been saved in the settings
        """
        #get a new shell
        player = PluginPlayerShell()

    def test_link_submod(self):
        """Tests opening the submodule settings, changing property types, verifying they are changed in the module manager"""

        #get a new shell
        player = PluginPlayerShell()

        #add a node
        moduleButton = Button()
        moduleButton.id = '0 0'
        player.tree_manager.add_node(moduleButton)

        moduleButton.id = '0 0 0 3'
        player.node_manager.link_submod(moduleButton)
        
    def test_run(self):
        """Set the inputs, property types, submodules and test a Multiplication tree has a successful run and output
        """


if __name__ == "__main__":
    unittest.main()
