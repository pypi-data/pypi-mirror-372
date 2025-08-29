
import c4d
import json
from cioc4d import asset_cache
from cioc4d.widgets.int_field_grp import IntFieldGrp
from cioc4d.widgets.button_row import ButtonRow
from cioc4d.sections.collapsible_section import CollapsibleSection
from cioc4d.widgets.text_area_grp import TextAreaGrp


class PreviewSection(CollapsibleSection):

    ORDER = 300

    def __init__(self, dialog):
        self.json_widget = None

        self.affectors = []

        super(PreviewSection, self).__init__(dialog, "Preview", collapse=True, override_color=c4d.Vector(0.2, 1,0.2))

    def build(self):
        self.actions_widget = ButtonRow(
            self.dialog, "Show Assets", button_width=120, dotted_label=False)
        self.json_widget = TextAreaGrp(self.dialog, height=200)
        self.dialog.HideElement(self.preview_button_id, True)

    def on_plugin_message(self, widget_id, msg):
        if widget_id in self.affectors:
            if not self.collapsed:
                self.set_submission_preview(True)

        if widget_id in self._store_affectors:
            self.save_to_store()

    def on_core_message(self, msg_id, msg):
        """Repopulate if EVMSG_CHANGE was emitted.

        It's possibly a result of the image paths being changed.
        """
        if msg_id in [c4d.EVMSG_CHANGE]:
            if not self.collapsed:
                self.set_submission_preview(True)


    def set_submission_preview(self,  with_assets=False):
        """
        Update the json in the preview window.

        We clear the asset cache first, which means that if the user wants to see scraped assets,
        they will be re-scanned. 

        Args:
            with_assets: Also signify that user wants to see scanned assets. Defaults to False.
        """
        asset_cache.clear()
        submission = self.dialog.calculate_submission(with_assets=with_assets)
        self.json_widget.set_value(json.dumps(submission, indent=2))

    def set_affectors(self):
        """
        Get the IDs of widgets that can affect the preview
        """
        self.affectors = []
        self.affectors.append(self.dialog.foot_grp.connect_button_id)

        for section in self.dialog.sections:
            self.affectors += section.get_preview_affectors()

    def on_expand(self):
        """
        Calculate submission preview window with assets while section is expanded.
        """
        if self.json_widget.get_value():
            self.set_submission_preview(True)

    def on_collapse(self):
        """
        Do not calculate submission preview window with assets while section
        is collapsed.
        """
        pass


    def get_preview_affectors(self):
        """
        Collecting assets is potentially expensive as we need to hit the
        filesystem. For this reason, make the user click a button so they know
        what to expect.
        """
        return [
            self.actions_widget.button_ids[0]
        ]

    @property
    def preview_button_id(self):
        return self.actions_widget.button_ids[0]

