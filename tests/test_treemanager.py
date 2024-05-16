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
from pluginplayer_shell import getShell

#kivy button for instance
from kivy.uix.button import Button


class TestTreeManager(unittest.TestCase):
    """Tests the functionality of the tree_manager"""

    def test_tree_building(self):
        """Sets a module to the tree checking its the tree can generate without any errors, doesn't check the visuals, only that there were no errors in tree building
        """
        player = getShell()
        
        #Manually enter submodules to test only tree functionality
        mm = player.mm
        
        #set a button to select to set the 3rd module from the 1st plugin (Multiply by Submods) and create a more complicated tree
        graph_button = Button()
        graph_button.id = "0 2"
        mm.change_submod("Multiply by Submods", "internal multiplier 1", "Multiply by 2")
        mm.change_submod("Multiply by Submods", "internal multiplier 2", "Multiply by 1")
        
        #should be a tree with multiply by submods as its node, on the left connected to a multiply by 2 with a multiply by 1 child, on the right connected to a multiply by 1
        #attempt to set Multiply by Submods into the tree
        player.tree_manager.set_module(graph_button)
        
        #Grab the success message that the module tree was created successfully
        last_message_log = player.root.ids.message_label.text.splitlines()[-1]
        
        self.assertEqual(last_message_log, "Successfully Created Module Tree")
        self.assertEqual(player.tree_manager.tree_module, "Multiply by Submods", "Didn't set the tree module variable")
        self.assertNotEqual(len(player.root.ids.tree_section.children), 0, "Did not add any widgets to the tree")
        self.assertNotEqual(len(player.root.ids.tree_section.canvas.before.children), 0, "Did not add lines")



    def test_delete_tree(self):
        """Check once you press the button to delete the tree, the tree is empty"""
        
        #Create a delete button to remove all widgets from the tree
        player = getShell()
        
        #first generate a basic tree with a line
        graph_button = Button()
        graph_button.id = "0 1"
        player.tree_manager.set_module(graph_button)     
        
        #now remove it
        player.tree_manager.delete_tree() 
        
        #Check if the tree isn't full of widgets or set to anything
        self.assertIsNone(player.tree_manager.tree_module, "Didn't clear the tree module variable")
        self.assertEqual(len(player.root.ids.tree_section.children), 0, "Did not clear all widgets")
        
        #lines still are within the canvas section but are not shown, this cannot be tested without visual confirmation        
        

if __name__ == "__main__":
    unittest.main()
