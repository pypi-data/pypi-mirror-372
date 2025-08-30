import os
import sys

CIO_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, CIO_DIR)

from cioc4d.conductor_dialog import ConductorDialog
import cioc4d.const as k
from cioc4d import utils

import c4d

import ciocore.loggeria

# Setup logging
ciocore.loggeria.setup_conductor_logging(
    logger_level =  ciocore.loggeria.LEVEL_MAP.get(ciocore.config.get()['log_level']),
)
class ConductorRender(c4d.plugins.CommandData):
    dialog = None

    def Execute(self, doc):
        if self.dialog is None:
            self.dialog = ConductorDialog()

        return self.dialog.Open(
            dlgtype=c4d.DLG_TYPE_ASYNC, pluginid=k.PLUGIN_ID, defaulth=800, defaultw=480
        )

    def RestoreLayout(self, sec_ref):
        if self.dialog is None:
            self.dialog = ConductorDialog()
        return self.dialog.Restore(pluginid=k.PLUGIN_ID, secret=sec_ref)


def enhance_render_menu():

    mainMenu = c4d.gui.GetMenuResource("M_EDITOR")
    renderMenu = False
    for index, value in mainMenu:

        for i, v in value:
            if v == "IDS_EDITOR_RENDER":
                renderMenu = value
                break
        if renderMenu:
            break

    if k.C4D_VERSION > 2023:
        renderMenu.InsData(c4d.MENURESOURCE_SEPARATOR, True)
    else:
        renderMenu.InsData(c4d.MENURESOURCE_SEPERATOR, True)
    renderMenu.InsData(c4d.MENURESOURCE_SUBTITLE, "Conductor")
    renderMenu.InsData(c4d.MENURESOURCE_COMMAND, "PLUGIN_CMD_1057859")
    renderMenu.InsData(c4d.MENURESOURCE_COMMAND, "PLUGIN_CMD_1057860")


def PluginMessage(the_id, data):
    if the_id == c4d.C4DPL_BUILDMENU:
        enhance_render_menu()


def main():
    cr_icon = c4d.bitmaps.BaseBitmap()
    cr_icon.InitWith(os.path.join(k.PLUGIN_DIR, "res", "conductorRender_30x30.png"))
    c4d.WriteConsole("Conductor plugin loading...\n")
    success = c4d.plugins.RegisterCommandPlugin(
        id=k.PLUGIN_ID,
        str="Conductor Render",
        info=0,
        icon=cr_icon,
        help="Render scene using Conductor cloud service",
        dat=ConductorRender(),
    )
    if not success:
        c4d.WriteConsole("Couldn't register Conductor plugin.\n")
        return
 
    c4d.WriteConsole("Conductor plugin loaded.\n")


if __name__ == "__main__":
    main()
