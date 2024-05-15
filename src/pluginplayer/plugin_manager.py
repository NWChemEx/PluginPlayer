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

Dynamically Importing Plugins
    Modular packages must be imported into the system when creating a GUI interface to allow users to work with Plugins. 
    Each CMake compiled modular project creates a Plugin file within the internal build directory, registered as a .so file. 
    Each Plugin has the load_modules() function to import Modules into a ModuleManager. If the Plugin contains Modules that 
    don’t define its inputs, outputs, or submodules, the Plugin will not be imported, and an error message will be displayed. 
    The ModuleManager acts as a directory for all the Modules to be later configured and run.

    The current GUI design for dynamically importing and viewing plugin information to create an efficient application build.

    Users can enter a path to a plugin .so file or a directory to browse.

    Once a Plugin is imported using the `plugin_loader` function, it is displayed as a folder in the Plugin Section, 
    updated by the `plugin_view` function.

Viewing Modules and API
    A comprehensive GUI application should allow users to view each dynamically imported plugin’s Modules and their APIs, 
    including a functional description, inputs, outputs, and required submodules, to gain information when creating an application 
    design. Having documentation of each loaded Module allows for a more efficient application build.

    When selecting a Plugin folder, a user is shown a popup, showing each of the Plugin’s Modules using the `view_modules` 
    function. The user can also delete the Plugin and remove its Modules from the ModuleManager, clone a Module into the Module Manager,
    and add a Module to the Module tree for application building, and view its API info.

    When selecting the “Info” button for the module, the following popup is displayed to show the Module’s description, inputs, 
    outputs, and submodules using the `view_module_info` function. Information is provided for the Module’s parameters. If the 
    Module does not provide information, “description unavailable” will be shown.


