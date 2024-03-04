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
TreeManager Class
#############################

Managing tree nodes
    The `TreeManager` class handles adding and deleting tree nodes and adding them to the `nodes` list.

    When a user wants to delete a node, they can press the delete X button on the node's widget to run the `delete_node` function which iterates through it's connections with other nodes, removes them, removes their lines, and then removes the widget from the tree.

    When a user wants to add a node, they can choose to add a module to the tree within the `module_view` which will run the `add_node` function, calling `NodeWidgetManager` defined types to build a new widget and add it to the `nodes` list with empty connections.

Running the tree
    A user can run their connected module tree by clicking the Run Tree button in the tree section. This will call the `run_tree` function that will recursively iterate through the `nodes` list using Depth First Search and determine if a node relies on another, creating a run order. If each node has all run settings set, the run order will individually run each module through the `ModuleManager`, store its output, and use it on other dependent modules. 

Deleting the tree
    A user can delete their connected module tree by clicking the Delete Tree button in the tree section. This will call the `delete_tree` function that will iterate through the `nodes` list and call the `remove_node` function, removing all connections within the tree and its nodes.

