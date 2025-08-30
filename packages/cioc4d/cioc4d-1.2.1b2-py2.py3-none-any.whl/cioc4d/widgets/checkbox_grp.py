

import c4d
from cioc4d.widgets import utils as wutil


class CheckboxGrp(object):
    """A group containing a label and checkbox"""

    def __init__(self, dialog, label, enabled=True):
        self.label = label
        self.dialog = dialog
        self.checkbox_id = None
        self.enabled = enabled
        self._build()
 
    def _build(self):
        grid_group_id = 0
        with wutil.grid_group(self.dialog, cols=2) as gg_id:
            grid_group_id = gg_id
            wutil.dotted_label(self.dialog, self.label)
            self.checkbox_id = self.dialog.register()
            self.dialog.AddCheckbox(
                    self.checkbox_id, c4d.BFH_SCALEFIT , initw=0, inith=0 , name="")
        if not self.enabled and grid_group_id:
            self.set_value(False)
            self.dialog.HideElement(grid_group_id, True)

    def get_value(self):
        return self.dialog.GetBool(self.checkbox_id) 

    def set_value(self, value):
        self.dialog.SetBool(self.checkbox_id, value) 

