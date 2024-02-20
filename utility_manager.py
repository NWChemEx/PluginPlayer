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


#Helper class for the PluginPlayer application to browse files, view class types, and import new class types.
class UtilityManager():

    def __init__(self, plugin_player):
        self.imported_classes = []
        self.plugin_player = plugin_player

    #browse for a new file from file system and place in entry
    def browse(self):

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
                popup.dismiss()

        #set up the popup
        popup = Popup(title='Select a file',
                      content=file_chooser,
                      size_hint=(None, None),
                      size=(500, 500))
        file_chooser.bind(on_submit=select_file)
        popup.open()

    #load in a new plugin

    #show a popup to see all class types imported
    def class_types(self, instance):

        #grab needed info
        node_number = int(instance.id.split()[0])
        key_number = int(instance.id.split()[1])

        #start creating the new popup
        types_box = BoxLayout(orientation='vertical')

        #height of the popup to be updated later to fill whitespace
        height = 0

        #create a back button
        #return to main config page or back to the add input page
        back_to_main = (key_number == -1)
        on_press_func = self.view_config if back_to_main else self.add_input
        back_button = Button(text="Back",
                             size_hint=(None, None),
                             size=(40, 20),
                             on_press=on_press_func)
        back_button.id = f'{node_number}' if back_to_main else f'{node_number} {key_number}'
        types_box.add_widget(back_button)
        height += 20

        types_box.add_widget(
            Label(
                text=
                "Add a new class type by filling in the blanks separated by a space",
                color=(0, 0, 0, 1),
                size_hint_y=None,
                height=20))

        height += 20

        #create the entry to add an extra input
        new_type = BoxLayout(orientation='horizontal',
                             size_hint_y=None,
                             height=35,
                             spacing=0)
        new_type_entry = TextInput(hint_text="from _____ import _____",
                                   multiline=False,
                                   size_hint_x=9 / 10)
        new_type.add_widget(new_type_entry)

        #set as global to pull from it when its submitted
        self.custom_declaration_widget = new_type_entry

        #add an import button
        add_button = Button(text="Import",
                            size_hint_x=1 / 10,
                            on_press=self.new_type)
        #if its a property type assignt the id to route back to view_config,
        #otherwise route to input page
        add_button.id = f'{node_number} {key_number}'
        new_type.add_widget(add_button)

        types_box.add_widget(new_type)
        height += 35

        types_box.add_widget(
            Label(text="Imported Types",
                  font_size="20sp",
                  size_hint_y=None,
                  height=20))
        height += 20

        for imported_type in self.imported_classes:
            types_box.add_widget(
                Label(text=imported_type,
                      size_hint_y=None,
                      height=15,
                      color=(0, 0, 0, 1)))
            height += 15

        #add scrolling capabilities
        if height < 450:
            types_box.add_widget(
                Widget(size_hint_y=None, height=(450 - height)))
        scroll_view = ScrollView(scroll_y=0,
                                 do_scroll_y=True,
                                 scroll_type=['content'])
        scroll_view.add_widget(types_box)

        self.plugin_player.create_popup(scroll_view, "Class Types", False)

    #define a new class type for custom inputs and property types
    def new_type(self, instance):
        try:
            import_name = self.custom_declaration_widget.text.split()[0]
            class_name = self.custom_declaration_widget.text.split()[1]
        except Exception as e:
            self.plugin_player.addMessage(
                "Invalid Entry, enter the blanks with a space in between from the Python import statement"
            )
            self.plugin_player.addMessage(e)
            return
        if class_name in self.imported_classes:
            self.plugin_player.addMessage(
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
        self.class_types(instance)
