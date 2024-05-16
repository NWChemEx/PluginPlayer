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
Managing tree generation
    The `TreeManager` class handles setting the module to be viewed in a tree view, and generates the tree with its connections.

    When a user wants to view a module on the tree, they can select the Graph button from the PluginSection (left). 
    
    The Module will then be placed as the root node on the tree and it will build a map for each layer of the tree, adding a new layer
    with the submodules of the previous layer, including their mappings. This is done with the `submodule_dependencies` function.
    
    The `generate_tree` function will use the built map to center and place the nodes into a tree like structure.
    
    The `add_connections` function will then bind the mappings of each node with a line connecting them.
    
Deleting the tree
    All canvas instructions and widgets added to the tree section are removed, and the set inputs and property types are cleared.
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
        self.node_height = dp(80)
        self.node_width = dp(140)

    def delete_tree(self):
        """Delete the entire tree, its edges, and nodes.
        """
        #remove all widgets and reset inputs and module variables
        tree_module = self.tree_module
        self.tree_module = None

        self.plugin_player.root.ids.tree_section.clear_widgets()
        self.plugin_player.root.ids.tree_section.canvas.clear()
        
        self.plugin_player.add_message(f"Removed Module Tree: {tree_module}")

    def create_node(self, module_name):
        """Create a new node to add the tree section

        :param module_name: The name of the module the node will represent
        :type module_name: String
        """
        #create main widget
        node_widget = Widget(size_hint=(None, None),
                                      size=(self.node_width, self.node_height),
                                      pos_hint={'center_y':.5})
        
        #set the background color
        with node_widget.canvas.before: 
            Color(155/255, 159/255, 144/255)  # NWChemEx Dark Beige
            rect = RoundedRectangle(size=node_widget.size, pos=node_widget.pos, radius=[dp(20), dp(20), dp(20), dp(20)])

        # Bind size and pos to the rectangle
        node_widget.bind(
            size=lambda instance, value: setattr(rect, 'size', value),
            pos=lambda instance, value: setattr(rect, 'pos', value))
        
        #set id to node number
        #node_widget.id = f'{node_number}'
        basis_box = BoxLayout(orientation='horizontal', spacing=0, size=(self.node_width, self.node_height), size_hint=(None,None))

        #left side reserved for label and configure button
        basis_left = BoxLayout(orientation='vertical', spacing= 0)

        #add module name label
        widget_label = Label(
            size_hint=(None, None),
            width=dp(100),
            height=dp(80),
            halign='center',
            valign='center',
            color=(0,0,0,1),
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
            config_button.id=module_name
            
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
            tree_nodes= self.generate_tree(module_tree)
            self.plugin_player.add_message("Successfully Generated Module Nodes")

            #add connections to the tree
            self.add_connections(module_tree, tree_nodes)
            self.plugin_player.add_message("Successfully Created Module Connections")
            
            self.plugin_player.add_message("Successfully Created Module Tree")


        except Exception as e:
            self.plugin_player.add_message(f"Module Tree Generation Unsuccessful \n {e}")



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

            next_layer = []
            
            #check if the current tree layer has dependencies
            while(module_index < len(module_tree[tree_layer])):



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
        layers = []
        
        tree_section = self.plugin_player.root.ids.tree_section

        #clear all lines and widgets
        tree_section.clear_widgets()
        tree_section.canvas.before.clear()
                
        tree_section.width = self.plugin_player.root.ids.right_section.width

        layer_count = 0

        #create each layer in the tree
        for layer in module_tree:

            #add place for the node widgets to go
            tree_nodes.append([])

            layer_layout = BoxLayout(orientation='horizontal', width = 0, size_hint=(None, None), spacing=dp(50))
            

            #for each module mapping in the layer, place a node, its connecting line, and a configure button if it has submods
            for module_mapping in layer:
                
                #create the widget for the module node
                node_widget = self.create_node(module_mapping[1])
                tree_nodes[layer_count].append(node_widget)
                layer_layout.width += node_widget.width
                if(len(tree_nodes[layer_count])):
                    layer_layout.width += layer_layout.spacing
                layer_layout.add_widget(node_widget)

                
            
            #extend the tree_section width if its content width is greater, initiating scrolling on x
            if(layer_layout.width > tree_section.width):
                tree_section.width = layer_layout.width
            
            tree_section.add_widget(layer_layout)
            layers.append(layer_layout)
            layer_count += 1
            
        for layer in layers:
            #add edit the positioning of the widgets according to their length
            position_x = (1- (layer.width / tree_section.width)) / 2 + (layer.width / tree_section.width)/2
            layer.pos_hint={'center_x': position_x}

        return tree_nodes
    
    def add_connections(self, module_tree, tree_nodes):
        """Adds the lines to connect nodes

        Args:
            module_tree (Array): 2d Array mapping the modules and their submodule dependencies by layer
            tree_nodes (Array): 2d Array holding the module's node widgets by layer
        """

        layer_count = 0
        tree_section = self.plugin_player.root.ids.tree_section
        tree_section.canvas.before.clear()
        
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
            
                # Create a Line object
                connecting_line = Line(width=dp(3), points=[parent_module.center_x, parent_module.center_y, child_module.center_x, child_module.center_y])
                
                #add to the screen
                tree_section.canvas.before.add(Color(192/255,59/255,20/255))  #NWChemEX Red
                tree_section.canvas.before.add(connecting_line)
                
                #set binding function to attach to the widgets
                update_line = lambda instance, value, connecting_line=connecting_line, parent_module=parent_module, child_module=child_module: setattr(
                    connecting_line, 'points',
                    [parent_module.center_x, parent_module.center_y, child_module.center_x, child_module.center_y])

                # Bind the update_line function to the center positions
                parent_module.bind(center=update_line)
                child_module.bind(center=update_line)

                module_count += 1
            
            layer_count += 1

        return



    

        

