import c4d
from cioc4d.widgets import utils as wutil
import copy

class DualComboBoxGrp(object):
    """
    A group containing a label and one or two combo boxes.

    # model is expected to be structured like this:

    [
        {
            "label": "Category 1",
            "id":"00123",
            "content": [
                {"label": "Content 1", "value": "content1", "id": "00128"},
                {"label": "Content 2", "value": "content2", "id": "00129"},
                {"label": "Content 3", "value": "content3", "id": "00130"}
            ]
        },
        {
            "label": "Category 2",
            "id":"00456",
            "content": [
                {"label": "Content 4", "value": "content4", "id": "004567"},
                {"label": "Content 5", "value": "content5", "id": "004568"},
                {"label": "Content 6", "value": "content6", "id": "004569"}
            ]
        }
    ]

    The "id" field is generated when we register each item.
    Categories must be unique.
    An instance type may appear in more than one category.
    """

    def __init__(self, dialog, **kwargs):
        self.dialog = dialog
        self.label = kwargs.get("label", "")

        self.category_combo_box_id = None
        self.content_combo_box_id = None
        self.model = []

        self._build()

    def _build(self):
        """Create the comboboxes and label"""
        with wutil.grid_group(self.dialog, cols=3):
            self.category_combo_box_id = self.dialog.register()
            self.content_combo_box_id = self.dialog.register()
            wutil.dotted_label(self.dialog, self.label)
            self.dialog.AddComboBox(self.category_combo_box_id, c4d.BFH_SCALEFIT)
            self.dialog.AddComboBox(self.content_combo_box_id, c4d.BFH_SCALEFIT)

    def clear_all(self):
        """Clear the comboboxes and the model.

        This is only needed on reconnect.
        """
        self.dialog.FreeChildren(self.category_combo_box_id)
        self.dialog.FreeChildren(self.content_combo_box_id)
        self.model = []

    def register_model(self, model):
        """
        add options to the model and register them with the dialog
        """
        self.model = copy.deepcopy(model)
        for category in self.model:
            category["id"] = self.dialog.register()
            for content in category["content"]:
                content["id"] = self.dialog.register()
        
        

        self.populate_category_combo()

    def populate_category_combo(self, default_value=None):
        """Add the categories to the category combobox

        If it already has a value, attempt to set it back to that value.
        """
        existing_label = self._get_selected_category_label()
        if existing_label and existing_label.startswith("--"):
            existing_label = default_value

        self.dialog.FreeChildren(self.category_combo_box_id)
        for category in self.model:
            self.dialog.AddChild(
                self.category_combo_box_id, category["id"], category["label"]
            )

        if not self._set_category_by_label(existing_label):
            self._set_category_by_index(0)
        
        # We don't want to show the category combobox if there is only one category
        self.dialog.HideElement( self.category_combo_box_id, len(self.model) < 2)

    def set_category_by_label(self, label):
        """Set the category combobox to the model element with the given label"""

        category = next((x for x in self.model if x["label"] == label), None)
        if category:
            self._set_category_by_id(category["id"])

    def set_content_by_value(self, value):
        """
        Set content by it's sku value.
        
        Finds the correct category and sets it, which will then populate the content combobox.
        Then sets the content combobox to the correct item.
        """
        for category in self.model:
            for content in category["content"]:
                if content["value"] == value:
                    self._set_category_by_id(category["id"])
                    self.dialog.SetInt32(self.content_combo_box_id, content["id"])
                    return True
        return False
    
    def get_selected_content_value(self):
        """Get the sku value of the selected content"""
        content = self._get_selected_content()
        return content and content["value"]
    

    # PRIVATE
    def on_category_change(self):
        """Called when the category combobox changes"""
        self._populate_content_combo(self.dialog.GetInt32(self.category_combo_box_id))
        
    def _populate_content_combo(self, category_id):
        self.dialog.FreeChildren(self.content_combo_box_id)
        category = next((x for x in self.model if x["id"] == category_id), None)
        if category:
            for content in category["content"]:
                self.dialog.AddChild(
                    self.content_combo_box_id, content["id"], content["label"]
                )
            self._set_content_by_index(0)


    def _set_category_by_label(self, label):
        category = next((x for x in self.model if x["label"] == label), None)
        if category:
            self._set_category_by_id(category["id"])

    def _set_category_by_index(self, index):
        try:
            self._set_category_by_id(self.model[index]["id"])
        except IndexError:
            self._set_category_by_id(self.model[0]["id"])

    def _set_category_by_id(self, category_id):
        """
        Set the category combobox to the given category id

        All the other methods of setting the category should ultimately call
        this one as it then sets the content based on the newly selected
        category.
        """
        self.dialog.SetInt32(self.category_combo_box_id, category_id)
        self._populate_content_combo(category_id)
        
    def _get_selected_category(self):
        selected_id = self.dialog.GetInt32(self.category_combo_box_id)
        return next((x for x in self.model if x["id"] == selected_id), None)

    def _get_selected_category_label(self):
        category = self._get_selected_category()
        return category and category["label"]

    def _get_selected_content(self):
        selected_id = self.dialog.GetInt32(self.content_combo_box_id)
        for category in self.model:
            for content in category["content"]:
                if content["id"] == selected_id:
                    return content
        return None

    def _get_selected_content_label(self):
        content = self._get_selected_content()
        return content and content["label"]

    def _set_content_by_index(self, index):

        category = self._get_selected_category()

        if index < len(category["content"]):
            content_id = category["content"][index]["id"]
        elif len(category["content"]) > 0:
            content_id = category["content"][0]["id"]
        else:
            return
        self._set_content_by_id(content_id)
            
    def _set_content_by_id(self, content_id):
        self.dialog.SetInt32(self.content_combo_box_id, content_id)
