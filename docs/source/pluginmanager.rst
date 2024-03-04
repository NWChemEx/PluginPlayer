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
PluginManager Class
#############################

Dynamically Importing Plugins
    Modular packages must be imported into the system when creating a GUI interface to allow users to work with Plugins. Each CMake compiled modular project creates a Plugin file within the internal build directory, registered as a .so file. Each Plugin has the load_modules() function to import Modules into a ModuleManager. If the Plugin contains Modules that don’t define its inputs, outputs, or submodules, the Plugin will not be imported, and an error message will be displayed. The ModuleManager acts as a directory for all the Modules to be later configured and run.

    The current GUI design for dynamically importing and viewing plugin information to create an efficient application build.

    Users can enter a path to a plugin .so file or a directory to browse.

    Once a Plugin is imported using the `plugin_loader` function, it is displayed as a folder in the Plugin Section, updated by the `plugin_view` function.

Viewing Modules and API
    A comprehensive GUI application should allow users to view each dynamically imported plugin’s Modules and their APIs, including a functional description, inputs, outputs, and required submodules, to gain information when creating an application design. Having documentation of each loaded Module allows for a more efficient application build.

    When selecting a Plugin folder, a user is shown a popup, showing each of the Plugin’s Modules using the `view_modules` function. The user can also delete the Plugin and remove its Modules from the ModuleManager, add a Module to the Module tree for application building, and view its API info.

    When selecting the “Info” button for the module, the following popup is displayed to show the Module’s description, inputs, outputs, and submodules using the `view_module_info` function. Information is provided for the Module’s parameters. If the Module does not provide information, “description unavailable” will be shown.





