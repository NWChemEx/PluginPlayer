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

#pluginplay helpers
import pluginplay as pp
import pluginplayer_examples as ppe
from pluginplayer.plugin_manager import PluginInfo
from pluginplayer.plugin_player import PluginPlayer
from unittest.mock import MagicMock

#helper classes for a PluginPlayer interface
from pluginplayer.plugin_manager import PluginManager, ModuleValues
from pluginplayer.tree_manager import TreeManager
from pluginplayer.run_manager import RunManager
from pluginplayer.utility_manager import UtilityManager

#kivy helpers
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.image import Image


class PluginPlayerShell:
    """The class representing the connecting helper class 
    components of PluginPlayer without triggering Kivy window production
    """

    def __init__(self):
        """Initializes the helpers and instance variables for the PluginPlayer class for testing
        """
        
        self.root = MagicMock()
                
        self.popup = Popup()

        #The app's module manager
        self.mm = pp.ModuleManager()

        #helper class handling addition/removal of nodes, deleting/running the tree
        self.tree_manager = TreeManager(self)

        #helper class handling the inputs, property types, and submodules at runtime
        self.run_manager = RunManager(self)
        
        #helper class handling the loading, deleting, and viewing of plugins and their modules
        self.plugin_manager = PluginManager(self)

        #helper class handling browsing, imported class types, and importing new classes
        self.utility_manager = UtilityManager(self)

        #mock the visual functions
        self.add_message = MagicMock()
        self.plugin_manager.plugin_view = MagicMock()
        self.create_image = MagicMock()
        self.create_popup = MagicMock()

        #load the example modules into the plugin manually through instance variables
        ppe.load_modules(self.mm)

        #add it to the list of modules
        new_plugin = PluginInfo(plugin_name="pluginplayer_examples",
                                modules=self.mm.keys())
        self.plugin_manager.saved_plugins.append(new_plugin)
        
        #add each module into the module dictionary for saving inputs and property types
        for key in self.mm.keys():
            self.run_manager.module_dict[key] = ModuleValues(key, self.mm)