"""

import pluginplay as pp
from collections import namedtuple

#import helpers
import sys
import os
import importlib

#kivy helpers
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.metrics import dp


PluginInfo = namedtuple('PluginInfo', ['plugin_name', 'modules'])

class ModuleValues:
    """The module class for storing information for the GUI, regarding the user's inputs and property types they set to each module
    """
    def __init__(self, module_name, mm):
        self.inputs = [None] * len(mm.at(module_name).inputs())
        self.evaluated_inputs = [None] * len(mm.at(module_name).inputs())
        self.property_type = None
        self.evaluated_property_type = None

class PluginManager:
    """Helper class for the PluginPlayer application handling loading/deleting plugins and viewing their modules
    """

    def __init__(self, plugin_player):
        """Initializing the PluginManager class to manage the PluginPlayer object

        :param plugin_player: The PluginPlayer object that the PluginManager will manage
        :type plugin_player: PluginPlayer
        """
        self.saved_plugins = []
        self.plugin_player = plugin_player
        self.custom_declaration = None

    def plugin_loader(self):
        """Attempt to load in a plugin from a filepath stored in an entry box and update the plugin view and module manager
        """
        #grab filepath from the entry
        selected_file_path = self.plugin_player.root.ids.file_entry.ids.file_path_input
        entered_text = selected_file_path.text
        selected_file_path.text = ""
        selected_file_path.hint_text = "Enter Filepath/Browsing Directory"
        
        # Check if the file exists and is a .so file
        if os.path.isfile(entered_text) and entered_text.endswith('.so'):
            self.plugin_player.add_message("File" + entered_text + "recognized as .so Plugin file")
            directory_path, filename = os.path.split(entered_text)
            library = os.path.splitext(filename)[0]
            
            #add to system path
            sys.path.append(directory_path)
            
        elif os.path.isfile(entered_text) and entered_text.endswith('.py'):
            self.plugin_player.add_message("File" + entered_text + "recognized as .py Plugin file")
            directory_path, filename = os.path.split(entered_text)
            library = os.path.splitext(filename)[0]
            #add to system path
            sys.path.append(directory_path)
        
        else:
            library = entered_text

        #import the plugin library
        try:
            lib = importlib.import_module(library)
            #try to load plugin modules into module manager
            try:
                lib.load_modules(self.plugin_player.mm)
                self.plugin_player.add_message(
                    f"Successfuly loaded {library} into ModuleManager")
                
                #save info of the Plugin and its modules
                temp_MM = pp.ModuleManager()
                lib.load_modules(temp_MM)
                new_plugin = PluginInfo(plugin_name=library,
                                        modules=temp_MM.keys())
                self.saved_plugins.append(new_plugin)

                #add each module into the module dictionary for saving inputs and property types
                for key in temp_MM.keys():
                    self.plugin_player.run_manager.module_dict[key] = ModuleValues(key, self.plugin_player.mm)
                
                #create the plugin view
                self.plugin_view(-1, None)
                
            except Exception as e:
                self.plugin_player.add_message(
                    f"Could not add {library} to ModuleManager")
                self.plugin_player.add_message(f"{e}")

        except Exception as e:
            self.plugin_player.add_message(
                f"Could not import module {library}: {e}")

    def delete_plugin(self, instance):
        """delete a preinstalled plugin from the module manager, remove all it's module nodes, remove linkage from the tree that depend on it's modules, and remove the folder from the plugin view.
        """
        #dismiss any popup
        self.plugin_player.popup.dismiss()

        #grab folder number and plugin name from the widget's id
        folder_number = int(instance.id)
        plugin = self.saved_plugins[folder_number]
        name = plugin.plugin_name

        #delete each module from the ModuleManager and the module dictionary
        for i in range(len(self.saved_plugins[folder_number].modules)):
            
            #grab module
            module = self.saved_plugins[folder_number].modules[i]
            
            #check if its currently in the tree, if so, delete the tree
            if(module == self.plugin_player.tree_manager.tree_module):
                self.plugin_player.tree_manager.delete_tree()

            #remove from module manager
            self.plugin_player.mm.erase(
                module)
            
            #remove from dictionary
            self.plugin_player.run_manager.module_dict.pop(module)
            
        #remove from the saved plugins
        deletedPlugin = self.saved_plugins[folder_number]
        self.saved_plugins.remove(deletedPlugin)
        
        #send message and update screen
        self.plugin_player.add_message("Removed Plugin: " + name)
        self.plugin_view(-1, None)

    def view_module_info(self, instance):
        """View a module's information of its property types, submodules, inputs, outputs, and description

        :param instance: Button that calls this function
        :type instance: kivy.uix.button.Button
        """
        accessed_in_tree = int(instance.id.split()[0])
        if(accessed_in_tree):
            module_name = instance.id[2:]
        else:
            #grab info from the instance id's
            module_number = int(instance.id.split()[1])
            plugin_number = int(instance.id.split()[2])
            module_name = self.saved_plugins[plugin_number].modules[module_number]
        module = self.plugin_player.mm.at(module_name)

        #find the information of inputs, outputs, submodules, description
        #alert on the messages and stop process if needed info can't be gathered
        outputs = ""
        inputs = ""
        submodules = ""
        description = ""
        output_dict = module.results()
        for key, value in output_dict.items():
            try:
                output_add = f"    {key}: {value.description()} \n"
            except:
                output_add = f"    {key}: description unavailable\n"
            outputs += output_add
        input_dict = module.inputs()
        for key, value in input_dict.items():
            try:
                input_add = f"    {key}: {value.description()} \n"
            except:
                input_add = f"    {key}: description unavailable\n"
            inputs += input_add
        submod_dict = module.submods()
        if submod_dict:
            for key, value in submod_dict.items():
                try:
                    submodule_add = f"    {key}: {value.description()} \n"
                    submodules += submodule_add
                except:
                    submodule_add = f"    {key} description unavailable"
                    submodules += submodule_add
        else:
            submodules = "    None\n"

        description = module.description()
        if not description:
            description = "Not Supported"

        #put into massive string
        full_info = f"Description:{description}\nInputs:\n{inputs}Outputs:\n{outputs}Submodules:\n{submodules}"

        #create main frame for popup
        new_frame = BoxLayout(orientation='vertical')

        #add info label
        info_label = Label(text=full_info, halign='left', color=(0, 0, 0, 1))
        new_frame.add_widget(info_label)
        scrolling_info = ScrollView(do_scroll_y=True, do_scroll_x=True)
        scrolling_info.add_widget(new_frame)

        self.plugin_player.create_popup(scrolling_info, module_name + " Info", True, (dp(800), dp(500)))

    def duplicate_module(self, instance):
        """Duplicates a module into the Module Manager by asking for a new name through a popup

        :param instance: The Clone button calling this function
        :type instance: kivy.uix.button
        """
        #grab the module's name
        moduleName = self.saved_plugins[int(instance.id.split()[0])].modules[int(instance.id.split()[1])]
        
        #create the main holder
        customNamePopup = BoxLayout(orientation='vertical', size=(dp(100), dp(100)))

        #prompt user to enter new clone name
        customNamePopup.add_widget(Label(text="Enter name for clone of " + moduleName,
                                color=(0,0,0,1),
                                height = dp(30), 
                                size_hint_y=None))
        
        #create text input
        self.custom_declaration = TextInput(multiline=False, 
                                            hint_text="ex. Classical Force (2)",
                                            height = dp(30), 
                                            size_hint_y=None)
        
        #add to holder
        customNamePopup.add_widget(self.custom_declaration)


        def initiate_clone(instance):
            """Internal function of duplicate_module that initiates the cloning process and stores in the saved plugins


            :param instance: When the submit button for the clone popup is pressed
            :type instance: kivy.uix.button
            """
            moduleName = self.saved_plugins[int(instance.id.split()[1])].modules[int(instance.id.split()[2])]

            #If the cancel button was called, put a cancel message and dismiss the popup
            if(instance.id.split()[0]=='-1'):
                self.plugin_player.add_message("Canceled module cloning " + moduleName)
                self.plugin_player.popup.dismiss()
                return
            

            newModuleName = self.custom_declaration.text
            #clone the module in the module manager
            try:
                self.plugin_player.mm.copy_module(moduleName, newModuleName)
                self.saved_plugins[int(instance.id.split()[1])].modules.append(newModuleName)
                self.plugin_player.run_manager.module_dict[newModuleName] = ModuleValues(newModuleName, self.plugin_player.mm)
                self.plugin_player.add_message("Successfully created clone module " + newModuleName)

                #create fake button to reset the plugin view
                fakeButton = Widget()
                fakeButton.id = f'{int(instance.id.split()[1])} 0 0'
                self.view_modules(fakeButton)
            except Exception as e:
                self.plugin_player.add_message("Failed cloning module:\n" + f'{e}')
                self.plugin_player.popup.dismiss()


        buttons = BoxLayout(orientation='horizontal', size=(dp(20), dp(100)))

        #add button padding
        buttons.add_widget(Widget(size_hint_x=1/5))

        #add cancel button 
        cancelButton = Button(on_press=initiate_clone, text="Cancel",  size_hint=(1,1/5))
        cancelButton.id = f'-1 {instance.id}'
        buttons.add_widget(cancelButton)

        #add button padding
        buttons.add_widget(Widget(size_hint_x=1/5))

        #add submit button
        submitButton = Button( on_press=initiate_clone, text="Submit", size_hint=(1,1/5))
        submitButton.id = f'1 {instance.id}'
        buttons.add_widget(submitButton)

        #add button padding
        buttons.add_widget(Widget(size_hint_x=1/5))

        customNamePopup.add_widget(buttons)
        
        #create popup
        self.plugin_player.create_popup(customNamePopup, "Cloning " + moduleName, False, (dp(600), dp(200)))
        return
    
    def view_modules(self, instance):
        """View modules from selecting a plugin giving options to add to the tree and view information

        :param instance: Button that calls this function
        :type instance: kivy.uix.button.Button
        """

        #close any current popup
        try:
            self.plugin_player.popup.dismiss()
        except:
            pass

        #grab folder number from the id
        folder_number = int(instance.id.split()[0])
        accessed_in_tree = int(instance.id.split()[1])
        
        #exit if back button was pressed from the tree view
        if accessed_in_tree:
            return
        
        #undrop the dropdown
        elif (int(instance.id.split()[2]) == 1):
            self.plugin_view(-1, None)
            return

        #grab pluginSection widget
        plugin_section = self.plugin_player.root.ids.plugin_section

        #create widget to fill with modules
        module_widget = BoxLayout(orientation='vertical',
                                  size_hint_x =None,
                                  size_hint_y = None,
                                  height = dp(20) + len(self.saved_plugins[folder_number].modules) * dp(35),
                                  width=plugin_section.width - dp(20),
                                  spacing=5)

        #add a delete plugin button
        delete_plugin = Button(text="Delete",
                               size_hint_y=None,
                               height=dp(20),
                               on_press=self.delete_plugin)

        #use id as a value holder for the folder number
        delete_plugin.id = f'{folder_number}'
        module_widget.add_widget(delete_plugin)

        #add each of the modules that are in the plugin
        module_amount = len(self.saved_plugins[folder_number].modules)
        for i in range(module_amount):
            #create main holding box
            view_module = BoxLayout(orientation='horizontal',
                                    size_hint_y=None,
                                    height=dp(30),
                                    spacing=dp(5))

            #add the name of the module, tabbed
            module_name = Label(
                text="    " + self.saved_plugins[folder_number].modules[i],
                color=(0, 0, 0, 1),
                size_hint_x=1 / 2)
            view_module.add_widget(module_name)

            duplicate = Button(
                text='Clone',
                size_hint_x =1 / 10,
                on_press=self.duplicate_module
            )
            duplicate.id = f'{folder_number} {i}'
            view_module.add_widget(duplicate)

            #add the add button to add to the tree
            add_to_tree = Button(
                text='Graph',
                size_hint_x=1 / 10,
                on_press=self.plugin_player.tree_manager.set_module)
            #set the id for the module number in the plugin
            add_to_tree.id = f'{folder_number} {i}'
            view_module.add_widget(add_to_tree)

            #add the info button for extended information
            view_info = Button(
                               size_hint_x=1 / 10,
                               text="Info",
                               on_press=self.view_module_info)
            #set the id for the module number and plugin number and 0 (accessed in folder)
            view_info.id = f'0 {i} {folder_number}'
            view_module.add_widget(view_info)

            #add the module widget to the main view
            module_widget.add_widget(view_module)

        self.plugin_view(folder_number, module_widget)

    def plugin_view(self, dropped, widget):
        """Updates the plugin section listing the import plugins, and will add a dropdown for the listed plugin, adding the given dropdown widget

        :param dropped: the plugin number which needs a dropdown
        :type dropped: int
        :param widget: the dropdown widget to be placed after the dropped plugin
        :type widget: kivy.uix.boxlayout
        """

        #grab the plugin section
        plugin_widget = self.plugin_player.root.ids.plugin_section.ids.plugin_container

        #clear the plugin section's previous widgets
        plugin_widget.clear_widgets()

        #resize dropdown images
        self.plugin_player.create_image('src/pluginplayer/assets/drop_button.png', 'src/pluginplayer/assets/drop.png', (20,20))
        self.plugin_player.create_image('src/pluginplayer/assets/dropped_button.png', 'src/pluginplayer/assets/dropped.png', (20, 20))


        #add a section for each plugin
        for i in range(len(self.saved_plugins)):
            pluginBox = BoxLayout(orientation='horizontal', height=dp(20), size_hint_y=None)
            pluginBox.id = f'{i}Plugin'

            #add the name
            pluginBox.add_widget(Label(text=self.saved_plugins[i].plugin_name, 
                                       size_hint_x=9/10,
                                       height=dp(20),
                                       size_hint_y=None, 
                                       color=(0, 0, 0, 1),
                                       font_size='17dp'))

            if(dropped == i):
                #add a dropdown button
                dropDown = Button( on_press=self.view_modules, 
                                background_normal='src/pluginplayer/assets/dropped.png',
                                size=(dp(20),dp(20)), 
                                size_hint=(None, None),
                                valign='bottom')
                dropDown.id = f'{i} 0 1'
                pluginBox.add_widget(dropDown)
                #add the widget to the main pluginView
                plugin_widget.add_widget(pluginBox)
                plugin_widget.add_widget(widget)    
            else:
                #add a dropdown button
                dropDown = Button(on_press=self.view_modules, 
                                background_normal='src/pluginplayer/assets/drop.png',
                                size=(dp(20),dp(20)), 
                                size_hint=(None, None),
                                valign='bottom')
                dropDown.id = f'{i} 0 0'

                pluginBox.add_widget(dropDown)
                #add the widget to the main pluginView
                plugin_widget.add_widget(pluginBox)
        plugin_widget.add_widget(Widget(height=dp(300), size_hint_y=None))
                
