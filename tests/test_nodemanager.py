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
from pluginplay_examples import Force


class TestNodeManager(unittest.TestCase):

    def test_link_input(self):
        #get a new shell
        player = PluginPlayerShell.get_shell(self)

        #add new nodes with instances routing to the first, second, and third module from the first plugin
        moduleButton = Button()
        moduleButton.id = '0 0'
        player.tree_manager.add_node(moduleButton)

        moduleButton.id = '1 0'
        player.tree_manager.add_node(moduleButton)

        moduleButton.id = '2 0'
        player.tree_manager.add_node(moduleButton)

        #link the output of the first node to the first input of the second node
        moduleButton.id = '0 0 1 0'
        player.node_manager.link_input(moduleButton)

        #link the output of the second node to the first input of the third node
        moduleButton.id = '1 0 2 0'
        player.node_manager.link_input(moduleButton)

        #check if the inputs and outputs are set
        self.assertEquals(player.nodes[1].output_map[0], [(2, 0)],
                          "The node's output map was not set correctly")
        self.assertEquals(player.nodes[1].input_map[0], (0, 0),
                          "The node's input map was not set correctly")
        self.assertEquals(player.nodes[0].output_map[0], [(1, 0)],
                          "The node's output map was not set correctly")
        self.assertEquals(player.nodes[2].input_map[0], (1, 0),
                          "The node's input map was not set correctly")

        #link the first output of the second node to the second input of the third node
        moduleButton.id = '1 0 2 1'
        player.node_manager.link_input(moduleButton)

        #check that the output is mapped to two places
        self.assertEquals(
            player.nodes[1].output_map[0], [(2, 0), (2, 1)],
            "The node's second output was not tracked in the output map")
        self.assertEquals(player.nodes[2].input_map[1], (1, 0),
                          "The node's input map was not set correctly")

        #change the first input of the third node, to map from the first output of the first node
        moduleButton.id = '0 0 2 0'
        player.node_manager.link_input(moduleButton)

        #check that the new and previous output and inputs are correctly editted
        self.assertEquals(player.nodes[0].output_map[0], [(1, 0), (2, 0)],
                          "The node's output map was not correctly editted")
        self.assertEquals(
            player.nodes[1].output_map[0], [(2, 1)],
            "The node's output was correctly editted after a replacement")
        self.assertEquals(
            player.nodes[2].input_map[0], (0, 0),
            "The node's input map was not set after a replacement")

    def test_link_property_type(self):
        #get a new shell
        player = PluginPlayerShell.get_shell(self)

        #add a node
        moduleButton = Button()
        moduleButton.id = '0 0'
        player.tree_manager.add_node(moduleButton)

        #set the id for the back button
        backButton = Button()
        backButton.id = '0 0'

        player.utility_manager.custom_declaration_widget.text = 'pluginplay_examples Force'

        #call the new_type function to add it to the list of types
        player.utility_manager.new_type(backButton, player)

        #enter Force() into the entry widget
        player.nodes[0].custom_declaration_widget.text = "Force()"

        #link the property type
        moduleButton.id = '0'
        player.node_manager.link_property_type(moduleButton)

        self.assertNotEquals(player.nodes[0].property_type, None,
                             "Property Type was not set")

    def test_link_submod(self):

        #get a new shell
        player = PluginPlayerShell.get_shell(self)

        #add a node
        moduleButton = Button()
        moduleButton.id = '0 0'
        player.tree_manager.add_node(moduleButton)

        moduleButton.id = '0 0 0 3'
        player.node_manager.link_submod(moduleButton)


if __name__ == "__main__":
    unittest.main()
