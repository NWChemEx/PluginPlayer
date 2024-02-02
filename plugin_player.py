#file and library helpers
import importlib
import os
import sys

#pluginplay library
import pluginplay as pp

#kivy helpers
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.filechooser import FileChooserListView
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Line
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import BooleanProperty


#image resizer
from PIL import Image as PILImage

#------------------------TREE/NODE CLASSES---------------------------------

class DraggableImageButton(ButtonBehavior, BoxLayout):
    def __init__(self, node_widget, relative_window, **kwargs):
        super().__init__(**kwargs)

        #the node to update the location
        self.node_widget = node_widget

        #window node belonds in
        self.relative_window = relative_window


        #icon for the drag button
        self.add_widget(Image(source='drag.png'))

    #prepare to drag
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.node_widget.is_dragging = True
            self.node_widget.touch_x = touch.x - self.node_widget.x
            self.node_widget.touch_y = touch.y - self.node_widget.y
            return True
        return super().on_touch_down(touch)

    #update movement on dragging
    def on_touch_move(self, touch):
        if self.node_widget.is_dragging:
            #updates location of the mouse
            new_x = touch.x - self.node_widget.touch_x
            new_y = touch.y - self.node_widget.touch_y

            # Check if the new position is within the boundaries of the relative window
            if 0 <= new_x <= self.relative_window.width - self.node_widget.width:

                #changes position of the connected lines
                for line in self.node_widget.incoming_lines:
                    in_line = line[0]
                    points = in_line.points
                    in_line.points = [new_x + 50, points[1], points[2], points[3]]
                for line in self.node_widget.outgoing_lines:
                    out_line = line[0]
                    points = out_line.points
                    out_line.points = [points[0], points[1], new_x + 50, points[3]]
                
                #changes node position
                self.node_widget.x = new_x

            if 0 <= new_y <= self.relative_window.height - self.node_widget.height:

                #changes the position of connecting lines
                for line in self.node_widget.incoming_lines:
                    in_line = line[0]
                    points = in_line.points
                    in_line.points = [points[0], new_y + 50, points[2], points[3]]
                for line in self.node_widget.outgoing_lines:
                    out_line = line[0]
                    points = out_line.points
                    out_line.points = [points[0], points[1], points[2], new_y + 50]
                
                #changes node position
                self.node_widget.y = new_y

            return True
        return super().on_touch_move(touch)

    #finish dragging process
    def on_touch_up(self, touch):
        if self.node_widget.is_dragging:
            self.node_widget.is_dragging = False
            return True
        return super().on_touch_up(touch)

#a drag-and-drop widget used for nodes in the tree
class DraggableWidget(BoxLayout):
    is_dragging = False
    touch_x = 0
    touch_y = 0

    def __init__(self, **kwargs):

        #the array holders for the visual lines connecting nodes that link outputs and inputs
        self.incoming_lines = []
        self.outgoing_lines = []

        #initializes the BoxLayout that will be draggable
        super().__init__(**kwargs)
class ModuleNode:
    def __init__(self, module, module_name, input_dict, output_dict, submod_dict, description):

        #module components the node holds
        self.module = module
        self.module_name = module_name

        #holds the input keys and descriptions the node needs to run
        self.input_dict = input_dict

        #holds the output keys and descriptions the node outputs after running
        self.output_dict = output_dict

        #holds the submodule keys and descriptions needed for the node to run
        self.submod_dict = submod_dict

        #holds the property type for the module
        self.property_type = None

        #holds the description of the module
        self.description = description

        #holds the widget of the node
        self.module_widget = None

        #holds the widget of the custom declaration of the currently selected input
        self.custom_declaration_widget = None

        #show the mapping of inputs, outputs and submodules used for running the tree
        self.input_map = []
        self.output_map = []
        self.submod_map = []

        #set up the configuration arrays to decide how to run the node
        if self.input_dict:
            for key, value in self.input_dict.items():
                #array is allocated where each index is the input number
                #index will be filled with the inputs value route comes from (node_number, output_number)
                self.input_map.append(None)
        if self.output_dict:
            for key, value in self.input_dict.items():
                #array is allocated where each index is the output number
                #index will be filled with multiple routes the output will have with (node_number, output_number)
                self.output_map.append([])
        if self.submod_dict:
            for key, value in self.submod_dict.items():
                #array is set with the first index value as the key for the submod
                #second index value at index 0 is the name of the submodule to use
                self.submod_map.append((key, None))
    def add_widget(self, widget):
        self.module_widget = widget
class ModuleTree:
    nodes = []
    def add_tree_node(self, node):
        self.nodes.append(node)

#Plugin class containing the modules imported
class PluginInfo:

    #name of the file the plugin came from
    plugin_name = None

    #list of all the module names the plugin holds
    modules = []

    def __init__(self, name, modules):
        self.plugin_name = name
        self.modules = modules

