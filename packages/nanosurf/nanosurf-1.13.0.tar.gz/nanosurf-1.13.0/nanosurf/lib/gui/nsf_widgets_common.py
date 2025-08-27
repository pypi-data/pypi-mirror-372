
""" defines some nanosurf colors
Copyright Nanosurf AG 2021
License - MIT
"""
import enum

class LabelWidgetSize:
    spacing_vertical = 0
    spacing_horizontal = 5
    content_margins = (0,0,0,0)

class WidgetLayout(enum.Enum):
    Horizontal = 0
    Vertical = 1
