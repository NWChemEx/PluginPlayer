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
The need for a utility manager
    Throughout the GUI it is essential to keep track of added class types, adding new class types, and browsing files. The `UtilityManager` class handles this to allow for helper functions needed throughout the application.

Browsing files

    Browsing files in kivy can be done by clicking the browse button to run the `browse` function and open a popup to view your system's files. The `browse` function reads text input from an entry and interprets it as a potential path to browse to in the system. Using a `ScrollView` widget, a user can navigate through their system and select a filepath of their plugin they would like to import.

Viewing class types
    To add an input or property type to a module's run settings, a user may need to declare a special variable type, evaluating their statement with an extra list of imported classes is necessary to allow for a more complex module run. Viewing imported class types within the `view_config` and `add_input` widget runs the `class_types` function, opening a popup to view a list of imported class types and a button to import a new type.

Importing a new class type
    Directed from the `class_types` popup, you can enter a python partial import statement defining the library to import from as well as the type name. Clicking the Import button, the `new_type` function runs `importlib` to import the new class type into the system's main modules which is used in evaluating import and property type statements. If a module is unable to be imported, a message is displayed and the system's modules are not modified.
"""

#import helpers
import importlib
import sys
import os

#kivy helpers
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.metrics import dp


class UtilityManager():
    """Helper class for the PluginPlayer application to browse files, view class types, and import new class types.
    """

    def __init__(self, plugin_player):
        """Initialization of the UtilityManager class

        Args:
            plugin_player (PluginPlayer): the PluginPlayer object this UtilityManager is associated with
        """
        self.plugin_player = plugin_player
        self.imported_classes = []
        self.custom_declaration_widget = None

    def browse(self, instance):
        """Browse for a new file from the file system and place in entry box
        """

        #grab text from entry
        entry_text = self.plugin_player.root.ids.file_entry.ids.file_path_input.text

        #if entry text is a directory, open popup to directory
        if os.path.isdir(entry_text):
            file_chooser = FileChooserListView(path=entry_text)
        else:
            file_chooser = FileChooserListView()

        #internal function to select the file
        def select_file(instance, selection, *args):
            if selection:
                # Set selected file path in TextInput
                file_entry_widget = self.plugin_player.root.ids.file_entry.ids.file_path_input
                file_entry_widget.text = selection[0]
                file_entry_widget = self.plugin_player.root.ids.file_entry.ids.file_path_input
                file_entry_widget.text = selection[0]
                popup.dismiss()

        #set up the popup
        popup = Popup(title='Select a file',
                      content=file_chooser,
                      size_hint=(None, None),
                      size=(dp(500), dp(500)))
        file_chooser.bind(on_submit=select_file)
        popup.open()

    def class_types(self):
        """Show a popup to see all class types imported
        """

        #start creating the new popup
        types_box = BoxLayout(orientation='vertical', minimum_height=dp(500))

        types_box.add_widget(
            Label(
                text=
                "Add a new class type by filling in the blanks separated by a space",
                color=(0, 0, 0, 1),
                size_hint_y=None,
                height=dp(20)))

        #create the entry to add an extra input
        new_type = BoxLayout(orientation='horizontal',
                             size_hint_y=None,
                             height=dp(35),
                             spacing=0)

        self.custom_declaration_widget =  TextInput(
            hint_text="from _____ import _____",
            multiline=False,
            size_hint_x=5/10)
        new_type.add_widget(self.custom_declaration_widget)

        #add an import button
        add_button = Button(text="Import",
                            size_hint_x=1 / 10,
                            on_press=self.new_type)
        
        new_type.add_widget(add_button)

        types_box.add_widget(new_type)

        types_box.add_widget(
            Label(text="Imported Types",
                  font_size="20sp",
                  height= dp(30),
                  color=(0, 0, 0, 1),
                  size_hint_y=None))

        for imported_type in self.imported_classes:
            types_box.add_widget(
                Label(text=imported_type,
                      size_hint_y=None,
                      height=dp(15),
                      color=(0, 0, 0, 1)))

        scroll_view = ScrollView(
                                 do_scroll_y=True,
                                 scroll_y=1,
                                 scroll_type=['bars'])
        scroll_view.add_widget(types_box)

        self.plugin_player.create_popup(scroll_view, "Class Types", True, (dp(800), dp(500)))

    def new_type(self, instance):
        """Defines a new class type for custom inputs and property types
        """
        try:
            import_name = self.custom_declaration_widget.text.split()[0]
            class_name = self.custom_declaration_widget.text.split()[1]
        except Exception as e:
            self.plugin_player.add_message(
                "Invalid Entry, enter the blanks with a space in between from the Python import statement"
            )
            self.plugin_player.add_message(f'{e}')
            return
        if class_name in self.imported_classes:
            self.plugin_player.add_message(
                f"Class type {class_name} previously imported")
            return
        try:
            #import the library
            lib = importlib.import_module(import_name)

            #create an instance
            class_instance = getattr(lib, class_name)

            # Add the class to the __main__ module's namespace and list of loaded class types
            setattr(sys.modules['__main__'], class_name, class_instance)
            self.imported_classes.append(class_name)

            #send success message
            self.plugin_player.add_message(f"Imported class type {class_name}")

        except Exception as e:
            #Failure Message
            self.plugin_player.add_message(
                f"Couldn't import type {class_name}: {e}")


        #recall the popup to update the newly loaded values and show hint text
        self.class_types()
