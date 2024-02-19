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

#an image button used to drag a module node within the tree section
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

#Defines the visual element of a module as a node within a tree and its connections for run time
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