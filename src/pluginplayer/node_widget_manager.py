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
"""
Building the node's widget
    When building a modular application design, nodes of the tree can be added from the module view, and a node is placed on the tree with the Module’s name and the node number, a series of options buttons, and a configuration button. This node widget building process is done by `NodeWidgetManager` class that imports image files and module settings into a `ModuleNode` class. The `ModuleNode` class contains dictionaries of the inputs, outputs, property type, and submodules required for the run process. 

Button Options 
    Within the options buttons the user to move the node with the navigation button, shown with a four-arrowed icon by dragging. The drag implementation is monitored by the `DraggableImageButton` and `DraggableWidget` class within `NodeWidgetManager` class to track user's touch and drag movements and move the widget based on the mouse location.  The user can access the API information for the Module the node contains by clicking the info button, shown with an “i” icon. The user can also remove the node by clicking the remove button, shown with an X icon. The remove functionality removes all connections in the tree and deletes the node from the tree through the `delete_node` function.

Viewing the node's configuration
    When a user clicks the “Configure” button, a popup will be shown to display the inputs, outputs, and Submodules for the nodes, as well as their connections in the tree if they are set. This popup is build by the `view_config` function within the `NodeManager` class, iterating through the node’s run settings and displaying each value that has been set or left empty. “Set” buttons are also next to each input, property type, and submodule displayed to set their connection in the tree.

Setting a connection
    The “Set” popup is displayed after the user decides to set either an input, property type, or submodule. Viewing the options for setting a run value is handled by the popup builder functions `add_input` and `add_submod` within the `NodeManager` class. Setting a property type requires only a text entry of the function type.

"""
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget


