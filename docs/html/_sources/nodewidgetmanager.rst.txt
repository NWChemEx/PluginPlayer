.. Copyright 2024 NWChemEx-Project
..
.. Licensed under the Apache License, Version 2.0 (the "License");
.. you may not use this file except in compliance with the License.
.. You may obtain a copy of the License at
..
.. http://www.apache.org/licenses/LICENSE-2.0
..
.. Unless required by applicable law or agreed to in writing, software
.. distributed under the License is distributed on an "AS IS" BASIS,
.. WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
.. See the License for the specific language governing permissions and
.. limitations under the License.

#############################
NodeWidgetManager Class
#############################

Building the node's widget
    When building a modular application design, nodes of the tree can be added from the module view, and a node is placed on the tree with the Module’s name and the node number, a series of options buttons, and a configuration button. This node widget building process is done by `NodeWidgetManager` class that imports image files and module settings into a `ModuleNode` class. The `ModuleNode` class contains dictionaries of the inputs, outputs, property type, and submodules required for the run process. 

Button Options 
    Within the options buttons the user to move the node with the navigation button, shown with a four-arrowed icon by dragging. The drag implementation is monitored by the `DraggableImageButton` and `DraggableWidget` class within `NodeWidgetManager` class to track user's touch and drag movements and move the widget based on the mouse location.  The user can access the API information for the Module the node contains by clicking the info button, shown with an “i” icon. The user can also remove the node by clicking the remove button, shown with an X icon. The remove functionality removes all connections in the tree and deletes the node from the tree through the `delete_node` function.

Viewing the node's configuration
    When a user clicks the “Configure” button, a popup will be shown to display the inputs, outputs, and Submodules for the nodes, as well as their connections in the tree if they are set. This popup is build by the `view_config` function within the `NodeManager` class, iterating through the node’s run settings and displaying each value that has been set or left empty. “Set” buttons are also next to each input, property type, and submodule displayed to set their connection in the tree.

Setting a connection
    The “Set” popup is displayed after the user decides to set either an input, property type, or submodule. Viewing the options for setting a run value is handled by the popup builder functions `add_input` and `add_submod` within the `NodeManager` class. Setting a property type requires only a text entry of the function type.

Linking a connection
    The Set input/submodule popup shows each module from each imported plugin and shows a “Set” button to set it as the input or submodule. On clicking a “Set” button, the ModuleManager will attempt to set it to the run settings using the `link_input`, `link_property_type`, or `link_submod` functions within the `NodeManager` class. If it succeeds, it will be set in the node’s run settings with its description and the connected node’s information. If an error occurs, a message will output the error, and no settings will be set.

