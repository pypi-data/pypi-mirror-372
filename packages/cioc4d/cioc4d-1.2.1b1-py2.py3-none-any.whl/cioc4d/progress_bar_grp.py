from contextlib import contextmanager

import c4d

@contextmanager
def progress_bar_group(dialog, **kwargs):
    grp_id = dialog.register()
    grp = dialog.GroupBegin(
        id=grp_id,
        flags= c4d.BFH_CENTER | c4d.BFH_SCALEFIT,
        title="",
        rows=3,
        cols=kwargs.get("cols", 0),
        groupflags=0)
    dialog.GroupBorderNoTitle(c4d.BORDER_ACTIVE_4)
    if grp:
        dialog.GroupBorderSpace(1, 1, 1, 1)
        yield grp_id
    dialog.GroupEnd()

class ProgressBarGrp(object):

    def __init__(self, dialog):
        self.group_id = None
        self.dialog = dialog
        self.progress_bar_title_id = None
        self.progress_bar_id = None
        self.progress_bar_caption_id = None
        self._build()

    def _build(self):
        with progress_bar_group(self.dialog, cols=0) as group_id:
            self.group_id = group_id
            self.progress_bar_title_id = self.dialog.register()
            self.progress_bar_id = self.dialog.register()
            self.progress_bar_caption_id = self.dialog.register()

            self.dialog.AddStaticText(self.progress_bar_title_id, 
                                flags=c4d.BFH_CENTER, 
                                name= "Submitting to Conductor...",
                                borderstyle=c4d.BORDER_NONE, initw=225)

            progress_status = c4d.BaseContainer(c4d.BFM_SETSTATUSBAR)
            progress_status[c4d.BFM_STATUSBAR_PROGRESSSPIN] = True

            self.dialog.AddCustomGui(self.progress_bar_id, c4d.CUSTOMGUI_PROGRESSBAR, "", 
                                    c4d.BFH_SCALEFIT, 0, 0, progress_status)

            self.dialog.AddStaticText(self.progress_bar_caption_id, 
                                flags=c4d.BFH_CENTER, 
                                name="Note: Please wait a few moments while we submit your scene.",
                                borderstyle=c4d.BORDER_NONE, initw=520)

            self.disable_progress_bar()

    def enable_progress_bar(self):
        """
        Enable inner progress bar elements and update dialog title.
        """
        self.dialog.SetTitle("Conductor Render: Submitting...")

        self.dialog.HideElement(self.progress_bar_title_id, False)
        self.dialog.HideElement(self.progress_bar_id, False)
        self.dialog.HideElement(self.progress_bar_caption_id, False)
        
        progress_status = c4d.BaseContainer(c4d.BFM_SETSTATUSBAR)
        progress_status[c4d.BFM_STATUSBAR_PROGRESSSPIN] = True
        self.dialog.SendMessage(self.progress_bar_id, progress_status)

        self.dialog.HideElement(self.group_id, False)
        self.dialog.LayoutChanged(self.group_id)

    def disable_progress_bar(self):
        self.dialog.SetTitle("Conductor Render")

        self.dialog.HideElement(self.progress_bar_title_id, True)
        self.dialog.HideElement(self.progress_bar_id, True)
        self.dialog.HideElement(self.progress_bar_caption_id, True)

        self.dialog.HideElement(self.group_id, True)
        self.dialog.LayoutChanged(self.group_id)

    def finish_progress(self):
        """
        Send message to progress bar to indicate upload completion.
        """
        progress_status = c4d.BaseContainer(c4d.BFM_SETSTATUSBAR)
        progress_status[c4d.BFM_STATUSBAR_PROGRESSON] = True
        progress_status[c4d.BFM_STATUSBAR_PROGRESS] = 1.0
        self.dialog.SendMessage(self.progress_bar_id, progress_status)

        self.dialog.LayoutChanged(self.progress_bar_id)