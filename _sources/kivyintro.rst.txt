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
Kivy
#############################

Windows and Kivy Structures
===========================
    In Kivy, a Window serves as the main drawing area for your application. It is the top-level container that encompasses the entire graphical space. You can customize the window's properties, such as its size, title, and fullscreen mode. Additionally, Kivy supports multiple windows, allowing for more complex application structures.

    The primary building blocks of the user interface in Kivy are Widgets. Widgets are graphical elements that can be added to windows to create interactive user interfaces. Kivy provides a wide range of predefined widgets, including buttons, labels, text inputs, and more. Widgets can be arranged and nested in various layouts to achieve the desired user interface design. They handle user input events, such as touch or mouse interactions, and can be styled and customized to fit the application's visual theme. Understanding the structure of Windows and Widgets is fundamental to creating dynamic and responsive user interfaces in Kivy.

Widget Types
============
    BoxLayout
        The `BoxLayout` widget in Kivy is a versatile layout manager that simplifies the 
        arrangement of child widgets either horizontally or vertically. With its `orientation` 
        property, developers can easily create rows or columns of widgets. The automatic sizing 
        of children based on available space makes it convenient for creating dynamic interfaces 
        that adapt to various screen sizes.

    Image
        Kivy's `Image` widget is a powerful tool for displaying graphical content within 
        applications. It supports a variety of image formats and provides features for 
        manipulating and presenting images, including scaling and rotation. This widget is 
        crucial for incorporating visual elements and enhancing the aesthetic appeal of Kivy 
        applications.

    Widget
        The `Widget` class serves as the fundamental building block for all other widgets in Kivy. 
        It offers a container for housing other widgets, providing essential properties and methods. 
        Developers can either use it as a generic container or subclass it to create custom widgets 
        with specific behaviors and functionalities.

    Button
        The `Button` widget is a fundamental component for creating interactive user interfaces in 
        Kivy applications. It represents a clickable element that can trigger predefined actions or 
        functions when pressed. Buttons are commonly employed for user-initiated actions, such as 
        submitting forms or navigating between different sections of an application.

    TextInput
        The `TextInput` widget facilitates the input and display of multiline text in Kivy 
        applications. It supports keyboard input and can be customized for various text-related 
        functionalities, such as password masking or restricting input to numeric values. This 
        widget is essential for capturing user-generated textual content.

    Line
        Kivy's `Line` widget is a powerful tool for drawing lines and shapes within an application. 
        It enables developers to create custom graphics and diagrams, allowing for enhanced 
        visualization and artistic expression in the user interface.

    Popup
        The `Popup` widget is a versatile tool for displaying temporary and context-specific 
        information in Kivy applications. Whether used for alerts, notifications, or additional 
        user input, the `Popup` widget creates a separate window that can be modal or non-modal, 
        enhancing the user experience by providing focused interactions.

    Label
        The `Label` widget in Kivy is essential for presenting textual information in the user 
        interface. It supports various text formatting options and serves as a straightforward yet 
        powerful means of conveying information, titles, or instructions within the application.

    ScrollView
        The `ScrollView` widget is indispensable when dealing with content that exceeds the 
        available screen space. It enables users to scroll through content, ensuring that all 
        information remains accessible. This widget is particularly useful for presenting lengthy 
        text, images, or other types of data without cluttering the main screen.

    `Kivy Documentation <https://kivy.org/doc/stable/>`_
