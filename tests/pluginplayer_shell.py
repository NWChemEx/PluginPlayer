#pluginplay helpers
import pluginplay as pp
import pluginplay_examples as ppe
from plugin_manager import PluginInfo
from unittest.mock import MagicMock
from plugin_player import PluginPlayer





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
    
