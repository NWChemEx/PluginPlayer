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

from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput


class DraggableImageButton(ButtonBehavior, BoxLayout):
    """An Image button used to drag a module node and is restricted within the tree section

    :param ButtonBehavior: The Kivy behavior for modifying a Button class
    :type ButtonBehavior: kivy.uix.behaviors.ButtonBehavior
    :param BoxLayout: The Kivy layout for arranging multiple widgets in one direction
    :type BoxLayout: kivy.uix.boxlayout.BoxLayout
    """

    def __init__(self, node_widget, relative_window, **kwargs):
        """Initialization of the DraggableImage button

        :param node_widget: the widget you want to be able to drag
        :type node_widget: Widget
        :param relative_window: The restricting window where it can be dragged in
        :type relative_window: RelativeWindow
        """
        super().__init__(**kwargs)

        #the node to update the location
        self.node_widget = node_widget

        #window node belonds in
        self.relative_window = relative_window

        #icon for the drag button
        self.add_widget(Image(source='src/pluginplayer/assets/drag.png'))

    def on_touch_down(self, touch):
        """Prepare for a widget to be dragged

        This method is called when a touch event occurs. It checks whether the touch point is within
        the boundaries of the widget, and if so, it prepares the widget for dragging by setting
        necessary attributes.

        :param touch: The point where a user has started clicking
        :type touch: kivy.core.window.Event
        :return: Returns True if the touch event is within the widget's boundaries, False otherwise.
        :rtype: bool
        """
        if self.collide_point(*touch.pos):
            self.node_widget.is_dragging = True
            self.node_widget.touch_x = touch.x - self.node_widget.x
            self.node_widget.touch_y = touch.y - self.node_widget.y
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        """Update the widget's position during a dragging motion.

        This method is called when a touch move event occurs, and it updates the position of the widget
        based on the user's dragging motion. It also adjusts the position of connected lines if the new
        widget position is within the boundaries of the relative window.

        :param touch: The touch event containing information about the user input.
        :type touch: kivy.core.window.Event
        :return: Returns True if the widget is currently being dragged, False otherwise.
        :rtype: bool
        """
        if self.node_widget.is_dragging:
            #updates location of the mouse
            new_x = touch.x - self.node_widget.touch_x
            new_y = touch.y - self.node_widget.touch_y

            # Check if the new position is within the boundaries of the relative window
            x_within_bounds = 0 <= new_x <= self.relative_window.width - self.node_widget.width
            y_within_bounds = 0 <= new_y <= self.relative_window.height - self.node_widget.height
            if x_within_bounds or y_within_bounds:
                #changes position of the connected lines
                for line in self.node_widget.incoming_lines:
                    in_line = line[0]
                    points = in_line.points
                    x1 = new_x + 50 if x_within_bounds else points[0]
                    y1 = new_y + 50 if x_within_bounds else points[1]
                    in_line.points = [x1, y1, points[2], points[3]]
                for line in self.node_widget.outgoing_lines:
                    out_line = line[0]
                    points = out_line.points
                    x2 = new_x + 50 if x_within_bounds else points[2]
                    y2 = new_y + 50 if x_within_bounds else points[3]
                    out_line.points = [points[0], points[1], x2, y2]
                #changes node position
                if x_within_bounds:
                    self.node_widget.x = new_x
                if y_within_bounds:
                    self.node_widget.y = new_y

            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        """Handle the completion of a dragging motion.

        This method is called when a touch up event occurs, signifying the end of a dragging motion.
        It resets the widget's dragging state, indicating that the dragging operation has concluded.

        :param touch: The touch event containing information about the user input.
        :type touch: kivy.core.window.Event
        :return: Returns True if the widget was previously being dragged, False otherwise.
        :rtype: bool
        """
        if self.node_widget.is_dragging:
            self.node_widget.is_dragging = False
            return True
        return super().on_touch_up(touch)


#a drag-and-drop widget used for nodes in the tree
class DraggableWidget(BoxLayout):
    """A drag-and-drop widget used for nodes in the tree.

    This class extends the Kivy BoxLayout to create a draggable widget that represents nodes
    in a tree structure. It provides functionality for handling drag-and-drop operations and
    visually connecting nodes through incoming and outgoing lines.

    :param kwargs: Additional keyword arguments to be passed to the BoxLayout constructor.
    :type kwargs: dict
    """

    def __init__(self, **kwargs):
        """Initialize the DraggableWidget.

        Sets up the initial state of the DraggableWidget, including attributes for tracking
        dragging state, touch coordinates, and arrays for visual lines connecting nodes.

        :param kwargs: Additional keyword arguments to be passed to the BoxLayout constructor.
        :type kwargs: dict
        """
        self.is_dragging = False
        self.touch_x = 0
        self.touch_y = 0

        #the array holders for the visual lines connecting nodes that link outputs and inputs
        self.incoming_lines = []
        self.outgoing_lines = []

        #initializes the BoxLayout that will be draggable
        super().__init__(**kwargs)


class ModuleNode:
    """Defines the visual element of a module as a node within a tree and its connections for run time
    """

    def __init__(self, module, module_name):
        """Initializes the ModuleNode class with its module, input, output, submodule, and property type information/descriptions"""
        #module components the node holds
        self.module = module
        self.module_name = module_name

        #find the information of inputs, outputs, submodules, description
        try:
            self.output_dict = module.results()
        except Exception as e:
            self.plugin_player.add_message(
                f"Couldn't find output information: {e}")
            return
        try:
            self.input_dict = module.inputs()
        except Exception as e:
            self.plugin_player.add_message(
                f"Couldn't find input information: {e}")
            return
        try:
            self.submod_dict = module.submods()
        except Exception as e:
            self.plugin_player.add_message(
                f"Couldn't find submodule information: {e}")
            return
        try:
            self.description = module.description()
        except Exception as e:
            self.description = "Not Supported"
            self.plugin_player.add_message(f"Couldn't find description: {e}")

        #holds the property type for the module
        self.property_type = None

        #holds the widget of the node
        self.module_widget = None

        #holds the widget of the custom declaration of the currently selected input
        self.custom_declaration_widget = TextInput(hint_text="ex: Force()",
                                                   size_hint_x=3 / 5,
                                                   multiline=False)

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
        """Adds a widget that represents the node in the tree."""
        self.module_widget = widget
