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

#pluginplay
import pluginplay as pp
import pluginplay_examples as ppe
from pluginplay_examples import PointCharge, ElectricField, Force


class TestTreeManager(unittest.TestCase):

    def test_add_node(self):
        #get a new shell
        player = PluginPlayerShell()

        #add a new node with instance routing to the first module from the first plugin
        moduleButton = Button()
        moduleButton.id = '0 0'
        player.tree_manager.add_node(moduleButton)

        #check to see a node was added
        self.assertEquals(len(player.nodes), 1,
                          "No node was added to tree section")

    def test_delete_node(self):
        #get a new shell
        player = PluginPlayerShell()

        #add a new node with instance routing to the first module from the first plugin
        moduleButton = Button()
        moduleButton.id = '0 0'
        player.tree_manager.add_node(moduleButton)

        moduleButton.id = '0'
        player.tree_manager.remove_node(moduleButton)

        #check to see a node was deleted
        self.assertEquals(player.nodes[0], None,
                          "The Node was not set to None after deletion")

        #get a new shell
        player = PluginPlayerShell()

        #add new nodes with instances routing to the first, second, and third module from the first plugin
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

        #delete the middle second node
        moduleButton.id = '1'
        player.tree_manager.remove_node(moduleButton)

        #check to see if second node was deleted, the output link of the first node was removed, the input link of the third node was removed
        self.assertEquals(player.nodes[1], None,
                          "The Node was not set to None after deletion")
        self.assertEquals(
            player.nodes[0].output_map[0], [],
            "Output link still exists after its linking node was deleted")
        self.assertEquals(
            player.nodes[2].input_map[0], None,
            "Input link still exists after its linking node was deleted")

    def test_delete_tree(self):
        #get a new shell
        player = PluginPlayerShell()

        #add a new node with instance routing to the first module from the first plugin
        moduleButton = Button()
        moduleButton.id = '0 0'
        player.tree_manager.add_node(moduleButton)

        moduleButton.id = '1 0'
        player.tree_manager.add_node(moduleButton)

        moduleButton.id = '2 0'
        player.tree_manager.add_node(moduleButton)

        moduleButton.id = '3 0'
        player.tree_manager.add_node(moduleButton)

        #remove all nodes in the tree
        player.tree_manager.delete_tree()

        self.assertEquals(player.nodes, [],
                          "There still exists nodes after tree deletion")

    def test_run_tree(self):
        mm = pp.ModuleManager()
        ppe.load_modules(mm)

        force0_mod = mm.at("Classical Force")
        force1_mod = mm.at("Coulomb's Law")
        force2_mod = mm.at("Single-precision Coulomb's law")
        force3_mod = mm.at("Coulomb's Law with screening")

        p0 = [0.0, 0.0, 0.0]
        p1 = [1.0, 0.0, 0.0]
        p2 = [2.0, 0.0, 0.0]
        r0 = [5.5, 0.0, 0.0]
        r1 = [1.5, 0.0, 0.0]
        pc0 = ppe.PointCharge(1.0, p0)
        pc1 = ppe.PointCharge(1.0, p1)
        pc2 = ppe.PointCharge(2.0, p2)
        pcs = [pc1, pc2]
        m1 = 2.0

        force_pt = ppe.Force()
        efield_pt = ppe.ElectricField()

        result0 = force0_mod.run_as(force_pt, pc0, m1, p2, pcs)
        result1 = force1_mod.run_as(efield_pt, p0, pcs)
        result2 = force3_mod.run_as(efield_pt, p0, pcs)
        #get player shell
        player = PluginPlayerShell()

        #add one of each nodes to the tree
        moduleButton = Button()
        moduleButton.id = '0 0'
        player.tree_manager.add_node(moduleButton)

        moduleButton.id = '1 0'
        player.tree_manager.add_node(moduleButton)

        moduleButton.id = '3 0'
        player.tree_manager.add_node(moduleButton)

        #add PointCharge and Force to the list of classes

        backButton = Button()
        backButton.id = '0 0'
        player.utility_manager.custom_declaration_widget.text = 'pluginplay_examples PointCharge'
        #call the new_type function to add it to the list of types
        player.utility_manager.new_type(backButton, player)

        player.utility_manager.custom_declaration_widget.text = 'pluginplay_examples Force'
        #call the new_type function to add it to the list of types
        player.utility_manager.new_type(backButton, player)

        player.utility_manager.custom_declaration_widget.text = 'pluginplay_examples ElectricField'
        #call the new_type function to add it to the list of types
        player.utility_manager.new_type(backButton, player)

        #add in the inputs, set the property types, and submodules

        #---------------------FORCE NODE--------------------------
        moduleButton.id = '-1 0 0 0'
        player.nodes[
            0].custom_declaration_widget.text = 'PointCharge( 1.0, [0.0, 0.0, 0.0])'
        player.node_manager.link_input(moduleButton)

        moduleButton.id = '-1 0 0 1'
        player.nodes[0].custom_declaration_widget.text = '2.0'
        player.node_manager.link_input(moduleButton)

        moduleButton.id = '-1 0 0 2'
        player.nodes[0].custom_declaration_widget.text = '[2.0, 0.0, 0.0]'
        player.node_manager.link_input(moduleButton)

        moduleButton.id = '-1 0 0 0'
        player.nodes[
            0].custom_declaration_widget.text = '[[1.0, 0.0, 0.0], [2.0, 0.0, 0.0]]'
        player.node_manager.link_input(moduleButton)

        moduleButton.id = '0 0 0 3'
        player.node_manager.link_submod(moduleButton)

        #enter Force() into the entry widget
        player.nodes[0].custom_declaration_widget.text = "Force()"

        #link the property type
        moduleButton.id = '0'
        player.node_manager.link_property_type(moduleButton)

        #-----------------Coloumb's law----------------
        moduleButton.id = '-1 0 1 0'
        player.nodes[1].custom_declaration_widget.text = '[0.0, 0.0, 0.0]'
        player.node_manager.link_input(moduleButton)

        moduleButton.id = '-1 0 1 1'
        player.nodes[
            1].custom_declaration_widget.text = '[[1.0, 0.0, 0.0], [2.0, 0.0, 0.0]]'
        player.node_manager.link_input(moduleButton)

        #enter PointCharge() into the entry widget
        player.nodes[1].custom_declaration_widget.text = "ElectricField()"

        #link the property type
        moduleButton.id = '1'
        player.node_manager.link_property_type(moduleButton)

        #-----------------Coloumb's Single-Precesion----------------
        moduleButton.id = '-1 0 2 0'
        player.nodes[2].custom_declaration_widget.text = '[0.0, 0.0, 0.0]'
        player.node_manager.link_input(moduleButton)

        moduleButton.id = '-1 0 2 1'
        player.nodes[
            2].custom_declaration_widget.text = '[[1.0, 0.0, 0.0], [2.0, 0.0, 0.0]]'
        player.node_manager.link_input(moduleButton)

        #enter PointCharge() into the entry widget
        player.nodes[2].custom_declaration_widget.text = "ElectricField()"

        #link the property type
        moduleButton.id = '1'
        player.node_manager.link_property_type(moduleButton)

        #Run the tree
        player.tree_manager.run_tree()

        #Check if the values are the same
        self.assertEquals(result0, player.tree_manager.saved_outputs[0],
                          "Module output did not ran as expected")
        self.assertEquals(result1, player.tree_manager.saved_outputs[1],
                          "Module output did not ran as expected")
        self.assertEquals(result2, player.tree_manager.saved_outputs[2],
                          "Module output did not ran as expected")


if __name__ == "__main__":
    unittest.main()
