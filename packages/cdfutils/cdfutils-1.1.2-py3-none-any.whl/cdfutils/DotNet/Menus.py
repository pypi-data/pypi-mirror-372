#
#   Module:     DotNet.Menus
#   Platform:   Python 3, Windows.NET
#
#   Some general helper classes for use with .NET Windows.Forms:
#
#       CustomMainMenu:
#           A MenuStrip created from a list of menu item parameters
#
#       CustomToolBar:
#           A ToolStrip created from a list of toolbar item parameters.
#
#       SimpleContextMenu:
#           A ContextMenu created from a list of handlers and item text.
#
#   Copyright Craig Farrow, 
#   2010 - 2025
#

import clr
clr.AddReference("System.Windows.Forms")

import os

from System import EventHandler
from System.Windows.Forms import (
    MenuStrip, ToolStripMenuItem,
    ContextMenuStrip,
    ToolStrip, ToolStripButton, ToolStripSeparator,
    ToolStripGripStyle,
    TextImageRelation,
    ImageList,
    ColorDepth,
    )
    
from System.Drawing import (
    Bitmap, Image
    )

# ------------------------------------------------------------------
class CustomMainMenu(MenuStrip):
    """
    Creates a .NET MenuStrip from an initialised structure:
        List of tuples: (Menu Title, Submenu List)
        Submenu List is a list of tuples:
            (Handler, Text, Shortcut, Tooltip)
            If the Handler is None, then the menu is disabled.
            Shortcut can be None for no shortcut key.
            If the tuple is None, then a separator is inserted.
        Handlers are standard .NET Event Handlers, which take two 
        parameters: the sender object, and System.EventArgs.
    """
    def __init__(self, menuList):
        MenuStrip.__init__(self)
        self.ShowItemToolTips = True
        for menu in menuList:
            newMenu = ToolStripMenuItem()
            newMenu.Text, submenuList = menu
            for submenu in submenuList:
                if submenu:
                    handler, text, shortcut, tooltip = submenu
                    newSubmenu = ToolStripMenuItem(text, None, EventHandler(handler))
                    if not handler:
                        newSubmenu.Enabled = False
                    if shortcut:
                        newSubmenu.ShortcutKeys = shortcut
                    newSubmenu.ToolTipText = tooltip
                else:
                    newSubmenu = ToolStripSeparator()
                newMenu.DropDownItems.Add(newSubmenu)
            self.Items.Add(newMenu)

# ------------------------------------------------------------------
class CustomToolBar(ToolStrip):
    """
    Creates a .NET ToolStrip from an initialised structure:
        buttonList = List of tuples: 
            (Handler, Text, ImageName, Tooltip)
            If the Handler is None, then the button is disabled.
            An item of None produces a toolbar separator.
        imagePathTuple = (prefix, suffix) pair to generate a full
            file path from the ImageName.
    """

    def __init__(self, buttonList, imagePathTuple):
        ToolStrip.__init__(self)
        self.GripStyle = ToolStripGripStyle.Hidden

        self.ImageList = ImageList()
        self.ImageList.ColorDepth = ColorDepth.Depth32Bit

        for bParams in buttonList:
            if bParams:
                button = ToolStripButton()
                button.TextImageRelation = TextImageRelation.ImageAboveText
                handler, button.Text, imageName, button.ToolTipText = bParams
                path, suffix = imagePathTuple
                imagePathName = os.path.join(path, imageName+suffix)
                self.ImageList.Images.Add(Bitmap.FromFile(imagePathName))
                button.ImageIndex = self.ImageList.Images.Count-1
                if handler:
                    button.Click += handler
                else:
                    button.Enabled = False
            else:
                button = ToolStripSeparator()
            self.Items.Add(button)

    def UpdateButtonText(self, buttonIndex, newText):
        self.Items[buttonIndex].Text = newText

# ------------------------------------------------------------------
class SimpleContextMenu(ContextMenuStrip):
    """
    Creates a .NET ContextMenu from a list of tuples: 
        (Handler, Text)
    """

    def __init__(self, contextMenuItems):
        ContextMenuStrip.__init__(self)

        for handler, itemText in contextMenuItems:
            item = ToolStripMenuItem (itemText, None, EventHandler(handler))
            self.Items.Add(item)

