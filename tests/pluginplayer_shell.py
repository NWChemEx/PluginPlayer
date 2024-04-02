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
import pluginplay_examples as ppe
from pluginplayer.plugin_manager import PluginInfo
from pluginplayer.plugin_player import PluginPlayer
from unittest.mock import MagicMock


class PluginPlayerShell:

    def get_shell(self):

        #create an instance of the player
        player = PluginPlayer()
        player.test_setup()

        #mock the visual functions
        player.add_message = MagicMock()
        player.plugin_manager.plugin_view = MagicMock()
        player.create_image = MagicMock()
        player.create_popup = MagicMock()
        player.root = MagicMock()

        #load the example modules into the plugin manually through instance variables
        ppe.load_modules(player.mm)

        #add it to the list of modules
        new_plugin = PluginInfo(plugin_name="pluginplay_examples",
                                modules=player.mm.keys())
        player.plugin_manager.saved_plugins.append(new_plugin)

        #return the instance
        return player
