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
UtilityManager Class
#############################

The need for a utility manager
    Throughout the GUI it is essential to keep track of added class types, adding new class types, and browsing files. The `UtilityManager` class handles this to allow for helper functions needed throughout the application.

Browsing files
    Browsing files in kivy can be done by clicking the browse button to run the `browse` function and open a popup to view your system's files. The `browse` function reads text input from an entry and interprets it as a potential path to browse to in the system. Using a `ScrollView` widget, a user can navigate through their system and select a filepath of their plugin they would like to import.

Viewing class types
    To add an input or property type to a module's run settings, a user may need to declare a special variable type, evaluating their statement with an extra list of imported classes is necessary to allow for a more complex module run. Viewing imported class types within the `view_config` and `add_input` widget runs the `class_types` function, opening a popup to view a list of imported class types and a button to import a new type.

Importing a new class type
    Directed from the `class_types` popup, you can enter a python partial import statement defining the library to import from as well as the type name. Clicking the Import button, the `new_type` function runs `importlib` to import the new class type into the system's main modules which is used in evaluating import and property type statements. If a module is unable to be imported, a message is displayed and the system's modules are not modified.