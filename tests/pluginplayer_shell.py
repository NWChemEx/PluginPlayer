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
import pluginplayer_examples
from pluginplayer.plugin_manager import PluginInfo,  ModuleValues
from pluginplayer.plugin_player import PluginPlayer


#kivy helpers
from kivy.app import App
from kivy.base import stopTouchApp



def getShell():
    """Initializes the helpers and instance variables for the PluginPlayer class for testing
    """
    running_app = App.get_running_app()
    if running_app:
        running_app.stop()
        stopTouchApp()
        running_app = None
        
    player = PluginPlayer()
    player.build()

    #load the example modules into the plugin manually through instance variables
    pluginplayer_examples.load_modules(player.mm)

    #add it to the list of modules
    new_plugin = PluginInfo(plugin_name="pluginplayer_examples",
                                modules=player.mm.keys())
    player.plugin_manager.saved_plugins.append(new_plugin)
        
    #add each module into the module dictionary for saving inputs and property types
    for key in player.mm.keys():
        player.run_manager.module_dict[key] = ModuleValues(key, player.mm)
        
    return player

def getShellNoLoading():
    """Initializes the helpers and instance variables for the PluginPlayer class for testing without importing the pluginplayer_examples
    """
    running_app = App.get_running_app()
    if running_app:
        running_app.stop()
        stopTouchApp()
        running_app = None
        
    player = PluginPlayer()
    player.build()

        
    return player
        
