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
from kivy.metrics import dp

import sys


class RunManager():
    """Helper class for the PluginPlayer application to build widgets for viewing a module's run configuration

    """

    def __init__(self, plugin_player):
        """Initialization to set the PluginPlayer for which the UtilityManager will be managing

        :param plugin_player: The PluginPlayer object that the UtilityManager will manage
        :type plugin_player: PluginPlayer
        """
        self.plugin_player = plugin_player
        self.module_dict = {}
        self.custom_declaration = None

    def inputs_config(self):
        """Open a popup to view the configuration of a module's inputs
        """

        #attempt to close any popups
        try:
            self.plugin_player.popup.dismiss()
        except:
            pass
        
        #clear the text entry array
        self.custom_declaration = []
        
        #grab the node's index and its corresponding module
        module_name = self.plugin_player.tree_manager.tree_module
        
        #return with error message if no module is in the tree view
        if(module_name == None):
            self.plugin_player.add_message("Can't configure inputs: No module added to the tree")
            return

        #-------------------------INPUT CONFIGURATION ---------------------

        #create a widget to display the inputs
        input_widget = BoxLayout(orientation='vertical',
                                 spacing=0,
                                 minimum_height=dp(500),
                                 size_hint_y=None)
        input_label = Label(text="Input Configuration",
                            valign='center',
                            halign='center',
                            font_size='20sp',
                            color=(0, 0, 0, 1),
                            size_hint_y=None,
                            height=dp(30))
        input_widget.add_widget(input_label)
        

        #add each input and a text input to add it
        for i in range(len(self.plugin_player.mm.at(module_name).inputs().items())):
            #grab the key for the input
            key = list(self.plugin_player.mm.at(module_name).inputs().keys())[i]
            try:
                value_description = list(
                    self.plugin_player.mm.at(module_name).inputs().values())[i].description()
            except:
                value_description = "description unavailable"

            #create the box to hold the input's options
            input_list = BoxLayout(orientation='horizontal',
                                   size_hint_y=None,
                                   height=dp(30),
                                   spacing=dp(10))

            #create label for the name of the input
            input_list.add_widget(
                Label(text=key,
                      halign='left',
                      size_hint_x = 2/5,
                      color=(0, 0, 0, 1)))

            #create label for the description
            input_description = Label(text=f'{value_description}',
                                      halign='left',
                                      color=(0, 0, 0, 1),
                                      size_hint_x=3 / 5)
            input_list.add_widget(input_description)
            
            #create a horizontal layout for the input boxes and buttons
            input_entry_list = BoxLayout(orientation='horizontal',
                                   size_hint_y=None,
                                   height=dp(30),
                                   spacing=dp(10))

            #add a declaration widget to set the input
            custom_declaration_widget = TextInput(hint_text="ex: [1, 2, 3]",
                                                   size_hint_x=4 / 5,
                                                   multiline=False)
            
            #set preselected input text if already set
            if self.module_dict[module_name].inputs[i]:
                custom_declaration_widget.hint_text = f'Set: {self.module_dict[module_name].inputs[i]}'
                
            input_entry_list.add_widget(custom_declaration_widget)
            self.custom_declaration.append(custom_declaration_widget)

            #create the add button that routes to an adding input function
            input_add_button = Button(text='Set', size_hint_x=1 / 5)
            input_add_button.id = f'{i} {module_name}'
            input_add_button.bind(on_press=self.add_input)
            input_entry_list.add_widget(input_add_button)

            #add it to main input holder
            input_widget.add_widget(input_list)
            input_widget.add_widget(input_entry_list)
            
        
        #add scrolling capabilities
        scroll_view = ScrollView(do_scroll_x=False,
                                 do_scroll_y=True,
                                 scroll_y=0,
                                 scroll_type=['bars'])
        scroll_view.add_widget(input_widget)

        self.plugin_player.create_popup(
            scroll_view, f'Input Configuration: {module_name})',
            True, (dp(500), dp(500)))
        return
    
    def add_input(self, instance):
        """Links an input from a text entry, adds to the ModuleManager, and updates the input popup

        :param instance: Button routing to this function
        :type instance: kivy.uix.button.Button
        """

        
        #grab needed info form the id
        key_number = int(instance.id.split()[0])
        module_name = instance.id[2:]
        key = list(self.plugin_player.mm.at(module_name).inputs())[key_number]

        #grab input from text entry
        custom_declaration = self.custom_declaration[key_number].text

        #try to assign the variable
        #may be a security risk as it evaluates injected code
        # TODO: find eval alternative
        try:
            custom_input = eval(custom_declaration,
                                sys.modules['__main__'].__dict__)
            
            #attempt to change the input in the module manager
            self.plugin_player.mm.at(module_name).change_input(key, custom_input)
            
            #if successful add it to the module dictionary to save and add success message
            self.module_dict[module_name].inputs[key_number] = custom_declaration
            
            self.plugin_player.add_message(f'Input {key} of {module_name} successfully set as {custom_declaration} in ModuleManager')
            
        except Exception as e:
            self.plugin_player.add_message(
                f"Could not set input {custom_declaration}: {e}")
        
        #refresh the inputs menu
        self.inputs_config()
        return
    
    
    def property_type_config(self):
        """Prompts user input for a property type through a popup
        """
        
        module_name = self.plugin_player.tree_manager.tree_module
        
        #check if a module is loaded onto the tree
        if(module_name == None):
            self.plugin_player.add_message("Can't configure property type: No module loaded onto the tree")
            return
        
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

        #create an entry to declare a property type
        custom_ptype = BoxLayout(orientation='horizontal', spacing=0)

        #add a declaration widget to set the input
        self.custom_declaration = TextInput(hint_text="ex: Force()",
                                               size_hint_x=4 / 5,
                                               multiline=False)
            
        #set preselected input text if already set
        if self.module_dict[module_name].property_type:
                self.custom_declaration.hint_text = f'Set: {self.module_dict[module_name].property_type}'
        custom_ptype.add_widget(self.custom_declaration)

        #add button to set the property type
        custom_entry_button = Button(
            text="Set",
            size_hint_x=1 / 5,
            on_press=self.add_property_type)
        
        custom_ptype.add_widget(custom_entry_button)

        ptype_widget.add_widget(custom_ptype)
        

        self.plugin_player.create_popup(
            ptype_widget, f'Property Type Configuration: {module_name})',
            True, (dp(500), dp(500)))
        return

    def add_property_type(self, instance):
        """Links a property type from a text entry and updates the property type popup

        Args:
            instance (kivy.uix.button): The button clicked to route to this function
        """

        module_name = self.plugin_player.tree_manager.tree_module
        
        #grab input from text entry
        custom_declaration = self.custom_declaration.text

        #try to assign the variable
        #may be a security risk as it evaluates injected code
        # TODO: find eval alternative
        try:
            property_type_eval = eval(custom_declaration,
                                sys.modules['__main__'].__dict__)
            
            #if(not self.plugin_player.mm.at(module_name).ready(property_type_eval)):
            #    self.plugin_player.add_message(
            #        f"Could not set property type {custom_declaration}: Invalid property type")
            
            #evaluates and will store property type, can evaluate again in the 
            #if successful add it to the module dictionary to save and add success message
            self.module_dict[module_name].property_type = custom_declaration
            self.module_dict[module_name].evaluated_property_type = property_type_eval
            
            
            self.plugin_player.add_message(f'Property type of {module_name} successfully set as {custom_declaration} in ModuleManager')
            
        except Exception as e:
            self.plugin_player.add_message(
                f"Could not set property type {custom_declaration}: {e}")
        
        #refresh the inputs menu
        self.property_type_config()
        return
        
    def submods_config(self, instance):
        """Generates a popup for setting the submodule for a module

        Args:
            instance (kivy.uix.button): the button clicked to route to the submodules options
        """

        #attempt to close any popups
        try:
            self.plugin_player.popup.dismiss()
        except:
            pass
        #grab the node's index and its corresponding module
        module_name = self.plugin_player.tree_manager.tree_module
        mm = self.plugin_player.mm
        module = mm.at(module_name)

        #create a widget to display the submodules
        submods_widget = BoxLayout(orientation='vertical',
                                   spacing=0,
                                   size_hint_y=None,
                                   minimum_height=dp(400))
        submod_label = Label(text="Submodule Configuration",
                             valign='center',
                             halign='center',
                             font_size='20sp',
                             color=(0, 0, 0, 1))
        submods_widget.add_widget(submod_label)

        
        #add each submodule and a text input to add it
        for i in range(len(module.submods().items())):
            #grab the key for the submodule
            key = list(module.submods().keys())[i]
            value = list(module.submods().values())[i]
            try:
                value_description = value.description()
                
            except:
                value_description = "description unavailable"

            #create the box to hold the submod's options
            submod_list = BoxLayout(orientation='horizontal',
                                    size_hint_y=None,
                                    height=dp(30),
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
            if(value.has_name()):
                submod_description.text = f'Set: {value.get_name()}'

            #create the add button that routes to an adding submodule function
            submod_add_button = Button(text='Set', size_hint_x=1 / 5)
            submod_add_button.id = f'{i}'
            submod_add_button.bind(on_press=self.select_submod)
            submod_list.add_widget(submod_add_button)

            #add it to main submodule holder
            submods_widget.add_widget(submod_list)

        #add a "no submodules" label if there are none
        if len(module.submods().items()) == 0:
            submods_widget.add_widget(
                Label(text="No Submodules", halign='left', color=(0, 0, 0, 1)))
        
        #add scrolling capabilities
        scroll_view = ScrollView(do_scroll_x=False,
                                 do_scroll_y=True,
                                 scroll_y =1,
                                 scroll_type=['bars'])
        scroll_view.add_widget(submods_widget)
        #add to the popup
        self.plugin_player.create_popup(
            scroll_view, f'Submodule Configuration for {module_name}',
            True, (dp(600), dp(400)))
        

    def select_submod(self, instance):
        """Opens a popup to prompt a user to select a submodule from the imported modules.

        :param instance: Button routing to the function
        :type instance: kivy.uix.button.Button
        """
        #grab needed info form the id and
        key_number = int(instance.id)
        module_name = self.plugin_player.tree_manager.tree_module
        key = list(self.plugin_player.mm.at(module_name).submods().keys())[key_number]

        #start creating a widget for selecting a submodule
        select_submod = BoxLayout(orientation='vertical',
                                  size_hint=(None, None),
                                  width=dp(800),
                                  minimum_height = dp(500),
                                  spacing=0)

        #keep track of height for scrolling padding
        height = 0
        #add back button
        back_button = Button(text="Back",
                             size_hint=(None, None),
                             size=(dp(40), dp(20)),
                             on_press=self.submods_config)
        select_submod.add_widget(back_button)
        height += 20

        plugin_number = 0
        module_number = 0
        #for each module in each plugin, place a module and option to add
        for plugin in self.plugin_player.plugin_manager.saved_plugins:

            for module in plugin.modules:
                #create a module with an add button
                module_box = BoxLayout(orientation='horizontal',
                                       size_hint=(None, None),
                                       size=(dp(750), dp(30)),
                                       spacing=0)
                module_box.add_widget(
                    Label(text=module,
                          color=(0, 0, 0, 1),
                          halign='left',
                          size_hint_x=9 / 10))

                add_button = Button(
                    text="Set",
                    size_hint_x=1 / 10,
                    on_press=self.add_submod)
                #add id to identify the submodule from the node, and the module to be the submodule
                add_button.id = f'{key_number} {plugin_number} {module_number}'
                module_box.add_widget(add_button)

                #add to main box
                select_submod.add_widget(module_box)
                height += dp(30)

                module_number += 1
        plugin_number += 1
        module_number = 0

        #add scrolling capabilities
        scroll_view = ScrollView(scroll_y=0,
                                 do_scroll_y=True,
                                 size_hint=(None, None),
                                 size=(dp(800), dp(500)),
                                 scroll_type=['content'])
        scroll_view.add_widget(select_submod)

        self.plugin_player.create_popup(scroll_view,
                                        f'Selecting submodule: {key}', False, (dp(800), dp(500)))
        
    #attempts to add a submodule type to a node
    def add_submod(self, instance):
        """Dictates the linkage of a module's submodule by attempting to assign the inputted submodule to the module

        :param instance: The instance of the button pressed to redirect to this function.
        :type instance: kivy.uix.button.Button
        """

        mm = self.plugin_player.mm
        module_name = self.plugin_player.tree_manager.tree_module
        
        #get info from the instance id
        key_number = int(instance.id.split()[0])
        key_name = list(mm.at(module_name).submods().keys())[key_number]
        plugin_number = int(instance.id.split()[1])
        submodule_number = int(instance.id.split()[2])
        submodule_name = self.plugin_player.plugin_manager.saved_plugins[
            plugin_number].modules[submodule_number]

        #attempt to add the submodule in the Module Manager
        try:
            mm.change_submod(module_name, key_name,submodule_name)
            self.plugin_player.add_message(
                f"Added submodule {submodule_name} to {key_name} of {module_name} in the ModuleManager"
            )
        except Exception as e:
            self.plugin_player.add_message(
                f"Could not add submodule {submodule_name} to {key_name} of {module_name}\n {e}"
            )

        #go back to submods_config and update tree
        module_tree = self.plugin_player.tree_manager.submodule_dependencies()
        tree_nodes = self.plugin_player.tree_manager.generate_tree(module_tree)
        self.plugin_player.tree_manager.add_connections(module_tree, tree_nodes)
        fakeButton =  Widget()
        self.submods_config(fakeButton)

        
        
    def run(self):
        
        #get the module name
        module_name = self.plugin_player.tree_manager.tree_module
        
        #check if a module is loaded onto the tree
        if(module_name == None):
            self.plugin_player.add_message("Run Error: No module loaded onto the tree")
            return
        
        #get the module
        mm = self.plugin_player.mm
        module = mm.at(module_name)
        
            
        # #get the reasons why its not ready
        # not_ready = module.list_not_ready()
            
        # #display inputs that aren't ready
        # if(not_ready["Inputs"]):
                
        #     #display error message
        #     self.plugin_player.add_message(f"Run Error: Module {module_name} is not ready to be ran")
            
        #     self.plugin_player.add_message("Inputs are not set:")
            
        #     for value in not_ready["Inputs"]:
        #         self.plugin_player.add_message(f"{value}")

        #     #skip rest of function
        #     return
                    
        # #display submodules that aren't ready
        # if(not_ready["Submodules"]):
        #     #display error message
        #     self.plugin_player.add_message(f"Run Error: Module {module_name} is not ready to be ran")
            
        #     self.plugin_player.add_message("Submodules are not set:")
            
        #     for value in not_ready["Submodules"]:
        #         self.plugin_player.add_message(f"{value}")
                
        #     #skip rest of function
        #     return                
        
        if(self.module_dict[module_name].property_type == None):
            self.plugin_player.add_message("Property Type is not set")
            #skip rest of function
            return
            
        
        #attempt to run the module
        try:
            output = module.run(self.module_dict[module_name].evaluated_property_type)
            
            #print success message and output
            self.plugin_player.add_message(f"Successfully ran {module_name}\nOutput: {output}")

        except Exception as e:
            self.plugin_player.add_message(f"Run Error: {e}")

        return
