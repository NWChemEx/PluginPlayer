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
Introductary Observations
#############################




Modular-based Software

    Using modular software in a project requires running collections of Modules in a series, 
    which are uniquely connected based on the user’s application needs. 
    Module collections are written in Plugins, which hold Modules with related 
    functionality and topics. Each Module has defined inputs, outputs, and submodules, 
    which define its property type and API to run correctly. 

    To run a Module, it must be imported into the ModuleManger, 
    which handles selecting Submodules and inputs to run the Module successfully. 
    When creating a complete modular program, the aim is to connect multiple Modules together, 
    using outputs from one Module as inputs for another. This requires the user to load each 
    Plugin’s Module collection into a ModuleManager manually, configure the Submodules, 
    and run each Module individually, storing a Module’s outputs to place as future inputs 
    for another Module.

An Alternative Solution: GUI Goals

    Using modular software as an approach allows separation between working units in a 
    complete application design but requires extensive writing of each application run 
    to import, link, and run modules in a series. The main goal of creating a Graphical 
    User Interface for a PluginPlay modular software application is to allow a user or 
    developer to select compiled plugins and create an application tree that connects 
    Modules’ outputs and inputs to run in a desired series. This can reduce a user's 
    or developer’s time testing an application using modular components. 

Using Kivy, Why?
    When designing a modular software user interface, we must note our objectives and choose 
    a visual library that suits the project’s needs. The main goal of this user interface is 
    to provide both users and developers with an application with a modern, simplistic, and 
    reliable design to build and view a custom visual tree-like structure of connected Modules. 
    This application should be functional on multiple platforms, as users have different 
    operating systems and screen proportions.

    Tkinter is a popular Python GUI-building library that can build objects, buttons, and 
    visual displays from the standard Python library. Tkinter runs on MacOS and Windows 
    systems and can be implemented into a website as a Python app. However, Tkinter has 
    limited “Canvas” functionality, limiting the number of widgets placed in a particular 
    area and varying designs from platform to platform. With adding a custom amount of Plugin 
    folders and listing Modules, Tkinter lacks the ease of organizing these objects in a frame. 
    Tkinter also manages mouse events complexly, limiting drag-and-drop functionality, which 
    is essential when maneuvering Modules into a custom tree-like structure. However, as Tkinter 
    is a standard python library, external third-party libraries are available to overcome some 
    limitations.

    PyQt is a set of Python bindings for a Qt application framework. PyQt provides a wide range 
    of customizable widgets, making it suitable for creating complex user interfaces, including 
    trees with various elements. PyQt offers a native look and feel on different platforms, 
    ensuring an application's GUI is consistent across Windows, macOS, and Linux. PyQt has a 
    steeper learning curve than more straightforward GUI frameworks like Tkinter, especially 
    for beginners. Understanding the Qt framework's concepts and PyQt-specific features may 
    take some time. The ability to change and modify the PluginPlay GUI framework is essential, 
    and a learning obstacle will make it difficult for editor alterations.

    Kivy is a versatile open-source Python framework for developing cross-platform applications,
    including those with custom GUI components like a tree structure with draggable widgets. 
    Kivy supports multiple platforms, including Windows, macOS, Linux, Android, and iOS, allowing 
    you to create applications that run on various devices. Supporting multiple platforms, including 
    mobile devices, allows the implementation of the GUI to branch to a mobile application. Kivy is 
    designed for touch interfaces, making it suitable for multitouch and gesture support applications. 
    This can be beneficial for interactive and touch-based interfaces. While you can use any Python 
    IDE with Kivy, the level of support might not be as extensive as for some other GUI frameworks. 
    However, there is extensive community support for Kivy and well-defined documentation that can 
    allow collaboration and easier editing of the GUI.

    Kivy was chosen as the Python library to build the PluginPlay GUI for its easy-to-use design 
    and assortment of widgets that can be moved with drag-and-drop manipulation to create a custom 
    Module tree design. The compatibility with multiple platforms and mobile devices makes Kivy a 
    versatile tool that can work on various devices.


    
      

