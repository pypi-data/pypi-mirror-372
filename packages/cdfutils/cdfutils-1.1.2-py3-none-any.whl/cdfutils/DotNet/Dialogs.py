#
#   Module:     DotNet.Dialogs
#   Platform:   Python 3, Windows.NET
#
#   Some general dialog creation classes for use with .NET Windows.Forms:
#
#       ChooserDialog:
#           A dialog box with a dropdown menu.
#
#       RadioDialog:
#           A dialog box with radio buttons.
#
#       TextDialog:
#           A dialog box with a text field.
#
#
#   Copyright Craig Farrow
#   2025
#
 
import clr
import sys

clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")

from System.Windows.Forms import (
    Form, Panel,
    FormStartPosition,
    FormBorderStyle,
    DockStyle,
    AnchorStyles,
    DialogResult,
    Button, 
    ComboBox, ComboBoxStyle,
    GroupBox,
    FlowLayoutPanel, FlowDirection,
    Padding,
    RadioButton,
    TextBox,
    )
    
from System.Drawing import (
    Point, Size,
    Color,
    )

# ------------------------------------------------------------------

# Size constants

DIALOG_WIDTH            = 300
DIALOG_HEIGHT_DEFAULT   = 100
OKCANCEL_PANEL_HEIGHT   = 40
SPACE                   = 20
BUTTON_SPACING          = 90

# ------------------------------------------------------------------

class DialogShell(Form):
    def __init__(self, 
                 title,
                 height = DIALOG_HEIGHT_DEFAULT):
        Form.__init__(self)
        self.Text = title
        self.ClientSize = Size(DIALOG_WIDTH, height)
        self.StartPosition = FormStartPosition.CenterScreen
        self.FormBorderStyle  = FormBorderStyle.Fixed3D
        self.MinimizeBox = False
        self.MaximizeBox = False
        
        # Bottom gray panel
        bottom_panel = Panel()
        bottom_panel.Height = OKCANCEL_PANEL_HEIGHT
        bottom_panel.Dock = DockStyle.Bottom
        bottom_panel.BackColor = Color.LightGray
        self.Controls.Add(bottom_panel)
        
        # OK button
        ok_button = Button()
        ok_button.Text = _("OK")
        ok_button.Location = Point(DIALOG_WIDTH - BUTTON_SPACING*2, 8)
        ok_button.DialogResult = DialogResult.OK
        bottom_panel.Controls.Add(ok_button)

        # Cancel button
        cancel_button = Button()
        cancel_button.Text = _("Cancel")
        cancel_button.Location = Point(DIALOG_WIDTH - BUTTON_SPACING, 8)
        cancel_button.DialogResult = DialogResult.Cancel
        bottom_panel.Controls.Add(cancel_button)

        self.AcceptButton = ok_button
        self.CancelButton = cancel_button


# ------------------------------------------------------------------

class ChooserDialog(DialogShell):
    """
    Creates a .NET dialog box with a ComboBox for selecting an item
    from a list.
    Parameters:
        title:       The dialog title.
        items:       A list of strings or any object that can be converted 
                     to a string.
        currentItem: One of the values from items, which is the 
                     default/current one to show in the ComboBox.
    Use the Show() method to display the dialog and get the user-selected 
    value (or None if the user canceled).
    """
    def __init__(self, 
                 title,
                 items, 
                 currentItem):
        super().__init__(title)

        self.SelectedValue = None
        self._items = items

        # ComboBox
        self.combo = ComboBox()
        self.combo.Location = Point(SPACE, SPACE)
        self.combo.Size = Size(DIALOG_WIDTH - SPACE*2, SPACE)
        self.combo.DropDownStyle = ComboBoxStyle.DropDownList # Non-editable

        for item in self._items:
            self.combo.Items.Add(str(item))
            if str(item) == str(currentItem):
                self.combo.SelectedItem = self.combo.Items[
                                                self.combo.Items.Count-1]
        self.Controls.Add(self.combo)
        self.ActiveControl = self.combo

    def Show(self):
        result = self.ShowDialog()
        if result == DialogResult.OK and self.combo.SelectedItem:
            self.SelectedValue = self.combo.SelectedItem
        else:
            self.SelectedValue = None
        return self.SelectedValue


# ------------------------------------------------------------------

class RadioDialog(DialogShell):
    """
    Creates a .NET dialog box with radio buttons for selecting an item
    from a list of options.
    Parameters:
        title:       The dialog title.
        items:       A list of strings or any object that can be converted 
                     to a string.
        currentItem: One of the values from items, which is the 
                     default/current one to show as selected.
    Use the Show() method to display the dialog and get the user-selected 
    value (or None if the user canceled).
    """
    def __init__(self, 
                 title,
                 items, 
                 currentItem):
        super().__init__(title, 
                         OKCANCEL_PANEL_HEIGHT + SPACE*2 + 24 * len(items))

        self.SelectedValue = None
        self._items = items
        
        self.panel = FlowLayoutPanel()
        self.panel.FlowDirection = FlowDirection.TopDown  # Vertical flow
        self.panel.AutoSize = True
        self.panel.Padding = Padding(SPACE)

        currentRB = None
        for item in self._items:
            radioButton = RadioButton()
            radioButton.AutoSize = True  # Adjust size based on text content
            radioButton.Text = str(item)
            if str(item) == str(currentItem):
                radioButton.Checked = True
                currentRB = radioButton
            self.panel.Controls.Add(radioButton)

        self.Controls.Add(self.panel)
        if currentRB:
            self.ActiveControl = currentRB
        else:
            self.ActiveControl = self.panel.Controls[0]

    def Show(self):
        result = self.ShowDialog()
        if result == DialogResult.OK:
            for control in self.panel.Controls:
                if isinstance(control, RadioButton) and control.Checked:
                    self.SelectedValue = control.Text
                    break
        else:
            self.SelectedValue = None
        return self.SelectedValue


# ------------------------------------------------------------------

class TextDialog(DialogShell):
    """
    Creates a .NET dialog box with a TextBox for entering free-form text.
    Parameters:
        title:       The dialog title.
        defaultValue: The initial value for the text field.
    Use the Show() method to display the dialog and get the entered 
    value (or None if the user canceled).
    """
    def __init__(self, 
                 title,
                 defaultValue = ""):
        super().__init__(title)

        self.SelectedValue = None

        # TextBox
        self.text = TextBox()
        self.text.Text = defaultValue
        self.text.Location = Point(SPACE, SPACE)
        self.text.Size = Size(DIALOG_WIDTH - SPACE*2, SPACE)       
        self.Controls.Add(self.text)
        self.ActiveControl = self.text

    def Show(self):
        result = self.ShowDialog()
        if result == DialogResult.OK:
            self.SelectedValue = self.text.Text
        else:
            self.SelectedValue = None
        return self.SelectedValue