#Class defining the running app
class PluginPlayer(App):

    #The app's module manager
    mm = pp.ModuleManager()

    #list of imported plugins and their modules
    savedPlugins = []

    #list of imported class types
    imported_classes = []

    #saved tree containing the nodes and modules to be ran
    tree = ModuleTree()

    #Popup used throughout the app
    popup = None

    #build the main window from the kv file
    def build(self):
        self.popup = Popup()
        #Window.fullscreen = True
        build = Builder.load_file('multi_sectioned.kv')

        #add logo
        tree_section = build.ids.right_section.ids.tree_section
        image = PILImage.open('NWCHEMEX.png')
        resized_image = image.resize((200, 200))
        resized_image.save('NWCHEMEX_icon.png')
        logo = Image(source='NWCHEMEX_icon.png', size_hint=(None, None), size=(200, 200), pos_hint={'x': .75, 'y': 0})
        tree_section.add_widget(logo)
        return build

    
    #Add a string message to the message section
    def addMessage(self, message):
        #grab message widget
        message_widget = self.root.ids.message_section

        #add the message
        message_widget.ids.message_label.text += f"\n{message}"
        message_widget.scroll_y = 1
    
    #browse for a new file from file system and place in entry
    def browse(self):
        popup = None

        #grab text from entry
        entry_text = self.root.ids.file_entry.ids.file_path_input.text

        #if entry text is a directory, open popup to directory
        if os.path.isdir(entry_text):
            file_chooser = FileChooserListView(path=entry_text)        
        else:
            file_chooser = FileChooserListView()

        #internal function to select the file
        def select_file(instance, selection, *args):
            if selection:
                # Set selected file path in TextInput
                file_entry_widget = self.root.ids.file_entry.ids.file_path_input
                file_entry_widget.text = selection[0] 
                popup.dismiss()
        
        #set up the popup
        popup = Popup(title='Select a file', content=file_chooser, size_hint=(None, None), size=(500, 500))        
        file_chooser.bind(on_submit=select_file)
        popup.open()
    #load in a new plugin
    def plugin_loader(self):
        #grab filepath from the entry
        selected_file_path = self.root.ids.file_entry.ids.file_path_input
        filepath = selected_file_path.text
        selected_file_path.text = ""
        selected_file_path.hint_text = "Enter Filepath/Browsing Directory"
        # Check if the file exists and is a .so file
        if not os.path.isfile(filepath):
            self.addMessage("File does not exist")
        elif not filepath.endswith('.so'):
            self.addMessage("File is not a Plugin (.so) file")
        else:
            # Split the file path into directory and filename
            directory_path, filename = os.path.split(filepath)

            #remove the .so from the filename
            filename = os.path.splitext(filename)[0]

            #add to system path
            sys.path.append(directory_path)

            #import the plugin library
            try:
                lib = importlib.import_module(filename)
                #try to load plugin modules into module manager
                try:
                    lib.load_modules(self.mm)
                    self.addMessage(f"Successfuly loaded {filename} into ModuleManager")

                    #save info of the Plugin and its modules
                    tempMM = pp.ModuleManager()
                    lib.load_modules(tempMM)
                    newPlugin = PluginInfo(filename, tempMM.keys())
                    self.savedPlugins.append(newPlugin)
                    self.pluginView()
                except Exception as e:
                    self.addMessage(f"Could not add {filename} to ModuleManager")
                    self.addMessage(f"{e}")
            except Exception as e:
                self.addMessage(f"Could not import module {filename}: {e}")
                
                
    #delete a preinstalled plugin from the mm and remove the folder
    def delete_plugin(self, instance):
        #dismiss any popup
        self.popup.dismiss()

        #grab folder number and plugin name from the widget's id
        folder_number = int(instance.id)
        plugin = self.savedPlugins[folder_number]
        name = plugin.plugin_name

        #delete dependencies on the tree that are of the plugin's modules
        for module_name in plugin.modules:
            node_number = 0
            for node in self.tree.nodes:
                if not node:
                    pass
                #remove nodes using the plugin's modules
                elif node.module_name == module_name:
                    temp_widget = Widget()
                    temp_widget.id = f'{node_number}'
                    self.remove_node(temp_widget)
            
                #remove all set submodules 
                else:
                    for submodule in node.submod_map:
                        #check if the submodule is set to use the module
                        if submodule[1] == module_name:
                            submodule = (submodule[0], None)
                            self.addMessage(f"Removed Submodule: {submodule[0]}, {module_name} from Node {node_number}")
                node_number += 1

        for i in range(len(self.savedPlugins[folder_number].modules)):
            self.mm.erase(self.savedPlugins[folder_number].modules[i])
        self.savedPlugins[folder_number] = None     
        self.addMessage("Removed Plugin: " + name)
        self.pluginView()
            



    def view_module_info(self, instance):
        #grab info from the instance id's
        module_number = int(instance.id.split()[0])
        plugin_number = int(instance.id.split()[1])
        accessed_in_tree = int(instance.id.split()[2])
        module_name = self.savedPlugins[plugin_number].modules[module_number]
        module = self.mm.at(module_name)

        #find the information of inputs, outputs, submodules, description
        #alert on the messages and stop process if needed info can't be gathered
        outputs = ""
        inputs = ""
        submodules = ""
        description = ""
        try:
            output_dict = module.results()
            for key, value in output_dict.items():
                try:
                    output_add = f"    {key}: {value.description()} \n"
                except:
                    output_add = f"    {key}: description unavailable\n"
                outputs += output_add
        except Exception as e:
            self.addMessage(f"Couldn't find output information: {e}")
        try:
            input_dict = module.inputs()
            for key, value in input_dict.items():
                try:
                    input_add = f"    {key}: {value.description()} \n"
                except:
                    input_add = f"    {key}: description unavailable\n"
                inputs += input_add
        except Exception as e:
            self.addMessage(f"Couldn't find input information: {e}")
        try:     
            submod_dict = module.submods()
            if submod_dict:
                for key, value in submod_dict.items():
                    try:
                        submodule_add = f"    {key}: {value.description()} \n"
                    except:
                        submodule_add = f"    {key} description unavailable"
                    submodules += submodule_add
            else:
                submodules = "    None\n"
        except Exception as e:
            self.addMessage(f"Couldn't find submodule information: {e}")
        try:
            description = module.description()
        except Exception as e:
            description = "Not Supported"
            self.addMessage(f"Couldn't find description: {e}")
        #put into massive string
        full_info = f"Description:{description}\nInputs:\n{inputs}Outputs:\n{outputs}Submods:\n{submodules}"

        #create main frame for popup
        new_frame = BoxLayout(orientation='vertical')
        #add back button
        back_button = Button(text="Back", size_hint=(None,None), size=(50, 20), halign='left', 
                on_press=self.view_modules)
        back_button.id = f'{plugin_number} {accessed_in_tree}'
        new_frame.add_widget(back_button)

        #add info label
        info_label = Label(text=full_info, halign='left', color=(0,0,0,1))
        new_frame.add_widget(info_label)
        scrolling_info = ScrollView(do_scroll_y=True, do_scroll_x=True)
        scrolling_info.add_widget(new_frame)

        #create a popup
        self.popup.dismiss()
        self.popup = Popup(content=scrolling_info, background_color=(255, 255, 255), size_hint=(None,None), 
                size=(self.root.ids.right_section.width, self.root.ids.right_section.height-100), 
                auto_dismiss=False, title=(module_name + " Info"), title_color=(0,0,0,1))
        self.popup.open()

    #view modules from selecting a plugin
    def view_modules(self, instance):

        #close any current popup
        try:
            self.popup.dismiss()
        except:
            pass
        
        #grab folder number from the id
        folder_number = int(instance.id.split()[0])
        accessed_in_tree = int(instance.id.split()[1])

        #exit if back button was pressed from the tree view
        if accessed_in_tree:
            return
        
        #grab pluginSection widget
        plugin_section = self.root.ids.plugin_section

        #create widget to fill with modules
        module_widget = BoxLayout(orientation='vertical', size_hint=(None, None), 
                size=(plugin_section.width - 20, plugin_section.height),spacing=5)
        
        #add a delete plugin button
        delete_plugin = Button(text='Delete Plugin', color=(0,0,0,1), size_hint_y=None, height=20, 
                on_press=self.delete_plugin)

        #use id as a value holder for the folder number
        delete_plugin.id = f'{folder_number}'
        module_widget.add_widget(delete_plugin)

        
        #add each of the modules that are in the plugin
        module_amount = len(self.savedPlugins[folder_number].modules)
        for i in range(module_amount):
            #create main holding box
            view_module = BoxLayout(orientation='horizontal', size_hint_y=None, height=30, spacing=5)

            #add the name of the module
            module_name = Label(text=self.savedPlugins[folder_number].modules[i], color=(0,0,0,1), size_hint_x=1/2)
            view_module.add_widget(module_name)

            #add the add button to add to the tree
            add_to_tree = Button(text='Add', size_hint_x=1/10, on_press=self.add_node)
            #set the id for the module number in the plugin
            add_to_tree.id = f'{i} {folder_number}'
            view_module.add_widget(add_to_tree)

            #add the info button for extended information
            view_info = Button(text='Info', size_hint_x=1/10, on_press=self.view_module_info)
            #set the id for the module number and plugin number and 0 (accessed in folder)
            view_info.id = f'{i} {folder_number} 0'
            view_module.add_widget(view_info)


            #add the module widget to the main view
            module_widget.add_widget(view_module)
        
        #fill in the empty scroll space
        space_filler = Label(height=plugin_section.height)
        module_widget.add_widget(space_filler)

        #add scrolling capabilities
        scroll_view = ScrollView(scroll_y=1, do_scroll_y=True)
        scroll_view.id = "scroll"
        scroll_view.add_widget(module_widget)

        #create and open popup
        self.popup = Popup(content=scroll_view, background_color=(255, 255, 255), size_hint=(None, None), 
                size=plugin_section.size, auto_dismiss=True, title=self.savedPlugins[folder_number].plugin_name, 
                title_color=(0,0,0,1))
        self.popup.id = f'{folder_number}'
        self.popup.open()

    #update the loaded plugin visuals
    def pluginView(self):
        #grab the plugin section
        plugin_widget = self.root.ids.plugin_section

        #clear the plugin section's previous widgets
        plugin_widget.clear_widgets()
        
        #Set the folder size
        image = PILImage.open('folder_icon.png')
        new_width, new_height = plugin_widget.width/4-10, plugin_widget.width/4-10
        resized_image = image.resize((int(new_width), int(new_height)))
        resized_image.save('button_folder.png') 

        number_of_added_plugins = 0
        for i in range(len(self.savedPlugins)):

            #skip when encountering a deleted plugin
            if not self.savedPlugins[i]:
                continue
            
            #add image and route the popup function when pressed
            image_widget = Button(on_press=self.view_modules, background_normal='button_folder.png', 
                    size_hint=(None,None), size=(new_width, new_height), text=self.savedPlugins[i].plugin_name, 
                    font_size=11, text_size=(new_width, None), halign='center', valign='bottom')
            image_widget.id = f'{i} 0'
            plugin_widget.add_widget(image_widget)
            number_of_added_plugins += 1

        #fill in space for sizing
        for i in range(3 - (number_of_added_plugins % 4) % 4):
            extra_widgets = BoxLayout(size_hint=(None,None), size=(new_width, new_height))
            plugin_widget.add_widget(extra_widgets)

    #-----------------------------TREE METHODS--------------------------------------------
    #delete the entire tree and its edges and nodes
    def delete_tree(self):
        #remove each node one by one
        self.addMessage("Initiating Tree Removal")
        for i in range(len(self.tree.nodes)):
            if self.tree.nodes[i]:
                temp_widget = Widget()
                temp_widget.id = f'{i}'
                self.remove_node(temp_widget)
        self.tree.nodes = []
        self.addMessage("Removed Tree") 
    
    #adds a new node to the tree section
    def add_node(self, instance):
        #grab info from instance
        self.popup.dismiss()
        module_number = int(instance.id.split()[0])
        plugin_number = int(instance.id.split()[1])
        module_name = self.savedPlugins[plugin_number].modules[module_number]
        module = self.mm.at(module_name)

        #find the information of inputs, outputs, submodules, description
        try:
            output_dict = module.results()
        except Exception as e:
            self.addMessage(f"Couldn't find output information: {e}")
            return
        try:
            input_dict = module.inputs()
        except Exception as e:
            self.addMessage(f"Couldn't find input information: {e}")
            return
        try:     
            submod_dict = module.submods()
        except Exception as e:
            self.addMessage(f"Couldn't find submodule information: {e}")
            return
        try:
            description = module.description()
        except Exception as e:
            description = "Not Supported"
            self.addMessage(f"Couldn't find description: {e}")

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
                halign='center', valign='center', text=f"{module_name} ({len(self.tree.nodes)})")
        widget_label.text_size=widget_label.size
        basis_box.add_widget(widget_label)

        #add box for option buttons
        options = BoxLayout(orientation='vertical', size_hint=(None,None), width=20, height=80,spacing=0)

        options.add_widget(Widget(size_hint_y=None, height=10))
        
        image = PILImage.open('drag_icon.png')
        resized_image = image.resize((20, 20))
        resized_image.save('drag.png') 
        navigate_button = DraggableImageButton(node_widget=node_widget, 
                relative_window=self.root.ids.right_section.ids.tree_section, size_hint_y=None, height=20)
        options.add_widget(navigate_button)
        
        image = PILImage.open('info_icon.png')
        resized_image = image.resize((20, 20))
        resized_image.save('info.png') 
        info_button = Button(background_normal='info.png', on_press=self.view_module_info, 
                size_hint_y=None, height=20)
        #add id for module number, plugin number, and 1 (accessed in treeview)
        info_button.id = f'{module_number} {plugin_number} 1'
        options.add_widget(info_button)

        image = PILImage.open('remove_icon.png')
        resized_image = image.resize((20, 20))
        resized_image.save('remove.png') 
        remove_button = Button(background_normal='remove.png', on_press=self.remove_node, 
                size_hint_y=None, height=20)
        remove_button.id = f'{len(self.tree.nodes)}'
        options.add_widget(remove_button)

        options.add_widget(Widget(size_hint_y=None, height=10))

        basis_box.add_widget(options)
        node_widget.add_widget(basis_box)

        #add configure button
        config_button = Button(size_hint=(None,None), height=20, width=90, valign='center', 
                text='Configure', on_press = self.view_config)
        config_button.id = f'{len(self.tree.nodes)}'
        node_widget.height += 20
        node_widget.add_widget(config_button)
        #add it to the screen and the main lists
        node_widget.pos = (1,1)
        self.root.ids.right_section.ids.tree_section.add_widget(node_widget)
        new_node.add_widget(node_widget)
        self.tree.add_tree_node(new_node)
        self.addMessage(f"Added new node {module_name} to the tree")

    #remove a node's widget and connecting edges
    def remove_node(self, instance):
        #get the node number
        node_number = int(instance.id)
        node = self.tree.nodes[node_number]

        self.addMessage(f"Initiating removal of {node.module_name} Node: {node_number}")

        #remove the widget
        self.root.ids.right_section.ids.tree_section.remove_widget(node.module_widget)

        #remove input edges that are mapped
        input_number = 0
        for input_edge in node.input_map:
            if input_edge and input_edge[0] != -1:
                input_key = list(node.input_dict.keys())[input_number]
                #find output node its mapped to
                output_node_number = input_edge[0]
                output_number = input_edge[1]
                output_node = self.tree.nodes[output_node_number]
                output_key = list(output_node.output_dict.keys())[output_number]

                #delete old lines connecting to the output node
                for line_set in output_node.module_widget.outgoing_lines:
                    if line_set[1] == (node_number, input_number):
                        output_node.module_widget.outgoing_lines.remove(line_set)
                        self.root.ids.right_section.ids.tree_section.canvas.before.remove(line_set[0])

                #remove its connection and create message
                output_node.output_map[output_number].remove((node_number, input_number))
                self.addMessage(f"Removed Output {output_key} of Node {output_node_number} to {input_key} from Node {node_number}")
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
                    input_node = self.tree.nodes[input_node_number]
                    input_key = list(input_node.input_dict.keys())[input_number]
                    
                    #delete old lines connecting to the input node
                    for line_set in input_node.module_widget.incoming_lines:
                        if line_set[1] == (node_number, output_number):
                            input_node.module_widget.incoming_lines.remove(line_set)
                            self.root.ids.right_section.ids.tree_section.canvas.before.remove(line_set[0])

                    #remove its connection and create message
                    input_node.input_map[input_number] = None
                    self.addMessage(f"Removed Input: {input_key} of Node {input_node_number} to {output_key} from Node {node_number}")
            output_number += 1

        #delete data from tree list
        self.tree.nodes[node_number] = None

        self.addMessage(f"Removed {node.module_name} Node: {node_number} from the tree")
        return

    def view_config(self, instance):
        
        #attempt to close any popups
        try:
            self.popup.dismiss()
        except:
            pass
        #grab the node's index and its corresponding module
        node_number = int(instance.id)
        node = self.tree.nodes[node_number]
        module = node.module
        module_name = node.module_name

        #create main widget to hold everything
        config_widget = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        config_widget.bind(minimum_height=config_widget.setter('height'))
        
        #add buffer for scrollview
        config_widget.add_widget(Widget(size_hint_y=None, height=100))


        #-------------------------INPUT CONFIGURATION ---------------------


        #create a widget to display the inputs
        input_widget = BoxLayout(orientation = 'vertical',spacing=0, size_hint_y=None)
        input_label = Label(text="Input Configuration", valign= 'center', halign='center', 
                font_size='20sp', color=(0,0,0,1), size_hint_y =None, height=30)
        input_widget.add_widget(input_label)

        #add each input and a text input to add it
        for i in range(len(node.input_dict.items())):
            #grab the key for the input
            key = list(node.input_dict.keys())[i]
            try:
                value_description = list(node.input_dict.values())[i].description()
            except:
                value_description = "description unavailable"
            
            #create the box to hold the input's options
            input_list = BoxLayout(orientation='horizontal', size_hint_y=None, height=30, spacing=0)

            #create label for the name of the input
            input_list.add_widget(Label(text=key, size_hint_x=1/5, halign='left', color=(0,0,0,1)))

            #create label for the description
            input_description = Label(text=f'{value_description}', halign='left', 
                    color=(0,0,0,1), size_hint_x =3/5)
            input_list.add_widget(input_description)
            
            #add preselected input if done
            if node.input_map[i]:
                #Show custom input
                if node.input_map[i][0] == -1:
                    input_description.text = f'Set: {node.input_map[i][2]}'
                #Show input route
                else:
                    input_description.text = f'Set: {self.tree.nodes[node.input_map[i][0]].module_name}({node.input_map[i][0]}), Output: {node.input_map[i][1]}'


            #create the add button that routes to an adding input function
            input_add_button = Button(text='Set', size_hint_x=1/5)
            input_add_button.id = f'{node_number} {i}'
            input_add_button.bind(on_press=self.add_input)
            input_list.add_widget(input_add_button)

            #add it to main input holder
            input_widget.add_widget(input_list)
        #add to main configuration holder
        config_widget.add_widget(input_widget)


        #---------------------------OUTPUT CONFIGURATION---------------------------------------


        #create a widget to display the outputs
        output_widget = BoxLayout(orientation = 'vertical',spacing=0, size_hint_y=None)
        output_label = Label(text="Output Configuration", valign= 'center',halign='center', 
                font_size='20sp', color=(0,0,0,1))
        output_widget.add_widget(output_label)

        #add each output and a text output to add it
        for i in range(len(node.output_dict.items())):
            #grab the key for the output
            key = list(node.output_dict.keys())[i]
            try:
                value_description = list(node.output_dict.values())[i].description()
            except:
                value_description = "description unavailable"
            
            #create the box to hold the output's options
            output_list = BoxLayout(orientation='horizontal', size_hint_y=None, height=30, spacing=0)

            #create label for the name of the output
            output_list.add_widget(Label(text=key, size_hint_x=1/5, halign='left', color=(0,0,0,1)))

            #create label for output description
            output_description = Label(text=f'{value_description}', halign='left', 
                    color=(0,0,0,1), size_hint_x =4/5)
            output_list.add_widget(output_description)

            #add preselected output paths if done
            output_edges = "Set: "
            output_set = False
            for output_edge in node.output_map[i]:
                output_set = True
                output_edges += f'{self.tree.nodes[output_edge[0]].module_name}({output_edge[0]}) Input: {output_edge[1]}   '
            if output_set:
                output_description.text = output_edges

            #add it to main output holder
            output_widget.add_widget(output_list)
        #add to main configuration holder
        config_widget.add_widget(output_widget)


        #-----------------------PROPERTY TYPE CONFIGURATION-----------------------------------

        #create a widget to display the property type chosen
        ptype_widget = BoxLayout(orientation='vertical', spacing=0, size_hint_y=None)
        ptype_widget.add_widget(Label(text="Property Type Configuration", valign= 'center', halign='center', 
                font_size='20sp', color=(0,0,0,1)))

        #create a label widget showing the current set property type
        if node.property_type == None:
            set_value = "No Property Type Set"
        else:
            set_value = node.property_type[0]
        ptype_widget.add_widget(Label(text=set_value, halign='left', color=(0,0,0,1)))

        #create an entry to declare a property type
        custom_ptype = BoxLayout(orientation='horizontal', spacing=0)
        text_entry = TextInput(hint_text="ex: Force()", size_hint_x=3/5, multiline=False)

        #add text entry to the node's properties
        node.custom_declaration_widget = text_entry
        custom_ptype.add_widget(text_entry)

        #add button to set the property type
        custom_entry_button = Button(text="Set", size_hint_x=1/5, on_press=self.link_property_type)
        
        #add button to view the class types
        class_types_button = Button(text="Class Types", size_hint_x = 1/5, on_press=self.class_types)

        #id to trigger the custom input response
        custom_entry_button.id = f'{node_number}'
        class_types_button.id = f'{node_number} {-1}'
        custom_ptype.add_widget(custom_entry_button)
        custom_ptype.add_widget(class_types_button)
        ptype_widget.add_widget(custom_ptype)

        config_widget.add_widget(ptype_widget)


        #-----------------------------SUBMODULE CONFIGURATION--------------------------------


        #create a widget to display the submodules
        submods_widget = BoxLayout(orientation='vertical', spacing=0, size_hint_y=None)
        submod_label = Label(text="Submodule Configuration", valign= 'center', halign='center', 
                font_size='20sp', color=(0,0,0,1))
        submods_widget.add_widget(submod_label)
        
        #add each submodule and a text input to add it
        for i in range(len(node.submod_dict.items())):
            #grab the key for the submodule
            key = list(node.submod_dict.keys())[i]
            try:
                value_description = list(node.submod_dict.values())[i].description()
            except:
                value_description = "description unavailable"
            
            #create the box to hold the submod's options
            submod_list = BoxLayout(orientation='horizontal', size_hint_y=None, height=30, spacing=0)

            #create label for the name of the submodule
            submod_list.add_widget(Label(text=key, size_hint_x=1/5, halign='left', color=(0,0,0,1)))

            #create label for submodule description
            submod_description = Label(text=f'{value_description}', halign='left', 
                    color=(0,0,0,1), size_hint_x =3/5)
            submod_list.add_widget(submod_description)
            
            #add preselected submodule if done
            if node.submod_map[i][1]:
                submod_description.text = f'Set: {node.submod_map[i][1]}'

            #create the add button that routes to an adding submodule function
            submod_add_button = Button(text='Set', size_hint_x=1/5)
            submod_add_button.id = f'{node_number} {i}'
            submod_add_button.bind(on_press=self.add_submod)
            submod_list.add_widget(submod_add_button)

            #add it to main submodule holder
            submods_widget.add_widget(submod_list)
        
        #add a "no submodules" label if there are none
        if len(node.submod_dict.items()) == 0:
            submods_widget.add_widget(Label(text="No Submodules", halign='left', color=(0,0,0,1)))
        #add to main configuration holder
        config_widget.add_widget(submods_widget)

        #add buffer for scrollview
        config_widget.add_widget(Widget(size_hint_y=None, height=100))

        #add scrolling capabilities
        scroll_view = ScrollView(do_scroll_x=False, do_scroll_y=True, scroll_type=['bars'])
        scroll_view.add_widget(config_widget)

        self.popup = Popup(content=scroll_view, size_hint=(None,None), size=(800, 500), 
                background_color=(255, 255, 255), auto_dismiss=True, title=f'Configuration for {module_name} ({node_number})', 
                title_color=(0,0,0,1))
        self.popup.open()
        return
    #attempts to add an entered input
    def add_input(self, instance):
        #grab needed info form the id and 
        node_number = int(instance.id.split()[0])
        key_number = int(instance.id.split()[1])
        node = self.tree.nodes[node_number]
        module_name = node.module_name
        key = list(node.input_dict.keys())[key_number]

        #start creating a widget for selecting an input
        select_input = BoxLayout(orientation='vertical',size_hint=(None,None), size=(800,500), spacing=0)

        #keep track of height for scrolling padding
        height = 0

        #add back button
        back_button = Button(text="Back", size_hint=(None,None), size=(40,20), on_press=self.view_config)
        back_button.id = f'{node_number}'
        select_input.add_widget(back_button)
        height +=20

        #add an option to declare your own input
        select_input.add_widget(Label(text="Declare input value using Python", color=(0,0,0,1), 
                size_hint_y=None, height=20, halign='center'))
        height += 20
        custom_input = BoxLayout(orientation='horizontal', spacing=0, size_hint=(None,None), size=(750,30))
        text_entry = TextInput(hint_text="ex: Point([-1.0, -1.0, -1.0])", size_hint_x=9/10, multiline=False)

        #add text entry to the node's properties
        node.custom_declaration_widget = text_entry
        custom_input.add_widget(text_entry)
        custom_entry_button = Button(text="Set", size_hint_x=1/10, on_press=self.link_input)

        #id to trigger the custom input response
        custom_entry_button.id = f'{-1} {-1} {node_number} {key_number}'
        custom_input.add_widget(custom_entry_button)

        #add button to import a new class type
        class_types_button = Button(text = "Class Types", size_hint_x=3/10, on_press=self.class_types)
        class_types_button.id = f'{node_number} {key_number}'
        custom_input.add_widget(class_types_button)

        select_input.add_widget(custom_input)
        height += 30

        output_node_number = 0
        output_number = 0
        #grab each output in each node on the tree
        for node_iter in self.tree.nodes:
            
            #ignore deleted nodes
            if not node_iter:
                output_node_number += 1
                continue
            #ignore same node
            if node_iter == node:
                output_node_number += 1
                continue

            #add node label
            select_input.add_widget(Label(text=f"Node {output_node_number}: {node_iter.module_name}", 
                    size_hint_y=None, height=20, halign='left', font_size="15sp", color=(0,0,0,1)))
            height += 30

            output_number = 0
            for output in list(node_iter.output_dict.keys()):
                #create an output with an add button
                output_box = BoxLayout(orientation='horizontal', size_hint=(None,None), size=(750,30), spacing=0)
                output_box.add_widget(Label(text=output, color=(0,0,0,1), halign='left', 
                        size_hint_x= 9/10))

                add_button = Button(text="Set", size_hint_x=1/10, on_press=self.link_input)
                #add id to identify the submodule from the node, and the module to be the submodule
                add_button.id = f'{output_node_number} {output_number} {node_number} {key_number}'
                output_box.add_widget(add_button)

                #add to main box
                select_input.add_widget(output_box)
                height += 30
                output_number += 1
            select_input.add_widget(Widget(size_hint_y=None, height=20))
            height += 20
            output_node_number += 1
            

        #add scrolling capabilities
        if height < 450:
            select_input.add_widget(Widget(size_hint_y=None, height=(450-height)))
        scroll_view = ScrollView(scroll_y=0, do_scroll_y=True, size_hint=(None, None), size=(800,500), scroll_type=['content'])
        scroll_view.add_widget(select_input)
        self.popup.dismiss()
        self.popup = None
        self.popup = Popup(content=scroll_view, size_hint=(None,None), size=(800,500), 
                background_color=(255, 255, 255), auto_dismiss=False, title=f'Selecting input: {key}', 
                title_color=(0,0,0,1))
        self.popup.open()       

        return
    #attempts to add an entered submodule to a node
    def add_submod(self, instance):
        #grab needed info form the id and 
        node_number = int(instance.id.split()[0])
        key_number = int(instance.id.split()[1])
        node = self.tree.nodes[node_number]
        module_name = node.module_name
        key = list(node.submod_dict.keys())[key_number]

        #start creating a widget for selecting a submodule
        select_submod = BoxLayout(orientation='vertical',size_hint=(None,None), size=(800,500), spacing=0)
        
        #keep track of height for scrolling padding
        height = 0
        #add back button
        back_button = Button(text="Back", size_hint=(None,None), size=(40,20), on_press=self.view_config)
        back_button.id = f'{node_number}'
        select_submod.add_widget(back_button)
        height +=20

        plugin_number = 0
        module_number = 0
        #for each module in each plugin, place a module and option to add
        for plugin in self.savedPlugins:

            #continue if the plugin was deleted
            if not plugin:
                continue
            
            for module in plugin.modules:
                #create a module with an add button
                module_box = BoxLayout(orientation='horizontal', size_hint=(None,None), size=(750,30), spacing=0)
                module_box.add_widget(Label(text=module, color=(0,0,0,1), halign='left', 
                        size_hint_x= 9/10))

                add_button = Button(text="Set", size_hint_x=1/10, on_press=self.link_submod)
                #add id to identify the submodule from the node, and the module to be the submodule
                add_button.id = f'{node_number} {key_number} {plugin_number} {module_number}'
                module_box.add_widget(add_button)

                #add to main box
                select_submod.add_widget(module_box)
                height += 30

                module_number += 1
        plugin_number += 1
        module_number = 0

        #add scrolling capabilities
        if height < 450:
            select_submod.add_widget(Widget(size_hint_y=None, height=(450-height)))
        scroll_view = ScrollView(scroll_y=0, do_scroll_y=True, size_hint=(None, None), size=(800,500), scroll_type=['content'])
        scroll_view.add_widget(select_submod)
        self.popup.dismiss()
        self.popup = None
        self.popup = Popup(content=scroll_view, size_hint=(None,None), size=(800,500), 
                background_color=(255, 255, 255), auto_dismiss=False, title=f'Selecting submodule: {key}', 
                title_color=(0,0,0,1))
        self.popup.open()
    
    def link_input(self, instance):
        #get info from instance id
        output_node_number = int(instance.id.split()[0])
        output_number = int(instance.id.split()[1])
        input_node_number = int(instance.id.split()[2])
        input_number = int(instance.id.split()[3])
        input_node = self.tree.nodes[input_node_number]
        input_key = list(input_node.input_dict.keys())[input_number]

        #check if input was previously set and wasn't a custom value
        if input_node.input_map[input_number] and input_node.input_map[input_number][0] != -1:
            #find previous output
            previous_output_node_number = input_node.input_map[input_number][0]
            previous_output_number = input_node.input_map[input_number][1]
            previous_output_node = self.tree.nodes[previous_output_node_number]
            previous_output_key = list(previous_output_node.output_dict.keys())[previous_output_number]
            
            #delete old lines connecting to the input node
            for line_set in input_node.module_widget.incoming_lines:
                if line_set[1] == (previous_output_node_number, previous_output_number):
                    input_node.module_widget.incoming_lines.remove(line_set)
                    self.root.ids.right_section.ids.tree_section.canvas.before.remove(line_set[0])

            #delete old lines connecting to the output node
            for line_set in previous_output_node.module_widget.outgoing_lines:
                if line_set[1] == (input_node_number, input_number):
                    previous_output_node.module_widget.outgoing_lines.remove(line_set)
                    self.root.ids.right_section.ids.tree_section.canvas.before.remove(line_set[0])

            #remove the previous output edge
            previous_output_node.output_map[previous_output_number].remove((input_node_number, input_number))
            self.addMessage(f"Removed input {input_key} of Node {input_node_number} to {previous_output_key} from Node {previous_output_node_number}")
        
        #load in a custom input 
        if output_node_number == -1:

            #grab remaining values
            input_node = self.tree.nodes[input_node_number]
            input_key = list(input_node.input_dict.keys())[input_number]

            #grab input from currently opened popup entry
            custom_declaration = input_node.custom_declaration_widget.text

            #try to assign the variable
            #may be a security risk as it evaluates injected code
            try:
                custom_input = eval(custom_declaration, sys.modules['__main__'].__dict__)
                input_node.input_map[input_number] = (-1, custom_input, custom_declaration)
                self.addMessage(f"Set input {input_key} of Node {input_node_number} with Value: {custom_declaration}")
            except Exception as e:
                self.addMessage(f"Could not set input {custom_declaration}: {e}")

        #set a new edge and input route
        else:
            #get remaining information
            output_node = self.tree.nodes[output_node_number]
            output_key = list(output_node.output_dict.keys())[output_number]

            #set the edges of the nodes
            output_node.output_map[output_number].append((input_node_number, input_number))
            input_node.input_map[input_number] = (output_node_number, output_number)

            #add a line connecting the nodes
            connecting_line = Line(points=[input_node.module_widget.x + 50, input_node.module_widget.y+50, 
                    output_node.module_widget.x+50, output_node.module_widget.y+50], width=2)
            input_node.module_widget.incoming_lines.append((connecting_line, (output_node_number, output_number)))
            output_node.module_widget.outgoing_lines.append((connecting_line, (input_node_number, input_number)))
            #add the line to the layout
            self.root.ids.right_section.ids.tree_section.canvas.before.add(Color(0,0,0))
            self.root.ids.right_section.ids.tree_section.canvas.before.add(connecting_line)
            #display message
            self.addMessage(f"Set input {input_key} of Node {input_node_number} to {output_key} from Node {output_node_number}")

        #go back to view_config
        temp_widget = Widget()
        temp_widget.id = f'{input_node_number}'
        self.view_config(temp_widget)
    
    #attempts to add a property type to a node
    def link_property_type(self, instance):
        
        #grab info from the instance id and text entry
        node_number = int(instance.id)
        node = self.tree.nodes[node_number]
        custom_declaration = node.custom_declaration_widget.text

        #try to assign the variable
        #may be a security risk as it evaluates injected code
        try:
            ptype = eval(custom_declaration, sys.modules['__main__'].__dict__)
            node.property_type = (custom_declaration, ptype)
            self.addMessage(f"Set property type of Node {node_number} with Value: {custom_declaration}")
        except Exception as e:
            self.addMessage(f"Could not set property type {custom_declaration}: {e}")
        self.view_config(instance)

    #attempts to add a submodule type to a node
    def link_submod(self, instance):
        
        #get info from the instance id
        node_number = int(instance.id.split()[0])
        node = self.tree.nodes[node_number]
        module_name = node.module_name
        key_number = int(instance.id.split()[1])
        key_name = list(node.submod_dict.keys())[key_number]
        plugin_number = int(instance.id.split()[2])
        submodule_number = int(instance.id.split()[3])
        submodule_name = self.savedPlugins[plugin_number].modules[submodule_number]

        try:
            self.mm.change_submod(module_name, key_name, submodule_name)
            self.addMessage(f"Added submodule {submodule_name} to {key_name} of {module_name}")
            node.submod_map[key_number] = (key_name, submodule_name)
        except Exception as e:
            self.addMessage(f"Could not add submodule {submodule_name} to {key_name} of {module_name}\n {e}")

        #go back to view_config
        temp_widget = Widget()
        temp_widget.id = f'{node_number}'
        self.view_config(temp_widget)

    #show a popup to see all class types imported
    def class_types(self, instance):

        #grab needed info
        node_number = int(instance.id.split()[0])
        key_number = int(instance.id.split()[1])

        #start creating the new popup
        types_box = BoxLayout(orientation='vertical')

        #height of the popup to be updated later to fill whitespace
        height = 0

        #create a back button
        #return to main config page if it is a property type
        if(key_number == -1):
            back_button = Button(text="Back", size_hint=(None,None), size=(40,20), on_press=self.view_config)
            back_button.id = f'{node_number}'
        #if its form the add input page, return back there
        else:
            back_button = Button(text="Back", size_hint=(None,None), size=(40,20), on_press=self.add_input)
            back_button.id = f'{node_number} {key_number}'
        types_box.add_widget(back_button)
        height += 20
        
        types_box.add_widget(Label(text="Add a new class type by filling in the blanks separated by a space", color=(0,0,0,1),
                size_hint_y=None, height=20))
        
        height += 20

        
        #create the entry to add an extra input
        new_type = BoxLayout(orientation='horizontal', size_hint_y=None, height=35, spacing = 0)
        new_type_entry = TextInput(hint_text="from _____ import _____", multiline=False, size_hint_x=9/10)
        new_type.add_widget(new_type_entry)

        #set as global to pull from it when its submitted
        self.custom_declaration_widget = new_type_entry

        #add an import button
        add_button = Button(text="Import",size_hint_x = 1/10, on_press=self.new_type)
        #if its a property type assignt the id to route back to view_config
        if(key_number == -1):
            add_button.id = f'{node_number} {-1}'
        #otherwise route to input page
        else:
            add_button.id = f'{node_number} {key_number}'
        new_type.add_widget(add_button)

        types_box.add_widget(new_type)
        height += 35

        types_box.add_widget(Label(text="Imported Types", font_size="20sp", size_hint_y=None, height=20))
        height += 20

        for imported_type in self.imported_classes:
            types_box.add_widget(Label(text=imported_type, size_hint_y=None, height=15, color=(0,0,0,1)))
            height += 15
        
        #add scrolling capabilities
        if height < 450:
            types_box.add_widget(Widget(size_hint_y=None, height=(450-height)))
        scroll_view = ScrollView(scroll_y=0, do_scroll_y=True, scroll_type=['content'])
        scroll_view.add_widget(types_box)

        #close and change popup
        self.popup.dismiss()
        self.popup = Popup(content=scroll_view, size_hint=(None,None), size=(800,500), 
                background_color=(255, 255, 255), auto_dismiss=False, title=f'Class Types', 
                title_color=(0,0,0,1))
        self.popup.open()

    #define a new class type for custom inputs and property types
    def new_type(self, instance):
        try:
            import_name = self.custom_declaration_widget.text.split()[0]
            class_name = self.custom_declaration_widget.text.split()[1]
            if class_name in self.imported_classes:
                self.addMessage(f"Class type {class_name} previously imported")
                return
        except Exception as e:
            self.addMessage("Invalid Entry, enter the blanks with a space in between from the Python import statement")
            self.addMessage(e)
            return
        try:
            #import the library
            lib = importlib.import_module(import_name)

            #create an instance
            class_instance = getattr(lib,class_name)

            # Add the class to the __main__ module's namespace and list of loaded class types
            setattr(sys.modules['__main__'], class_name, class_instance)
            self.imported_classes.append(class_name)

            #send success message
            self.addMessage(f"Imported class type {class_name}")

        except Exception as e:
            #Failure Message
            self.addMessage(f"Couldn't import type {class_name}: {e}")
        
        #recall the popup to update the newly loaded values and show hint text
        self.class_types(instance)


        
    #run the series of nodes through the connected tree
    def run_tree(self):
        #grab the tree
        tree = self.tree
        nodes = self.tree.nodes

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
                    self.addMessage(f"Run Failure: {node.module_name}({nodes.index(node)}) has a missing input")
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
                    self.addMessage(f"Run Failure: {node.module_name}({nodes.index(node)} has missing submodule")
                    return

            #check if property type is set
            if not node.property_type:
                self.addMessage(f"Run Failure: {node.module_name}({nodes.index(node)}) has no property type set")
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
            self.addMessage("Could not find starting node with no routed inputs")
            return
        
        #do a dfs search
        dfs_result = self.dfs_traversal(nodes, dfs_stack, visited)

        #stop if no run order was given
        if not dfs_result:
            return
        
        #Print success and show run order
        self.addMessage("Successful initial scan of the tree")
        run_order = "Running in order: "
        for next_node in dfs_result:
            run_order += f"{next_node.module_name}({nodes.index(next_node)}), "
        run_order[:-2]
        self.addMessage(run_order)

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
                    self.mm.change_submod(run_node.module_name, submod_set[0], submod_set[1])
                except Exception as e:
                    self.addMessage(f"Couldn't add submodule {submod_set[0]} to {run_node.module_name}")
                    self.addMessage(f"Aborting tree run")
                    return

            
            #attempt to run the module with the inputs
            try:
                #Implement a way to select the property type using the class types imports
                output = self.mm.at(run_node.module_name).run_as(run_node.property_type[1], *run_inputs)
                self.addMessage(f"{run_node.module_name}({nodes.index(run_node)}) Output: {output}")
                saved_outputs[nodes.index(run_node)].append(output)
            except Exception as e:
                self.addMessage(f"Could not run {run_node.module_name}({nodes.index(run_node)}): {e}")
                self.addMessage(f"Aborting tree run")
                return              
        self.addMessage("Successfully ran tree")      
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
                next_node = self.tree.nodes[next_node_number]

                #check if the next node has already been processed by this node (two outputs from this node mapped to next node)
                if next_node in routed:
                    continue

                #dependency of current node can be ignored (already satisfied)
                if next_node == current_node:
                    continue

                #check if node has already been processed by a different branch
                if next_node in visited:
                    
                    #back edge / cycle detected
                    self.addMessage(f"Cycle in tree detected from {next_node.module_name}({next_node_number}) to {current_node.module_name}({nodes.index(current_node)}))")
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
                    dependent_node = self.tree.nodes[input[0]]

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

        




if __name__ == '__main__':
    PluginPlayer().run()