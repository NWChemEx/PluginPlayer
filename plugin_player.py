#file and library helpers
import importlib
import os
import sys

#helper classes for a PluginPlayer interface
import pluginplay as pp
from plugin_manager import PluginManager
from tree_manager import TreeManager
from node_widget_manager import NodeWidgetManager
from node_manager import NodeManager
from utility_manager import UtilityManager

#kivy helpers
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.image import Image

#image resizer
from PIL import Image as PILImage


#Class defining the running app
class PluginPlayer(App):

    #build the main window from the kv file
    def build(self):
        self.popup = Popup()

        #The app's module manager
        self.mm = pp.ModuleManager()

        #saved tree containing the nodes and modules to be ran
        self.nodes = []
        
        #helper class handling addition/removal of nodes, deleting/running the tree
        self.tree_manager = TreeManager(self)

        #helper class handling the widget building for the node configuration
        self.node_widget_manager = NodeWidgetManager(self)

        #helper class handling the linking of inputs, submods, property types between modules
        self.node_manager = NodeManager(self)

        #helper class handling the loading, deleting, and viewing of plugins and their modules
        self.plugin_manager = PluginManager(self)

        #helper class handling browsing, imported class types, and importing new classes
        self.utility_manager = UtilityManager(self)

        #build the main application from the kivy script file
        build = Builder.load_file('plugin_player_setup.kv')

        #add logo
        tree_section = build.ids.right_section.ids.tree_section
        logo = Image(source='NWCHEMEX.png', fit_mode="fill", size_hint=(None, None), size=(200, 200), pos_hint={'right': 1, 'y': 0})
        tree_section.add_widget(logo)

        return build

    #Add a string message to the message section
    def add_message(self, message):

        #grab message widget
        message_widget = self.root.ids.message_section

        #add the message
        message_widget.ids.message_label.text += f"\n{message}"
        message_widget.scroll_y = 1

    #set up a basic popup given a scrolling widget and a name
        
    def create_popup(self, widget, description, dismiss):
        
        #close and change popup
        self.popup.dismiss()
        self.popup = Popup(content=widget, size_hint=(None,None), size=(800,500), 
                background_color=(255, 255, 255), auto_dismiss=dismiss, title=description, 
                title_color=(0,0,0,1))
        self.popup.open()

    def create_image(self, filepath, new_filepath, size):
        image = PILImage.open(filepath)
        resized_image = image.resize(size)
        resized_image.save(new_filepath)
if __name__ == "__main__":
    PluginPlayer().run()