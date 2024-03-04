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

import pluginplay as pp
from collections import namedtuple

#import helpers
import sys
import os
import importlib

#kivy helpers
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

PluginInfo = namedtuple('PluginInfo', ['plugin_name', 'modules'])


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

    def plugin_loader(self):
        """Attempt to load in a plugin from a filepath stored in an entry box and update the plugin view and module manager
        """
        #grab filepath from the entry
        selected_file_path = self.plugin_player.root.ids.file_entry.ids.file_path_input
        filepath = selected_file_path.text
        selected_file_path.text = ""
        selected_file_path.hint_text = "Enter Filepath/Browsing Directory"
        # Check if the file exists and is a .so file
        if not os.path.isfile(filepath):
            self.plugin_player.add_message("File does not exist")
        elif not filepath.endswith('.so'):
            self.plugin_player.add_message("File is not a Plugin (.so) file")
        else:
            # Split the file path into directory and filename
            directory_path, filename = os.path.split(filepath)

            #remove the .so from the filename
            filename = os.path.splitext(filename)[0]

            #add to system path
            sys.path.append(directory_path)

            #import the plugin library
            try:
                lib = importlib.import_module(filename)
                #try to load plugin modules into module manager
                try:
                    lib.load_modules(self.plugin_player.mm)
                    self.plugin_player.add_message(
                        f"Successfuly loaded {filename} into ModuleManager")

                    #save info of the Plugin and its modules
                    temp_MM = pp.ModuleManager()
                    lib.load_modules(temp_MM)
                    new_plugin = PluginInfo(plugin_name=filename,
                                            modules=temp_MM.keys())
                    self.saved_plugins.append(new_plugin)
                    self.plugin_view()
                except Exception as e:
                    self.plugin_player.add_message(
                        f"Could not add {filename} to ModuleManager")
                    self.plugin_player.add_message(f"{e}")
            except Exception as e:
                self.plugin_player.add_message(
                    f"Could not import module {filename}: {e}")

    def delete_plugin(self, instance):
        """delete a preinstalled plugin from the module manager, remove all it's module nodes, remove linkage from the tree that depend on it's modules, and remove the folder from the plugin view.
        """
        #dismiss any popup
        self.plugin_player.popup.dismiss()

        #grab folder number and plugin name from the widget's id
        folder_number = int(instance.id)
        plugin = self.saved_plugins[folder_number]
        name = plugin.plugin_name

        #delete dependencies on the tree that are of the plugin's modules
        for module_name in plugin.modules:
            node_number = 0
            for node in self.plugin_player.nodes:
                if not node:
                    pass
                #remove nodes using the plugin's modules
                elif node.module_name == module_name:
                    temp_widget = Widget()
                    temp_widget.id = f'{node_number}'
                    self.plugin_player.tree_manager.remove_node(temp_widget)

                #remove all set submodules
                else:
                    for submodule in node.submod_map:
                        #check if the submodule is set to use the module
                        if submodule[1] == module_name:
                            submodule = (submodule[0], None)
                            self.plugin_player.add_message(
                                f"Removed Submodule: {submodule[0]}, {module_name} from Node {node_number}"
                            )
                node_number += 1

        for i in range(len(self.saved_plugins[folder_number].modules)):
            self.plugin_player.mm.erase(
                self.saved_plugins[folder_number].modules[i])
        self.saved_plugins[folder_number] = None
        self.plugin_player.add_message("Removed Plugin: " + name)
        self.plugin_view()

    def view_module_info(self, instance):
        """View a module's information of its property types, submodules, inputs, outputs, and description

        :param instance: Button that calls this function
        :type instance: kivy.uix.button.Button
        """
        #grab info from the instance id's
        module_number = int(instance.id.split()[0])
        plugin_number = int(instance.id.split()[1])
        accessed_in_tree = int(instance.id.split()[2])
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
                except:
                    submodule_add = f"    {key} description unavailable"
                    submodules += submodule_add
        else:
            submodules = "    None\n"

        description = module.description()
        if not description:
            description = "Not Supported"

        #put into massive string
        full_info = f"Description:{description}\nInputs:\n{inputs}Outputs:\n{outputs}Submods:\n{submodules}"

        #create main frame for popup
        new_frame = BoxLayout(orientation='vertical')
        #add back button
        back_button = Button(text="Back",
                             size_hint=(None, None),
                             size=(50, 20),
                             halign='left',
                             on_press=self.view_modules)
        back_button.id = f'{plugin_number} {accessed_in_tree}'
        new_frame.add_widget(back_button)

        #add info label
        info_label = Label(text=full_info, halign='left', color=(0, 0, 0, 1))
        new_frame.add_widget(info_label)
        scrolling_info = ScrollView(do_scroll_y=True, do_scroll_x=True)
        scrolling_info.add_widget(new_frame)

        self.plugin_player.create_popup(scrolling_info, module_name + " Info",
                                        False)

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

        #grab pluginSection widget
        plugin_section = self.plugin_player.root.ids.plugin_section

        #create widget to fill with modules
        module_widget = BoxLayout(orientation='vertical',
                                  size_hint=(None, None),
                                  size=(plugin_section.width - 20,
                                        plugin_section.height),
                                  spacing=5)

        #add a delete plugin button
        delete_plugin = Button(text='Delete Plugin',
                               color=(0, 0, 0, 1),
                               size_hint_y=None,
                               height=20,
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
                                    height=30,
                                    spacing=5)

            #add the name of the module
            module_name = Label(
                text=self.saved_plugins[folder_number].modules[i],
                color=(0, 0, 0, 1),
                size_hint_x=1 / 2)
            view_module.add_widget(module_name)

            #add the add button to add to the tree
            add_to_tree = Button(
                text='Add',
                size_hint_x=1 / 10,
                on_press=self.plugin_player.tree_manager.add_node)
            #set the id for the module number in the plugin
            add_to_tree.id = f'{i} {folder_number}'
            view_module.add_widget(add_to_tree)

            #add the info button for extended information
            view_info = Button(text='Info',
                               size_hint_x=1 / 10,
                               on_press=self.view_module_info)
            #set the id for the module number and plugin number and 0 (accessed in folder)
            view_info.id = f'{i} {folder_number} 0'
            view_module.add_widget(view_info)

            #add the module widget to the main view
            module_widget.add_widget(view_module)

        #fill in the empty scroll space
        space_filler = Label(height=plugin_section.height)
        module_widget.add_widget(space_filler)

        #add scrolling capabilities
        scroll_view = ScrollView(scroll_y=1, do_scroll_y=True)
        scroll_view.id = "scroll"
        scroll_view.add_widget(module_widget)

        self.plugin_player.popup = Popup(
            content=scroll_view,
            background_color=(255, 255, 255),
            size_hint=(None, None),
            size=plugin_section.size,
            auto_dismiss=True,
            title=self.saved_plugins[folder_number].plugin_name,
            title_color=(0, 0, 0, 1))
        self.plugin_player.popup.id = f'{folder_number}'
        self.plugin_player.popup.open()

    def plugin_view(self):
        """update the loaded plugin visual display of folders"""
        #grab the plugin section
        plugin_widget = self.plugin_player.root.ids.plugin_section

        #clear the plugin section's previous widgets
        plugin_widget.clear_widgets()

        #Set the folder size
        new_width, new_height = plugin_widget.width / 4 - 10, plugin_widget.width / 4 - 10
        self.plugin_player.create_image('../assets/folder_icon.png',
                                        '../assets/button_folder.png',
                                        (int(new_width), int(new_height)))

        number_of_added_plugins = 0
        for i in range(len(self.saved_plugins)):

            #skip when encountering a deleted plugin
            if not self.saved_plugins[i]:
                continue

            #add image and route the popup function when pressed
            image_widget = Button(on_press=self.view_modules,
                                  background_normal='button_folder.png',
                                  size_hint=(None, None),
                                  size=(new_width, new_height),
                                  text=self.saved_plugins[i].plugin_name,
                                  font_size=11,
                                  text_size=(new_width, None),
                                  halign='center',
                                  valign='bottom')
            image_widget.id = f'{i} 0'
            plugin_widget.add_widget(image_widget)
            number_of_added_plugins += 1

        #fill in space for sizing
        for i in range(4 - (number_of_added_plugins % 4)):
            extra_widgets = BoxLayout(size_hint=(None, None),
                                      size=(new_width, new_height))
            plugin_widget.add_widget(extra_widgets)
