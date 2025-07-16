"""
osintbuddy.elements.

This module aggregates all base, display, and input elements
used in OsintBuddy UI plugins. Importing from this module provides
direct access to all component classes in one place.

Usage
-----
from osintbuddy.elements import Title, TextInput, Table, ...
"""

# Base classes
from osintbuddy.elements.base import BaseDisplay
from osintbuddy.elements.base import BaseElement
from osintbuddy.elements.base import BaseInput
from osintbuddy.elements.displays import CopyCode
from osintbuddy.elements.displays import CopyText
from osintbuddy.elements.displays import Empty
from osintbuddy.elements.displays import Image
from osintbuddy.elements.displays import Json
from osintbuddy.elements.displays import List
from osintbuddy.elements.displays import Pdf
from osintbuddy.elements.displays import Table
from osintbuddy.elements.displays import Text

# Display elements
from osintbuddy.elements.displays import Title
from osintbuddy.elements.displays import Video
from osintbuddy.elements.inputs import DecimalInput
from osintbuddy.elements.inputs import DropdownInput
from osintbuddy.elements.inputs import NumberInput
from osintbuddy.elements.inputs import TextAreaInput
from osintbuddy.elements.inputs import TextInput

# Input elements
from osintbuddy.elements.inputs import UploadFileInput

__all__ = [
    # Base
    "BaseElement",
    "BaseInput",
    "BaseDisplay",
    # Displays
    "Title",
    "Text",
    "CopyText",
    "CopyCode",
    "Json",
    "Image",
    "Video",
    "Pdf",
    "List",
    "Table",
    "Empty",
    # Inputs
    "UploadFileInput",
    "TextInput",
    "TextAreaInput",
    "DropdownInput",
    "NumberInput",
    "DecimalInput",
]
