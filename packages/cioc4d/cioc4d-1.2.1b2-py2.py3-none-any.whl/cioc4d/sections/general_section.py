# -*- coding: utf-8 -*-
import os

import c4d
from cioc4d.sections.collapsible_section import CollapsibleSection
from cioc4d.widgets.combo_box_grp import ComboBoxGrp
from cioc4d.widgets.dual_combo_box_grp import DualComboBoxGrp
from cioc4d.widgets.text_field_grp import TextFieldGrp
from cioc4d.widgets.checkbox_grp import CheckboxGrp
from cioc4d import utils
from cioc4d import const as k
from ciocore import data as coredata

TAKE_OPTIONS = list(k.TAKES_OPTIONS.values())

NOT_CONNECTED_INST_TYPES = [ {  "label": k.NOT_CONNECTED, "content": [{"label":k.NOT_CONNECTED, "value":k.NOT_CONNECTED}]} ]


        
class GeneralSection(CollapsibleSection):
    """The section that holds the most commonly used settings"""

    ORDER = 10

    def __init__(self, dialog):
        self.takes_widget = None
        self.title_widget = None
        self.projects_widget = None
        self.destination_widget = None
        self.instance_types_widget = None
        self.preemptible_widget = None
        self.is_coreweave = coredata.data()['instance_types'].provider == 'cw'

        super(GeneralSection, self).__init__(dialog, "General", collapse=False)

    def build(self):

        self.takes_widget = ComboBoxGrp(self.dialog, label="Takes")

        self.title_widget = TextFieldGrp(
            self.dialog, label="Job Title", placeholder="Title in Conductor dashboard"
        )

        self.projects_widget = ComboBoxGrp(self.dialog, label="Conductor Project")

        self.dialog.add_separator()
        
        self.instance_types_widget = DualComboBoxGrp(
            self.dialog, label="Instance Type"
        )


        self.preemptible_widget = CheckboxGrp(self.dialog, "Preemptible", 
                                            enabled=not self.is_coreweave)   


    def populate_from_store(self):

        self.update_combo_items()

        store = self.dialog.store
        if not self.is_coreweave:
            self.preemptible_widget.set_value(store.preemptible())
        self.takes_widget.set_items(TAKE_OPTIONS)
        self.takes_widget.set_by_value(store.takes())
        self.title_widget.set_value(store.title())
        self.projects_widget.set_by_value(store.project())
        
        self.instance_types_widget.set_content_by_value(store.instance_type())

    def save_to_store(self):
        store = self.dialog.store

        store.set_preemptible(self.preemptible_widget.get_value())
        store.set_takes(self.takes_widget.get_selected_value())
        store.set_title(self.title_widget.get_value())
        store.set_project(self.projects_widget.get_selected_value())
        
        store.set_instance_type(self.instance_types_widget.get_selected_content_value())
        store.commit()

    def on_plugin_message(self, widget_id, msg):
        if widget_id == self.dialog.foot_grp.connect_button_id:
            self.update_combo_items()

        if widget_id in self._store_affectors:
            self.save_to_store()
            
        if widget_id == self.instance_types_widget.category_combo_box_id:
            self.instance_types_widget.on_category_change()
            self.save_to_store()

    def resolve_current_take(self):
        """Returns currently selected BaseTake object."""
        doc = c4d.documents.GetActiveDocument()
        take_data = doc.GetTakeData()
        if take_data is None:
            raise RuntimeError("Failed to retrieve the take data.")

        current_take = take_data.GetCurrentTake()
        if current_take is None:
            raise RuntimeError("Failed to retrieve the current take data.")

        return current_take

    def resolve_current_take_name(self):
        """Returns name of currently selected take name."""
        current_take = self.resolve_current_take()
        return current_take.GetName()

    def resolve_marked_takes(self):
        """Returns list of all BaseTake objects in TakeData tree."""
        doc = c4d.documents.GetActiveDocument()
        takeData = doc.GetTakeData()
        if takeData is None:
            raise RuntimeError("Failed to retrieve the take data.")

        # The main take is the first take in the tree
        mainTake = takeData.GetMainTake()
        if mainTake is None:
            raise RuntimeError("Failed to retrieve the main take.")

        all_takes = []
        self.takes_ordered(mainTake, all_takes)
        return list(filter(lambda x: x.IsChecked(), all_takes))

    def resolve_marked_takes_names(self):
        """Return list of marked take names."""
        all_takes = self.resolve_marked_takes()
        return [t.GetName() for t in all_takes]

    def takes_ordered(self, current_take, all_takes):
        """Traversal of TakeData take tree."""
        all_takes.append(current_take)

        #get list of children
        childTakes = []
        childTake = current_take.GetDown()
        while childTake:
            childTakes.append(childTake)
            childTake = childTake.GetNext()

        # traverse child nodes
        for ct in childTakes:
            self.takes_ordered(ct, all_takes)

    def update_combo_items(self):
        """Fill the combo boxes with the options from the endpoints"""
        if coredata.valid():
            store = self.dialog.store
            projects = coredata.data()["projects"]
            inst_types_model = coredata.data()["instance_types"].get_model()
            self.projects_widget.set_items(projects, default_value=store.project())
            self.instance_types_widget.register_model(inst_types_model)
        else:
            self.projects_widget.set_items([k.NOT_CONNECTED])
            self.instance_types_widget.register_model(NOT_CONNECTED_INST_TYPES)

    def resolve(self, expander, **kwargs):
        instance_type = self.instance_types_widget.get_selected_content_value()

        rpd = utils.rpd()
        try:
            resolved_title = c4d.modules.tokensystem.StringConvertTokens(
                self.title_widget.get_value(), rpd
            )
        except SystemError:
            resolved_title = "C4d untitled"

        if self.is_coreweave:
            preemptible = False
        else:
            preemptible = self.preemptible_widget.get_value()

        return {
            "job_title": resolved_title,
            "project": self.projects_widget.get_selected_value(),
            "instance_type": instance_type or "INVALID",
            "preemptible": preemptible
        }

    def get_preview_affectors(self):
        """See CollapsibleSection::get_preview_affectors"""
        return [
            self.takes_widget.combo_box_id,
            self.title_widget.text_field_id,
            self.projects_widget.combo_box_id,
            self.instance_types_widget.category_combo_box_id,
            self.instance_types_widget.content_combo_box_id,
            self.preemptible_widget.checkbox_id
            
        ]
