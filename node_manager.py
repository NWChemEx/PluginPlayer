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

#kivy helpers
from kivy.graphics import Line
from kivy.uix.widget import Widget
from kivy.graphics import Color

#system's classes
import sys


#helper class for the PluginPlayer application handling the linking of inputs, outputs, submodules, and property types of modules
class NodeManager():

    def __init__(self, plugin_player):
        self.plugin_player = plugin_player

    def link_input(self, instance):
        #get info from instance id
        output_node_number = int(instance.id.split()[0])
        output_number = int(instance.id.split()[1])
        input_node_number = int(instance.id.split()[2])
        input_number = int(instance.id.split()[3])
        input_node = self.plugin_player.nodes[input_node_number]
        input_key = list(input_node.input_dict.keys())[input_number]

        #check if input was previously set and wasn't a custom value
        if input_node.input_map[input_number] and input_node.input_map[
                input_number][0] != -1:
            #find previous output
            previous_output_node_number = input_node.input_map[input_number][0]
            previous_output_number = input_node.input_map[input_number][1]
            previous_output_node = self.plugin_player.nodes[
                previous_output_node_number]
            previous_output_key = list(previous_output_node.output_dict.keys()
                                       )[previous_output_number]

            #delete old lines connecting to the input node
            for line_set in input_node.module_widget.incoming_lines:
                if line_set[1] == (previous_output_node_number,
                                   previous_output_number):
                    input_node.module_widget.incoming_lines.remove(line_set)
                    self.plugin_player.root.ids.right_section.ids.tree_section.canvas.before.remove(
                        line_set[0])

            #delete old lines connecting to the output node
            for line_set in previous_output_node.module_widget.outgoing_lines:
                if line_set[1] == (input_node_number, input_number):
                    previous_output_node.module_widget.outgoing_lines.remove(
                        line_set)
                    self.plugin_player.root.ids.right_section.ids.tree_section.canvas.before.remove(
                        line_set[0])

            #remove the previous output edge
            previous_output_node.output_map[previous_output_number].remove(
                (input_node_number, input_number))
            self.plugin_player.add_message(
                f"Removed input {input_key} of Node {input_node_number} to {previous_output_key} from Node {previous_output_node_number}"
            )

        #load in a custom input
        if output_node_number == -1:

            #grab remaining values
            input_node = self.plugin_player.nodes[input_node_number]
            input_key = list(input_node.input_dict.keys())[input_number]

            #grab input from currently opened popup entry
            custom_declaration = input_node.custom_declaration_widget.text

            #try to assign the variable
            #may be a security risk as it evaluates injected code
            # TODO: find eval alternative
            try:
                custom_input = eval(custom_declaration,
                                    sys.modules['__main__'].__dict__)
                input_node.input_map[input_number] = (-1, custom_input,
                                                      custom_declaration)
                self.plugin_player.add_message(
                    f"Set input {input_key} of Node {input_node_number} with Value: {custom_declaration}"
                )
            except Exception as e:
                self.plugin_player.add_message(
                    f"Could not set input {custom_declaration}: {e}")

        #set a new edge and input route
        else:
            #get remaining information
            output_node = self.plugin_player.nodes[output_node_number]
            output_key = list(output_node.output_dict.keys())[output_number]

            #set the edges of the nodes
            output_node.output_map[output_number].append(
                (input_node_number, input_number))
            input_node.input_map[input_number] = (output_node_number,
                                                  output_number)

            #add a line connecting the nodes
            connecting_line = Line(points=[
                input_node.module_widget.x + 50,
                input_node.module_widget.y + 50,
                output_node.module_widget.x + 50,
                output_node.module_widget.y + 50
            ],
                                   width=2)
            input_node.module_widget.incoming_lines.append(
                (connecting_line, (output_node_number, output_number)))
            output_node.module_widget.outgoing_lines.append(
                (connecting_line, (input_node_number, input_number)))
            #add the line to the layout
            self.plugin_player.root.ids.right_section.ids.tree_section.canvas.before.add(
                Color(0, 0, 0))
            self.plugin_player.root.ids.right_section.ids.tree_section.canvas.before.add(
                connecting_line)
            #display message
            self.plugin_player.add_message(
                f"Set input {input_key} of Node {input_node_number} to {output_key} from Node {output_node_number}"
            )

        #go back to view_config
        temp_widget = Widget()
        temp_widget.id = f'{input_node_number}'
        self.plugin_player.node_widget_manager.view_config(temp_widget)

    #attempts to add a property type to a node
    def link_property_type(self, instance):

        #grab info from the instance id and text entry
        node_number = int(instance.id)
        node = self.plugin_player.nodes[node_number]
        custom_declaration = node.custom_declaration_widget.text

        #try to assign the variable
        #may be a security risk as it evaluates injected code
        # TODO: find eval alternative
        try:
            ptype = eval(custom_declaration, sys.modules['__main__'].__dict__)
            node.property_type = (custom_declaration, ptype)
            self.plugin_player.add_message(
                f"Set property type of Node {node_number} with Value: {custom_declaration}"
            )
        except Exception as e:
            self.plugin_player.add_message(
                f"Could not set property type {custom_declaration}: {e}")
        self.plugin_player.node_widget_manager.view_config(instance)

    #attempts to add a submodule type to a node
    def link_submod(self, instance):

        #get info from the instance id
        node_number = int(instance.id.split()[0])
        node = self.plugin_player.nodes[node_number]
        module_name = node.module_name
        key_number = int(instance.id.split()[1])
        key_name = list(node.submod_dict.keys())[key_number]
        plugin_number = int(instance.id.split()[2])
        submodule_number = int(instance.id.split()[3])
        submodule_name = self.saved_plugins[plugin_number].modules[
            submodule_number]

        try:
            self.plugin_player.mm.change_submod(module_name, key_name,
                                                submodule_name)
            self.plugin_player.add_message(
                f"Added submodule {submodule_name} to {key_name} of {module_name}"
            )
            node.submod_map[key_number] = (key_name, submodule_name)
        except Exception as e:
            self.plugin_player.add_message(
                f"Could not add submodule {submodule_name} to {key_name} of {module_name}\n {e}"
            )

        #go back to view_config
        temp_widget = Widget()
        temp_widget.id = f'{node_number}'
        self.plugin_player.node_widget_manager.view_config(temp_widget)
