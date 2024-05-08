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
Managing tree nodes
    The `TreeManager` class handles adding and deleting tree nodes and adding them to the `nodes` list.

    When a user wants to delete a node, they can press the delete X button on the node's widget to run the `delete_node` function which iterates through it's connections with other nodes, removes them, removes their lines, and then removes the widget from the tree.

    When a user wants to add a node, they can choose to add a module to the tree within the `module_view` which will run the `add_node` function, calling `NodeWidgetManager` defined types to build a new widget and add it to the `nodes` list with empty connections.

Running the tree
    A user can run their connected module tree by clicking the Run Tree button in the tree section. This will call the `run_tree` function that will recursively iterate through the `nodes` list using Depth First Search and determine if a node relies on another, creating a run order. If each node has all run settings set, the run order will individually run each module through the `ModuleManager`, store its output, and use it on other dependent modules. 

Deleting the tree
    A user can delete their connected module tree by clicking the Delete Tree button in the tree section. This will call the `delete_tree` function that will iterate through the `nodes` list and call the `remove_node` function, removing all connections within the tree and its nodes.

"""


#kivy helpers
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.metrics import dp


class TreeManager():
    """TreeManager is a helper class for the PluginPlayer application to add/delete nodes from the module tree, run the tree, and delete the tree
    """

    def __init__(self, plugin_player):
        """Initialization of the TreeManager class

        :param plugin_player: The PluginPlayer object that holds the nodes and tree the TreeManager will manage
        :type plugin_player: PluginPlayer
        """
        self.plugin_player = plugin_player
        self.saved_output = None
        self.tree_module = None

    def delete_tree(self):
        """Delete the entire tree, its edges, and nodes.
        """
        #remove all widgets and reset inputs and module variables
        tree_module = self.tree_module
        self.tree_module = None
        self.plugin_player.run_manager.module_dict[tree_module].property_type = None
        self.plugin_player.run_manager.module_dict[tree_module].inputs = [None] * len(self.plugin_player.mm.at(tree_module).inputs())
        self.plugin_player.run_manager.module_dict[tree_module].evaluated_inputs = [None] * len(self.plugin_player.mm.at(tree_module).inputs())

        self.plugin_player.run_manager.module_dict[tree_module].evaluated_property_type = None

        self.plugin_player.root.ids.right_section.ids.tree_section.clear_widgets()
        
        self.plugin_player.add_message(f"Removed Module Tree: {tree_module}")

    def create_node(self, module_name):
        """Create a new node to add the tree section

        :param module_name: The name of the module the node will represent
        :type module_name: String
        """
        #create main widget
        node_widget = Widget(size_hint=(None, None),
                                      size=(dp(140), dp(80)),
                                      pos_hint={'center_y':.5, 'center_x':.5})
        
        #set the background color
        with node_widget.canvas.before:
            Color(37 / 255, 150 / 255, 190 / 255,
                  1)  # Set the color (R, G, B, A)
            rect = RoundedRectangle(size=node_widget.size, pos=node_widget.pos, radius=[dp(20), dp(20), dp(20), dp(20)])

        # Bind size and pos to the rectangle
        node_widget.bind(
            size=lambda instance, value: setattr(rect, 'size', value),
            pos=lambda instance, value: setattr(rect, 'pos', value))
        
        #set id to node number
        #node_widget.id = f'{node_number}'
        basis_box = BoxLayout(orientation='horizontal', spacing=0, size=(dp(140), dp(80)), size_hint=(None,None))

        #left side reserved for label and configure button
        basis_left = BoxLayout(orientation='vertical', spacing= 0)

        #add module name label
        widget_label = Label(
            size_hint=(None, None),
            width=dp(100),
            height=dp(80),
            halign='center',
            valign='center',
            text=f"{module_name}")
        widget_label.text_size = widget_label.size
        basis_left.add_widget(widget_label)
        
        #add configure button if it has submodules
        if(self.plugin_player.mm.at(module_name).submods()):
            config_button = Button(
                size_hint=(None, None),
                height=dp(20),
                width=dp(90),
                valign='center',
                halign='center',
                pos_hint={'center_x':0.5},
                text='Map',
                on_press=self.plugin_player.run_manager.submods_config)
            node_widget.height += dp(20)
            
            basis_left.add_widget(config_button)

        basis_box.add_widget(basis_left)
        

        #resize info button
        self.plugin_player.create_image(
            'src/pluginplayer/assets/info_icon.png',
            'src/pluginplayer/assets/info.png', (dp(30), dp(30)))

        #make info button
        info_button = Button(
            background_normal='src/pluginplayer/assets/info.png',
            on_press=self.plugin_player.plugin_manager.view_module_info,
            size_hint=(None,None),
            pos_hint={'center_y':0.5},
            size=(dp(30),dp(30)))
        
        #Shift info button if a submodule existed
        if(self.plugin_player.mm.at(module_name).submods()): 
            info_button.pos_hint={'center_y':.65}
        
        #add id for module number, plugin number, and 1 (accessed in treeview)
        info_button.id = f'1 {module_name}'
        basis_box.add_widget(info_button)

        node_widget.add_widget(basis_box)
        
        # Bind posiion of widget to the basis box
        node_widget.bind(pos=lambda instance, value: setattr(basis_box, 'pos', value))

        return node_widget

    def set_module(self, instance):
        """Adds a module to the tree and saves its information to the tree

        Args:
            instance (kivy.uix.button): The button clicked to add the module to the tree
        """

        #remove the tree if its currently set
        if self.tree_module:
            self.delete_tree()


        #get the module you would like to add to the tree view
        plugin = self.plugin_player.plugin_manager.saved_plugins[int(instance.id.split()[0])]
        self.tree_module = plugin.modules[int(instance.id.split()[1])]


        try:
            #generate the submodule dependencies 
            module_tree = self.submodule_dependencies()
            self.plugin_player.add_message("Successfully Mapped Submodules")

            #generate the new tree
            tree_nodes = self.generate_tree(module_tree)
            self.plugin_player.add_message("Successfully Generated Module Nodes")

            #add connections to the tree
            self.add_connections(module_tree, tree_nodes)
            self.plugin_player.add_message("Successfully Created Module Connections")


        except Exception as e:
            self.plugin_player.add_message(f"Module Tree Generation Unsuccessful \n {e}")


        self.plugin_player.add_message("Successfully Created Module Tree")

    def submodule_dependencies(self):
        """generates a 2D array of each level of the tree
        """

        #grab the module manager
        mm = self.plugin_player.mm

        #start the 2D array
        module_tree = []

        #fill the first element of the array with the root (module added to the tree)
        module_tree.append([(-1, self.tree_module)])

        module_index = 0
        tree_layer = 0
        has_dependency = True

        #start iterating through, inserting the dependent submodules in the array
        while(has_dependency):

            #assume the layer does not have a dependency unless proved otherwise
            has_dependency = False

            #check if the current tree layer has dependencies
            while(module_index < len(module_tree[tree_layer])):

                next_layer = []

                #get module and its submodule list
                submodule_list = mm.at(module_tree[tree_layer][module_index][1]).submods()

                #if it has a submodule dependency that's set, add it to the next tree layer
                if(submodule_list):
                    for value in submodule_list.values():
                        if(value.has_name()):
                            next_layer.append((module_index, value.get_name()))
                            has_dependency = True

                #increment to check out next module
                module_index += 1
            
            #add the next layer if its full, reset counters
            if(len(next_layer) > 0):
                module_tree.append(next_layer)
                next_layer = []

            module_index = 0
            tree_layer += 1
        return module_tree
    
    def generate_tree(self, module_tree):
        """Generates the visual tree map, filling with module nodes

        Args:
            module_tree (Array): The 2d Array filled with the module layers of the trees
        """

        #Create the same 2D array module mapper, but fill with its corresponding widgets
        tree_nodes = []
        
        tree_section = self.plugin_player.root.ids.right_section.ids.tree_section

        tree_section.clear_widgets()
        tree_section.width = self.plugin_player.root.ids.right_section.width

        layer_count = 0

        #create each layer in the tree
        for layer in module_tree:

            #add place for the node widgets to go
            tree_nodes.append([])

            layer_layout = BoxLayout(orientation='horizontal', spacing=dp(50), size_hint=(None,None), pos_hint={'center_x':.5, 'center_y':.5})

            #for each module mapping in the layer, place a node, its connecting line, and a configure button if it has submods
            for module_mapping in layer:
                
                #create the widget for the module node
                node_widget = self.create_node(module_mapping[1])
                tree_nodes[layer_count].append(node_widget)
                layer_layout.add_widget(node_widget)
            
            #extend the tree_section width if its content width is greater, initiating scrolling on x
            if(layer_layout.width > tree_section.width):
                tree_section.width = layer_layout.width
            
            tree_section.add_widget(layer_layout)
            layer_count += 1

        return tree_nodes



        return
    
    def add_connections(self, module_tree, tree_nodes):
        """Adds the lines to connect nodes

        Args:
            module_tree (Array): 2d Array mapping the modules and their submodule dependencies by layer
            tree_nodes (Array): 2d Array holding the module's node widgets by layer
        """

        layer_count = 0

        #iterate through the module tree and make a line that connects the two modules
        for module_map_list in module_tree:

            #check if its the first module map, then skip it
            if (layer_count == 0):
                layer_count += 1
                continue

            module_count = 0

            #check each module map and add the line
            for module_map in module_map_list:
                parent_module_index = module_map[0]

                # grab the widget of the parent module
                parent_module = tree_nodes[layer_count - 1][parent_module_index]

                # grab the dependent module
                child_module = tree_nodes[layer_count][module_count]
                
                tree_section = self.plugin_player.root.ids.right_section.ids.tree_section
                #find the y coordinates of the parent and child be counting the hieght of each layer, and padding and centering
                child_y = (layer_count * dp(80) + layer_count * dp(50) + dp(50))
                parent_y =((layer_count - 1) * dp(80) + (layer_count - 1) * dp(50) + dp(50))

                #find the x coordinates of the parent and child be finding the distance between start of tree_section and the layer widget, added by the distance between start of layer widget and the module widget
                child_x = ((tree_section.width - child_module.parent.width) / 2) + child_module.x + dp(65)
                parent_x = ((tree_section.width - parent_module.parent.width) / 2) + parent_module.x + dp(65)

                # create the connecting line
                connecting_line = Line(points=[
                    parent_x,
                    parent_y,
                    child_x,
                    child_y
                ], width=2)

                # add the line to the layout
                self.plugin_player.root.ids.right_section.ids.tree_section.canvas.before.add(Color(0, 0, 0))
                self.plugin_player.root.ids.right_section.ids.tree_section.canvas.before.add(connecting_line)
                
                #add the line to the layout
                self.plugin_player.root.ids.right_section.ids.tree_section.canvas.before.add(
                    Color(0, 0, 0))
                self.plugin_player.root.ids.right_section.ids.tree_section.canvas.before.add(
                    connecting_line)

                module_count += 1
            
            layer_count += 1

        return



    

        

