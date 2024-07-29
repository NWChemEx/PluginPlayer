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

#pluginplay_examples
from pluginplayer_examples import Multiplier


class TestRunManager(unittest.TestCase):
    """Tests the functionality of the run manager"""

    def test_add_input(self):
        """Tests opening the add input button, and adding the inputs needed, checking the module manager that its been set
        """
        player = getShell()

        #set Multiply by 1 as tree's module
        player.tree_manager.tree_module = "Multiply by 1"

        #create button to edit the 1st input of Multiplyby1
        input_button = Button()
        input_button.id = "0 Multiply by 1"

        #create the popup
        player.run_manager.inputs_config()

        #enter the text box for the first input
        player.run_manager.custom_declaration[0].text = "5"

        #link the input
        player.run_manager.add_input(input_button)

        #check if the first input was set
        self.assertEqual(
            player.run_manager.module_dict["Multiply by 1"].
            evaluated_inputs[0], 5, "Did not save the input")

    def test_link_property_type(self):
        """Tests opening the property type popup, adding a property type, checking that its been saved in the settings
        """
        #get a new shell
        player = getShell()

        #open a new popup to view the class types
        player.utility_manager.class_types()

        #set the id for the back button to make a new type
        backButton = Button()
        backButton.id = '0 0'

        #set the type to import
        player.utility_manager.custom_declaration_widget.text = 'pluginplayer_examples Multiplier'

        #call the new_type function to add it to the list of types
        player.utility_manager.new_type(backButton)

        #set Multiply by 1 as tree's module
        player.tree_manager.tree_module = "Multiply by 1"

        #create the popup to enter the property type
        player.run_manager.property_type_config()

        #enter the text box for the property type
        player.run_manager.custom_declaration.text = "Multiplier()"

        #link the property type
        dummy_button = Button()
        player.run_manager.add_property_type(dummy_button)

        #check if the first input was set
        self.assertTrue(
            isinstance(
                player.run_manager.module_dict["Multiply by 1"].
                evaluated_property_type, Multiplier),
            "Did not set property type to Multiplier")

    def test_link_submod(self):
        """Tests opening the submodule settings, changing property types, verifying they are changed in the module manager"""
        player = getShell()

        #set the Multiply by Submods module as the current module being used in the tree
        player.tree_manager.tree_module = "Multiply by Submods"

        map_button = Button()
        map_button.id = "Multiply by Submods"

        #open the popup to select which submodule to map
        player.run_manager.submods_config(map_button)

        #select the first submodule to map
        map_button.id = "0 Multiply by 2"
        player.run_manager.select_submod(map_button)

        #say you want to map the first submodule to Multiply by 2, the second module within the first plugin
        map_button.id = "0 0 1 Multiply by Submods"
        player.run_manager.add_submod(map_button)

        #check that the submodules are set
        self.assertTrue(
            player.mm.at("Multiply by Submods").submods()
            ['internal multiplier 1'].has_name(),
            "Did not set a submodule in the module manager")
        #check that the submodule is set correctly
        self.assertEqual(
            player.mm.at("Multiply by Submods").submods()
            ['internal multiplier 1'].get_name(), "Multiply by 2",
            "Did not set the submodule to Multiply by 2")

    def test_run(self):
        """Set the inputs, property types, submodules and test a Multiplication tree has a successful run and output
        """

        player = getShell()

        #Manually enter property types, inputs, and submodules to isolate testing on the run functionality

        #set submodules to create the function ((x * 2) * (x *1))
        player.mm.change_submod("Multiply by Submods", "internal multiplier 1",
                                "Multiply by 2")
        player.mm.change_submod("Multiply by Submods", "internal multiplier 2",
                                "Multiply by 1")

        #set input to 10
        player.run_manager.module_dict["Multiply by Submods"].inputs[0] = "5"
        player.run_manager.module_dict["Multiply by Submods"].evaluated_inputs[
            0] = 5
        player.mm.at("Multiply by Submods").change_input("r", 5)

        #Set property type
        player.run_manager.module_dict[
            "Multiply by Submods"].property_type = "Multiplier()"
        player.run_manager.module_dict[
            "Multiply by Submods"].evaluated_property_type = Multiplier()

        #set the module as the currently used module
        player.tree_manager.tree_module = "Multiply by Submods"

        #run that puppy
        player.run_manager.run()

        #grab the last message log
        last_message_log = player.root.ids.message_label.text.splitlines()[-1]

        #check if its correct (5 * (5 * 2)) = 50
        self.assertEqual(last_message_log, "Output: 50",
                         "Incorrect output message, did not run successfully")


if __name__ == "__main__":
    unittest.main()
