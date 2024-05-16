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

#file and library helpers
import importlib
import os
import sys

#helper classes for a PluginPlayer interface
import pluginplay as pp
from pluginplayer.plugin_manager import PluginManager
from pluginplayer.tree_manager import TreeManager
from pluginplayer.utility_manager import UtilityManager
from pluginplayer.run_manager import RunManager

#kivy helpers
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.metrics import dp

#image resizer
from PIL import Image as PILImage


#Class defining the running app
class PluginPlayer(App):
    """A class to open a python Kivy application for the PluginPlayer GUI. 

    This GUI will allow users to import plugins from their filesystem, view each of their module's information, and create a tree structure of modules to run.
    Creating a tree structure, they are able to link modules together, add submodules, property types, and inputs for each module.

    :param App: The Kivy App class
    :type App: kivy.app.App
    :return: returns a built app
    :rtype: kivy.app.App
    """

    #build the main window from the kv file
    def build(self):
        """Builds the main window from the plugin_player_setup.kv file, and creates instances of helper classes to alter the imported plugins and tree structure.

        :return: The built Kivy application
        :rtype: kivy.app.App
        """

        #string array holding the filepaths of resized images
        self.resized_images = []

        self.popup = Popup()

        #The app's module manager
        self.mm = pp.ModuleManager()

        #helper class handling addition/removal of nodes, deleting/running the tree
        self.tree_manager = TreeManager(self)

        #helper class handling the widget setting submodules, inputs, and running the module
        self.run_manager = RunManager(self)

        #helper class handling the loading, deleting, and viewing of plugins and their modules
        self.plugin_manager = PluginManager(self)

        #helper class handling browsing, imported class types, and importing new classes
        self.utility_manager = UtilityManager(self)

        #build the main application from the kivy script file
        build = Builder.load_file('src/pluginplayer/plugin_player_setup.kv')

        #standardize spacing
        tree_section = build.ids.tree_section
        tree_section.spacing = dp(50)

        self.root = build

        return build

    def add_message(self, message):
        """Add a string message to the message section

        :param message: The string to add to the message section
        :type message: str
        """

        #add the message
        self.root.ids.message_label.text += f"\n{message}"
        self.root.ids.message_section.scroll_y = 1

    def create_popup(self, widget, description, dismiss, size):
        """Set up a basic popup given a scrolling widget, name, description, and dismissal protocol


        :param widget: The widget to be displayed in the popup
        :type widget: kivy.uix.widget.Widget
        :param description: The description of the popup
        :type description: str
        :param dismiss: True if you want the popup to autodismiss, False if not
        :type dismiss: bool
        """

        #close and change popup
        self.popup.dismiss()
        self.popup = Popup(content=widget,
                           size_hint=(None, None),
                           size=(int(size[0]), int(size[1])),
                           background_color=(255, 255, 255),
                           auto_dismiss=dismiss,
                           title=description,
                           title_color=(0, 0, 0, 1))
        self.popup.open()

    def create_image(self, filepath, new_filepath, size):
        """Resize an image using Pillow to fit the pixel size desired.

        :param filepath: The filepath of the image to be resized
        :type filepath: str
        :param new_filepath: The filepath of the new resized image
        :type new_filepath: str
        :param size: The desired size of the new image
        :type size: (int, int)
        """

        image = PILImage.open(filepath)
        resized_image = image.resize((int(size[0]), int(size[1])))
        resized_image.save(new_filepath)
        self.resized_images.append(new_filepath)

    def on_stop(self):
        """On the closing of the application, the saved resized images used in the application are located and deleted.
        """
        for filepath in self.resized_images:
            if os.path.exists(filepath):
                os.remove(filepath)


if __name__ == "__main__":
    PluginPlayer().run()