class NodeWidgetManager():
    """Helper class for the PluginPlayer application to build widgets for viewing a module's run configuration

    """

    def __init__(self, plugin_player):
        """Initialization to set the PluginPlayer for which the UtilityManager will be managing

        :param plugin_player: The PluginPlayer object that the UtilityManager will manage
        :type plugin_player: PluginPlayer
        """
        self.plugin_player = plugin_player

    def view_config(self, instance):
        """Open a popup to view the configuration of a module's inputs, outputs, property type, and submodules with options to edit

        :param instance: The button routing to this function
        :type instance: kivy.uix.button.Button
        """

        #attempt to close any popups
        try:
            self.plugin_player.popup.dismiss()
        except:
            pass
        #grab the node's index and its corresponding module
        node_number = int(instance.id)
        node = self.plugin_player.nodes[node_number]
        module = node.module
        module_name = node.module_name

        #create main widget to hold everything
        config_widget = BoxLayout(orientation='vertical',
                                  spacing=10,
                                  size_hint_y=None)
        config_widget.bind(minimum_height=config_widget.setter('height'))

        #add buffer for scrollview
        config_widget.add_widget(Widget(size_hint_y=None, height=100))

        #-------------------------INPUT CONFIGURATION ---------------------

        #create a widget to display the inputs
        input_widget = BoxLayout(orientation='vertical',
                                 spacing=0,
                                 size_hint_y=None)
        input_label = Label(text="Input Configuration",
                            valign='center',
                            halign='center',
                            font_size='20sp',
                            color=(0, 0, 0, 1),
                            size_hint_y=None,
                            height=30)
        input_widget.add_widget(input_label)

        #add each input and a text input to add it
        for i in range(len(node.input_dict.items())):
            #grab the key for the input
            key = list(node.input_dict.keys())[i]
            try:
                value_description = list(
                    node.input_dict.values())[i].description()
            except:
                value_description = "description unavailable"

            #create the box to hold the input's options
            input_list = BoxLayout(orientation='horizontal',
                                   size_hint_y=None,
                                   height=30,
                                   spacing=0)

            #create label for the name of the input
            input_list.add_widget(
                Label(text=key,
                      size_hint_x=1 / 5,
                      halign='left',
                      color=(0, 0, 0, 1)))

            #create label for the description
            input_description = Label(text=f'{value_description}',
                                      halign='left',
                                      color=(0, 0, 0, 1),
                                      size_hint_x=3 / 5)
            input_list.add_widget(input_description)

            #add preselected input if done
            if node.input_map[i]:
                #Show custom input
                if node.input_map[i][0] == -1:
                    input_description.text = f'Set: {node.input_map[i][2]}'
                #Show input route
                else:
                    input_description.text = f'Set: {self.plugin_player.nodes[node.input_map[i][0]].module_name}({node.input_map[i][0]}), Output: {node.input_map[i][1]}'

            #create the add button that routes to an adding input function
            input_add_button = Button(text='Set', size_hint_x=1 / 5)
            input_add_button.id = f'{node_number} {i}'
            input_add_button.bind(on_press=self.add_input)
            input_list.add_widget(input_add_button)

            #add it to main input holder
            input_widget.add_widget(input_list)
        #add to main configuration holder
        config_widget.add_widget(input_widget)

        #---------------------------OUTPUT CONFIGURATION---------------------------------------

        #create a widget to display the outputs
        output_widget = BoxLayout(orientation='vertical',
                                  spacing=0,
                                  size_hint_y=None)
        output_label = Label(text="Output Configuration",
                             valign='center',
                             halign='center',
                             font_size='20sp',
                             color=(0, 0, 0, 1))
        output_widget.add_widget(output_label)

        #add each output and a text output to add it
        for i in range(len(node.output_dict.items())):
            #grab the key for the output
            key = list(node.output_dict.keys())[i]
            try:
                value_description = list(
                    node.output_dict.values())[i].description()
            except:
                value_description = "description unavailable"

            #create the box to hold the output's options
            output_list = BoxLayout(orientation='horizontal',
                                    size_hint_y=None,
                                    height=30,
                                    spacing=0)

            #create label for the name of the output
            output_list.add_widget(
                Label(text=key,
                      size_hint_x=1 / 5,
                      halign='left',
                      color=(0, 0, 0, 1)))

            #create label for output description
            output_description = Label(text=f'{value_description}',
                                       halign='left',
                                       color=(0, 0, 0, 1),
                                       size_hint_x=4 / 5)
            output_list.add_widget(output_description)

            #add preselected output paths if done
            output_edges = "Set: "
            output_set = False
            for output_edge in node.output_map[i]:
                output_set = True
                output_edges += f'{self.plugin_player.nodes[output_edge[0]].module_name}({output_edge[0]}) Input: {output_edge[1]}   '
            if output_set:
                output_description.text = output_edges

            #add it to main output holder
            output_widget.add_widget(output_list)
        #add to main configuration holder
        config_widget.add_widget(output_widget)

        #-----------------------PROPERTY TYPE CONFIGURATION-----------------------------------

        #create a widget to display the property type chosen
        ptype_widget = BoxLayout(orientation='vertical',
                                 spacing=0,
                                 size_hint_y=None)
        ptype_widget.add_widget(
            Label(text="Property Type Configuration",
                  valign='center',
                  halign='center',
                  font_size='20sp',
                  color=(0, 0, 0, 1)))

        #create a label widget showing the current set property type
        if node.property_type == None:
            set_value = "No Property Type Set"
        else:
            set_value = node.property_type[0]
        ptype_widget.add_widget(
            Label(text=set_value, halign='left', color=(0, 0, 0, 1)))

        #create an entry to declare a property type
        custom_ptype = BoxLayout(orientation='horizontal', spacing=0)
        text_entry = TextInput(hint_text="ex: Force()",
                               size_hint_x=3 / 5,
                               multiline=False)

        #add text entry to the node's properties
        node.custom_declaration_widget = text_entry
        custom_ptype.add_widget(text_entry)

        #add button to set the property type
        custom_entry_button = Button(
            text="Set",
            size_hint_x=1 / 5,
            on_press=self.plugin_player.node_manager.link_property_type)

        #add button to view the class types
        class_types_button = Button(
            text="Class Types",
            size_hint_x=1 / 5,
            on_press=lambda instance, *args: self.plugin_player.utility_manager
            .class_types(instance, self.plugin_player))

        #id to trigger the custom input response
        custom_entry_button.id = f'{node_number}'
        class_types_button.id = f'{node_number} {-1}'
        custom_ptype.add_widget(custom_entry_button)
        custom_ptype.add_widget(class_types_button)
        ptype_widget.add_widget(custom_ptype)

        config_widget.add_widget(ptype_widget)

        #-----------------------------SUBMODULE CONFIGURATION--------------------------------

        #create a widget to display the submodules
        submods_widget = BoxLayout(orientation='vertical',
                                   spacing=0,
                                   size_hint_y=None)
        submod_label = Label(text="Submodule Configuration",
                             valign='center',
                             halign='center',
                             font_size='20sp',
                             color=(0, 0, 0, 1))
        submods_widget.add_widget(submod_label)

        #add each submodule and a text input to add it
        for i in range(len(node.submod_dict.items())):
            #grab the key for the submodule
            key = list(node.submod_dict.keys())[i]
            try:
                value_description = list(
                    node.submod_dict.values())[i].description()
            except:
                value_description = "description unavailable"

            #create the box to hold the submod's options
            submod_list = BoxLayout(orientation='horizontal',
                                    size_hint_y=None,
                                    height=30,
                                    spacing=0)

            #create label for the name of the submodule
            submod_list.add_widget(
                Label(text=key,
                      size_hint_x=1 / 5,
                      halign='left',
                      color=(0, 0, 0, 1)))

            #create label for submodule description
            submod_description = Label(text=f'{value_description}',
                                       halign='left',
                                       color=(0, 0, 0, 1),
                                       size_hint_x=3 / 5)
            submod_list.add_widget(submod_description)

            #add preselected submodule if done
            if node.submod_map[i][1]:
                submod_description.text = f'Set: {node.submod_map[i][1]}'

            #create the add button that routes to an adding submodule function
            submod_add_button = Button(text='Set', size_hint_x=1 / 5)
            submod_add_button.id = f'{node_number} {i}'
            submod_add_button.bind(on_press=self.add_submod)
            submod_list.add_widget(submod_add_button)

            #add it to main submodule holder
            submods_widget.add_widget(submod_list)

        #add a "no submodules" label if there are none
        if len(node.submod_dict.items()) == 0:
            submods_widget.add_widget(
                Label(text="No Submodules", halign='left', color=(0, 0, 0, 1)))
        #add to main configuration holder
        config_widget.add_widget(submods_widget)

        #add buffer for scrollview
        config_widget.add_widget(Widget(size_hint_y=None, height=100))

        #add scrolling capabilities
        scroll_view = ScrollView(do_scroll_x=False,
                                 do_scroll_y=True,
                                 scroll_type=['bars'])
        scroll_view.add_widget(config_widget)

        self.plugin_player.create_popup(
            scroll_view, f'Configuration for {module_name} ({node_number})',
            True)
        return

    #attempts to add an entered input
    def add_input(self, instance):
        """Opens a popup to ask a user to add an input. Can add a custom input value or link output from another node.

        :param instance: Button routing to this function
        :type instance: kivy.uix.button.Button
        """
        #grab needed info form the id and
        node_number = int(instance.id.split()[0])
        key_number = int(instance.id.split()[1])
        node = self.plugin_player.nodes[node_number]
        module_name = node.module_name
        key = list(node.input_dict.keys())[key_number]

        #start creating a widget for selecting an input
        select_input = BoxLayout(orientation='vertical',
                                 size_hint=(None, None),
                                 size=(800, 500),
                                 spacing=0)

        #keep track of height for scrolling padding
        height = 0

        #add back button
        back_button = Button(text="Back",
                             size_hint=(None, None),
                             size=(40, 20),
                             on_press=self.view_config)
        back_button.id = f'{node_number}'
        select_input.add_widget(back_button)
        height += 20

        #add an option to declare your own input
        select_input.add_widget(
            Label(text="Declare input value using Python",
                  color=(0, 0, 0, 1),
                  size_hint_y=None,
                  height=20,
                  halign='center'))
        height += 20
        custom_input = BoxLayout(orientation='horizontal',
                                 spacing=0,
                                 size_hint=(None, None),
                                 size=(750, 30))
        text_entry = TextInput(hint_text="ex: Point([-1.0, -1.0, -1.0])",
                               size_hint_x=9 / 10,
                               multiline=False)

        #add text entry to the node's properties
        node.custom_declaration_widget = text_entry
        custom_input.add_widget(text_entry)
        custom_entry_button = Button(
            text="Set",
            size_hint_x=1 / 10,
            on_press=self.plugin_player.node_manager.link_input)

        #id to trigger the custom input response
        custom_entry_button.id = f'{-1} {-1} {node_number} {key_number}'
        custom_input.add_widget(custom_entry_button)

        #add button to import a new class type

        class_types_button = Button(
            text="Class Types",
            size_hint_x=3 / 10,
            on_press=lambda instance, *args: self.plugin_player.utility_manager
            .class_types(instance, self.plugin_player))
        class_types_button.id = f'{node_number} {key_number}'
        custom_input.add_widget(class_types_button)

        select_input.add_widget(custom_input)
        height += 30

        output_node_number = 0
        output_number = 0
        #grab each output in each node on the tree
        for node_iter in self.plugin_player.nodes:

            #ignore deleted nodes and same node
            if not node_iter or node_iter == node:
                output_node_number += 1
                continue

            #add node label
            select_input.add_widget(
                Label(
                    text=f"Node {output_node_number}: {node_iter.module_name}",
                    size_hint_y=None,
                    height=20,
                    halign='left',
                    font_size="15sp",
                    color=(0, 0, 0, 1)))
            height += 30

            output_number = 0
            for output in list(node_iter.output_dict.keys()):
                #create an output with an add button
                output_box = BoxLayout(orientation='horizontal',
                                       size_hint=(None, None),
                                       size=(750, 30),
                                       spacing=0)
                output_box.add_widget(
                    Label(text=output,
                          color=(0, 0, 0, 1),
                          halign='left',
                          size_hint_x=9 / 10))

                add_button = Button(
                    text="Set",
                    size_hint_x=1 / 10,
                    on_press=self.plugin_player.node_manager.link_input)
                #add id to identify the submodule from the node, and the module to be the submodule
                add_button.id = f'{output_node_number} {output_number} {node_number} {key_number}'
                output_box.add_widget(add_button)

                #add to main box
                select_input.add_widget(output_box)
                height += 30
                output_number += 1
            select_input.add_widget(Widget(size_hint_y=None, height=20))
            height += 20
            output_node_number += 1

        #add scrolling capabilities
        if height < 450:
            select_input.add_widget(
                Widget(size_hint_y=None, height=(450 - height)))
        scroll_view = ScrollView(scroll_y=0,
                                 do_scroll_y=True,
                                 size_hint=(None, None),
                                 size=(800, 500),
                                 scroll_type=['content'])
        scroll_view.add_widget(select_input)
        self.plugin_player.popup.dismiss()
        self.plugin_player.popup = None
        self.plugin_player.popup = Popup(content=scroll_view,
                                         size_hint=(None, None),
                                         size=(800, 500),
                                         background_color=(255, 255, 255),
                                         auto_dismiss=False,
                                         title=f'Selecting input: {key}',
                                         title_color=(0, 0, 0, 1))
        self.plugin_player.popup.open()

        return

    def add_submod(self, instance):
        """Opens a popup to prompt a user to select a submodule from the imported modules.

        :param instance: Button routing to the function
        :type instance: kivy.uix.button.Button
        """
        #grab needed info form the id and
        node_number = int(instance.id.split()[0])
        key_number = int(instance.id.split()[1])
        node = self.plugin_player.nodes[node_number]
        module_name = node.module_name
        key = list(node.submod_dict.keys())[key_number]

        #start creating a widget for selecting a submodule
        select_submod = BoxLayout(orientation='vertical',
                                  size_hint=(None, None),
                                  size=(800, 500),
                                  spacing=0)

        #keep track of height for scrolling padding
        height = 0
        #add back button
        back_button = Button(text="Back",
                             size_hint=(None, None),
                             size=(40, 20),
                             on_press=self.view_config)
        back_button.id = f'{node_number}'
        select_submod.add_widget(back_button)
        height += 20

        plugin_number = 0
        module_number = 0
        #for each module in each plugin, place a module and option to add
        for plugin in self.plugin_player.plugin_manager.saved_plugins:

            #continue if the plugin was deleted
            if not plugin:
                continue

            for module in plugin.modules:
                #create a module with an add button
                module_box = BoxLayout(orientation='horizontal',
                                       size_hint=(None, None),
                                       size=(750, 30),
                                       spacing=0)
                module_box.add_widget(
                    Label(text=module,
                          color=(0, 0, 0, 1),
                          halign='left',
                          size_hint_x=9 / 10))

                add_button = Button(
                    text="Set",
                    size_hint_x=1 / 10,
                    on_press=self.plugin_player.node_manager.link_submod)
                #add id to identify the submodule from the node, and the module to be the submodule
                add_button.id = f'{node_number} {key_number} {plugin_number} {module_number}'
                module_box.add_widget(add_button)

                #add to main box
                select_submod.add_widget(module_box)
                height += 30

                module_number += 1
        plugin_number += 1
        module_number = 0

        #add scrolling capabilities
        if height < 450:
            select_submod.add_widget(
                Widget(size_hint_y=None, height=(450 - height)))
        scroll_view = ScrollView(scroll_y=0,
                                 do_scroll_y=True,
                                 size_hint=(None, None),
                                 size=(800, 500),
                                 scroll_type=['content'])
        scroll_view.add_widget(select_submod)

        self.plugin_player.create_popup(scroll_view,
                                        f'Selecting submodule: {key}', False)
