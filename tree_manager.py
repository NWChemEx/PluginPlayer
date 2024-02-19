#helper widget classes for a draggable widget representing a module
from node_widget import DraggableImageButton, DraggableWidget, ModuleNode

#kivy helpers
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle


#helper class for the PluginPlayer application to add/delete nodes from the module tree, run the tree, and delete the tree
class TreeManager():
    def __init__(self, plugin_player):
        self.plugin_player = plugin_player

#delete the entire tree and its edges and nodes
    def delete_tree(self):
        #remove each node one by one
        self.plugin_player.addMessage("Initiating Tree Removal")
        for i in range(len(self.plugin_player.nodes)):
            if self.plugin_player.nodes[i]:
                temp_widget = Widget()
                temp_widget.id = f'{i}'
                self.remove_node(temp_widget)
        self.plugin_player.nodes = []
        self.plugin_player.addMessage("Removed Tree") 
    
    #adds a new node to the tree section
    def add_node(self, instance):
        #grab info from instance
        self.plugin_player.popup.dismiss()
        module_number = int(instance.id.split()[0])
        plugin_number = int(instance.id.split()[1])
        module_name = self.plugin_player.savedPlugins[plugin_number].modules[module_number]
        module = self.plugin_player.mm.at(module_name)

        #find the information of inputs, outputs, submodules, description
        try:
            output_dict = module.results()
        except Exception as e:
            self.plugin_player.addMessage(f"Couldn't find output information: {e}")
            return
        try:
            input_dict = module.inputs()
        except Exception as e:
            self.plugin_player.addMessage(f"Couldn't find input information: {e}")
            return
        try:     
            submod_dict = module.submods()
        except Exception as e:
            self.plugin_player.addMessage(f"Couldn't find submodule information: {e}")
            return
        try:
            description = module.description()
        except Exception as e:
            description = "Not Supported"
            self.plugin_player.addMessage(f"Couldn't find description: {e}")

        #create a node object
        new_node = ModuleNode(module=module, module_name=module_name, input_dict=input_dict, output_dict=output_dict, 
                submod_dict=submod_dict, description=description)

        #create main widget
        node_widget = DraggableWidget(size_hint=(None,None), size=(120,80), orientation='vertical', spacing=0)
        with node_widget.canvas.before:
            Color(37 / 255, 150 / 255, 190 / 255, 1)  # Set the color (R, G, B, A)
            rect = Rectangle(size=node_widget.size, pos=node_widget.pos)

        # Bind size and pos to the rectangle (optional)
        node_widget.bind(size=lambda instance, value: setattr(rect, 'size', value),
                 pos=lambda instance, value: setattr(rect, 'pos', value))
        #set id to node number
        #node_widget.id = f'{node_number}'
        basis_box = BoxLayout(orientation='horizontal', spacing=0)
        #add module name label
        widget_label = Label(size_hint=(None,None), width=100,height=80, 
                halign='center', valign='center', text=f"{module_name} ({len(self.plugin_player.nodes)})")
        widget_label.text_size=widget_label.size
        basis_box.add_widget(widget_label)

        #add box for option buttons
        options = BoxLayout(orientation='vertical', size_hint=(None,None), width=20, height=80,spacing=0)

        options.add_widget(Widget(size_hint_y=None, height=10))
        
        self.plugin_player.create_image('drag_icon.png', 'drag.png', (20,20))
        navigate_button = DraggableImageButton(node_widget=node_widget, 
                relative_window=self.plugin_player.root.ids.right_section.ids.tree_section, size_hint_y=None, height=20)
        options.add_widget(navigate_button)
        
        self.plugin_player.create_image('info_icon.png', 'info.png', (20,20))

        info_button = Button(background_normal='info.png', on_press=self.plugin_player.plugin_manager.view_module_info, 
                size_hint_y=None, height=20)
        #add id for module number, plugin number, and 1 (accessed in treeview)
        info_button.id = f'{module_number} {plugin_number} 1'
        options.add_widget(info_button)

        self.plugin_player.create_image('remove_icon.png','remove.png', (20,20))

        remove_button = Button(background_normal='remove.png', on_press=self.remove_node, 
                size_hint_y=None, height=20)
        remove_button.id = f'{len(self.plugin_player.nodes)}'
        options.add_widget(remove_button)

        options.add_widget(Widget(size_hint_y=None, height=10))

        basis_box.add_widget(options)
        node_widget.add_widget(basis_box)

        #add configure button
        config_button = Button(size_hint=(None,None), height=20, width=90, valign='center', 
                text='Configure', on_press = self.plugin_player.node_widget_manager.view_config)
        config_button.id = f'{len(self.plugin_player.nodes)}'
        node_widget.height += 20
        node_widget.add_widget(config_button)
        #add it to the screen and the main lists
        node_widget.pos = (1,1)
        self.plugin_player.root.ids.right_section.ids.tree_section.add_widget(node_widget)
        new_node.add_widget(node_widget)
        self.plugin_player.nodes.append(new_node)
        self.plugin_player.addMessage(f"Added new node {module_name} to the tree")

    #remove a node's widget and connecting edges
    def remove_node(self, instance):
        #get the node number
        node_number = int(instance.id)
        node = self.plugin_player.nodes[node_number]

        self.plugin_player.addMessage(f"Initiating removal of {node.module_name} Node: {node_number}")

        #remove the widget
        self.plugin_player.root.ids.right_section.ids.tree_section.remove_widget(node.module_widget)

        #remove input edges that are mapped
        input_number = 0
        for input_edge in node.input_map:
            if input_edge and input_edge[0] != -1:
                input_key = list(node.input_dict.keys())[input_number]
                #find output node its mapped to
                output_node_number = input_edge[0]
                output_number = input_edge[1]
                output_node = self.plugin_player.nodes[output_node_number]
                output_key = list(output_node.output_dict.keys())[output_number]

                #delete old lines connecting to the output node
                for line_set in output_node.module_widget.outgoing_lines:
                    if line_set[1] == (node_number, input_number):
                        output_node.module_widget.outgoing_lines.remove(line_set)
                        self.plugin_player.root.ids.right_section.ids.tree_section.canvas.before.remove(line_set[0])

                #remove its connection and create message
                output_node.output_map[output_number].remove((node_number, input_number))
                self.plugin_player.addMessage(f"Removed Output {output_key} of Node {output_node_number} to {input_key} from Node {node_number}")
            input_number += 1

        #remove output edges that are mapped
        output_number = 0
        for output in node.output_map:
            for output_edge in output:
                if output_edge:
                    output_key = list(node.output_dict.keys())[output_number]
                    #find input node its mapped to
                    input_node_number = output_edge[0]
                    input_number = output_edge[1]
                    input_node = self.plugin_player.nodes[input_node_number]
                    input_key = list(input_node.input_dict.keys())[input_number]
                    
                    #delete old lines connecting to the input node
                    for line_set in input_node.module_widget.incoming_lines:
                        if line_set[1] == (node_number, output_number):
                            input_node.module_widget.incoming_lines.remove(line_set)
                            self.plugin_player.root.ids.right_section.ids.tree_section.canvas.before.remove(line_set[0])

                    #remove its connection and create message
                    input_node.input_map[input_number] = None
                    self.plugin_player.addMessage(f"Removed Input: {input_key} of Node {input_node_number} to {output_key} from Node {node_number}")
            output_number += 1

        #delete data from tree list
        self.plugin_player.nodes[node_number] = None

        self.plugin_player.addMessage(f"Removed {node.module_name} Node: {node_number} from the tree")
        return
    
        #run the series of nodes through the connected tree
    def run_tree(self):
        #grab the tree
        nodes = self.plugin_player.nodes

        #create the stack for nodes to be processed including only nodes not dependent on others
        dfs_stack = []
        visited = []

        #run initial checks before traversal
        for node in nodes:

            #ignore deleted nodes
            if not node:
                continue
            
            #check if all nodes have a routed or set input and if they have a dependency
            has_dependency = False
            for input in node.input_map:
                if not input:
                    self.plugin_player.addMessage(f"Run Failure: {node.module_name}({nodes.index(node)}) has a missing input")
                    return
                if input[0] != -1:
                    has_dependency = True
            
            has_outputs = False
            for output_set in node.output_map:
                for output in output_set:
                    if output:
                        has_outputs = True
            
            #check if each submodule is satisfied
            for submod in node.submod_map:
                if not submod[1]:
                    self.plugin_player.addMessage(f"Run Failure: {node.module_name}({nodes.index(node)} has missing submodule")
                    return

            #check if property type is set
            if not node.property_type:
                self.plugin_player.addMessage(f"Run Failure: {node.module_name}({nodes.index(node)}) has no property type set")
                return
            
            #check if node has no edges for inputs or outputs
            #if not has_dependency and not has_outputs:
            #    self.addMessage(f"Unlinked node detected: {node.module_name}({nodes.index(node)})")

            
            #if it doesn't have a dependency, add it to the queue
            if not has_dependency:
                dfs_stack.append(node)
                visited.append(node)

        #check if it doesn't have any starting points
        if len(dfs_stack) == 0:
            self.plugin_player.addMessage("Could not find starting node with no routed inputs")
            return
        
        #do a dfs search
        dfs_result = self.dfs_traversal(nodes, dfs_stack, visited)

        #stop if no run order was given
        if not dfs_result:
            return
        
        #Print success and show run order
        self.plugin_player.addMessage("Successful initial scan of the tree")
        run_order = "Running in order: "
        for next_node in dfs_result:
            run_order += f"{next_node.module_name}({nodes.index(next_node)}), "
        run_order[:-2]
        self.plugin_player.addMessage(run_order)

        #set up the array for saving ouputs
        saved_outputs = []
        for i in range(len(run_order)):
            saved_outputs.append([])
        
        #run each node
        for run_node in dfs_result:

            #set up array for inputs to use
            run_inputs = []

            #gather each input
            for input in run_node.input_map:

                #grab custom input
                if input[0] == -1:
                    run_inputs.append(input[1])
                
                #grab saved output
                else:
                    output_node = run_inputs.input_map[0]
                    output_number = run_inputs.input_map[1]
                    saved_output = saved_output[output_node][output_number]
                    run_inputs.append(saved_output)
            
            #set the submodules
            for submod_set in run_node.submod_map:
                try:
                    self.plugin_player.mm.change_submod(run_node.module_name, submod_set[0], submod_set[1])
                except Exception as e:
                    self.plugin_player.addMessage(f"Couldn't add submodule {submod_set[0]} to {run_node.module_name}")
                    self.plugin_player.addMessage(f"Aborting tree run")
                    return

            
            #attempt to run the module with the inputs
            try:
                #Implement a way to select the property type using the class types imports
                output = self.plugin_player.mm.at(run_node.module_name).run_as(run_node.property_type[1], *run_inputs)
                self.plugin_player.addMessage(f"{run_node.module_name}({nodes.index(run_node)}) Output: {output}")
                saved_outputs[nodes.index(run_node)].append(output)
            except Exception as e:
                self.plugin_player.addMessage(f"Could not run {run_node.module_name}({nodes.index(run_node)}): {e}")
                self.plugin_player.addMessage(f"Aborting tree run")
                return              
        self.plugin_player.addMessage("Successfully ran tree")      
        return


    #recursively traverse the tree and returns run order list, catches cycles and non-used nodes
    def dfs_traversal(self, nodes, dfs_stack, visited):
            
        #START DFS TRAVERSAL

        #take top item in the stack
        current_node = dfs_stack[-1]

        #make an array to track the nodes already routed from this node
        routed = []

        #find a node its dependent on 
        for output_array in current_node.output_map:
            for output in output_array:
                next_node_number = output[0]
                next_input_number = output[1]
                next_node = self.plugin_player.nodes[next_node_number]

                #check if the next node has already been processed by this node (two outputs from this node mapped to next node)
                if next_node in routed:
                    continue

                #dependency of current node can be ignored (already satisfied)
                if next_node == current_node:
                    continue

                #check if node has already been processed by a different branch
                if next_node in visited:
                    
                    #back edge / cycle detected
                    self.plugin_player.addMessage(f"Cycle in tree detected from {next_node.module_name}({next_node_number}) to {current_node.module_name}({nodes.index(current_node)}))")
                    return None
                
                #no cycle detected, add it to the routed nodes list
                routed.append(next_node)


                #check if the next node can now run with the given input
                has_dependency = False
                for input in next_node.input_map:

                    #ignore custom inputs
                    if input[0] == -1:
                        continue
                    
                    #grab node it is dependent on
                    dependent_node = self.plugin_player.nodes[input[0]]

                    if dependent_node in visited:
                        pass

                    #set break if it has a dependency not yet ran
                    else:
                        has_dependency = True
                        break
                
                #make node the next in the tree traversal if it has no dependencies
                if not has_dependency:
                    dfs_stack.append(next_node)
                    visited.append(next_node)
                    back_edges = self.dfs_traversal(nodes, dfs_stack, visited)
                    
                    #if back edge was recursively detected, return None
                    if not back_edges:
                        return None

        
        #after fully traversing from the node, remove from the stack
        dfs_stack.remove(current_node)
        #return false, no back_edges were detected
        return visited
