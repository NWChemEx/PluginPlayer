#stop automatic kivy methods
from kivy.config import Config
# Set Kivy to dummy backend to prevent window creation
Config.set('graphics', 'backend', 'dummy')

# test_pluginplayer.py
import unittest
from pluginplayer_shell import PluginPlayerShell

#kivy button for instance
from kivy.uix.button import Button

class TestPluginManager(unittest.TestCase):
    def test_plugin_import_from_shell(self):
        #get a new shell
        player = PluginPlayerShell.get_shell(self)

        #check if plugin is loaded
        self.assertNotEqual(player.plugin_manager.saved_plugins[0], None, "Failed to import pluginplay examples through test shell")
        self.assertEqual(len(player.plugin_manager.saved_plugins), 1, "Failed to import pluginplay examples through test shell")

    def test_delete_plugins(self):
        #get a new shell
        player = PluginPlayerShell.get_shell(self)

        #Create button instance to delete the first plugin
        deleteButton = Button()
        deleteButton.id = '0'
        player.plugin_manager.delete_plugin(deleteButton)

        #attempt to delete the first plugin
        self.assertEqual(player.plugin_manager.saved_plugins[0], None, "Failed to set the imported plugin to None after deletion")
        self.assertEqual(player.nodes, [])

        #get a new shell
        player = PluginPlayerShell.get_shell(self)

        #add a new node with instance routing to the first module from the first plugin
        moduleButton = Button()
        moduleButton.id = '0 0'
        player.tree_manager.add_node(moduleButton)
        
        #delete the plugin, which should delete all plugin's nodes as well
        player.plugin_manager.delete_plugin(deleteButton)

        self.assertEqual(player.plugin_manager.saved_plugins[0], None, "Failed to set the imported plugin to None after deletion")
        self.assertEqual(player.nodes[0], None, "Failed to set a plugin's nodes to None after the plugin's deletion")

if __name__ == "__main__":
    unittest.main()
