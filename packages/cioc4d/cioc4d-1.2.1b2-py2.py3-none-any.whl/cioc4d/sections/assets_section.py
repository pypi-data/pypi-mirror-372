import os
import c4d
from cioc4d.sections.collapsible_section import CollapsibleSection
from cioc4d.widgets.button_row import ButtonRow
from cioc4d.widgets.path_widget import PathWidget
from ciopath.gpath_list import GLOBBABLE_REGEX, PathList
from ciopath.gpath import Path
from cioc4d import const as k
from cioc4d import asset_cache

BG_COLOR = c4d.Vector(0.2, 0.2, 0.2)


class AssetsSection(CollapsibleSection):
    ORDER = 200

    def __init__(self, dialog):
        self.path_list_grp_id = None
        self.pathlist = PathList()
        self.path_widgets = []
        super(AssetsSection, self).__init__(dialog, "Extra Assets", collapse=True)

    def build(self):

        self.button_row = ButtonRow(
            self.dialog, "Clear List", "Browse File", "Browse Directory", label="Actions"
        )

        self.scroll_id = self.dialog.register()
        self.path_list_grp_id = self.dialog.register()

        scroll_grp = self.dialog.ScrollGroupBegin(
            id=self.scroll_id,
            flags=c4d.BFH_SCALEFIT,
            inith=100,
            scrollflags=c4d.SCROLLGROUP_VERT | c4d.SCROLLGROUP_HORIZ,
        )

        if scroll_grp:
            grp = self.dialog.GroupBegin(
                id=self.path_list_grp_id,
                flags=c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT,
                title="",
                cols=1,
                groupflags=0,
            )
            if grp:
                self.dialog.GroupBorderSpace(2, 2, 2, 2)

            self.dialog.GroupEnd()  # main
        self.dialog.GroupEnd()  # scroll

        self.dialog.SetDefaultColor(self.path_list_grp_id, c4d.COLOR_BG, BG_COLOR)

    def populate_from_store(self):
        store = self.dialog.store
        self.pathlist = PathList(*(store.assets()))
        self._update_widgets()

    def save_to_store(self):
        store = self.dialog.store
        store.set_assets([p.fslash() for p in self.pathlist])
        store.commit()

    @property
    def clear_button_id(self):
        return self.button_row.button_ids[0]

    @property
    def browse_file_button_id(self):
        return self.button_row.button_ids[1]

    @property
    def browse_directory_button_id(self):
        return self.button_row.button_ids[2]

    def on_plugin_message(self, widget_id, msg):

        # clear list button
        if widget_id == self.clear_button_id:
            self.clear_entries()
        # browse file
        elif widget_id == self.browse_file_button_id:
            fn = c4d.storage.LoadDialog(flags=c4d.FILESELECT_LOAD)
            self.add_entry(fn)
        # browse dir
        elif widget_id == self.browse_directory_button_id:
            fn = c4d.storage.LoadDialog(flags=c4d.FILESELECT_DIRECTORY)
            self.add_entry(fn)
        else:
            # delete one entry button
            path_widget = next(
                (widget for widget in self.path_widgets if widget.delete_btn_id == widget_id), None
            )
            if path_widget:
                self.remove_entry(path_widget.get_value())

    def clear_entries(self):
        self.pathlist = PathList()
        self._update_widgets()
        self.save_to_store()

    def add_entry(self, entry):
        self.pathlist.add(entry)
        self._update_widgets()
        self.save_to_store()

    def remove_entry(self, entry):
        self.pathlist.remove(entry)
        self._update_widgets()
        self.save_to_store()

    def _update_widgets(self):
        self.path_widgets = []
        self.dialog.LayoutFlushGroup(self.path_list_grp_id)
        for path in self.pathlist:
            self.path_widgets.append(PathWidget(self.dialog, path=path.fslash()))
        self.dialog.LayoutChanged(self.path_list_grp_id)

    def resolve(self, expander, **kwargs):
        """Resolve the assets section.
        
        Collect all the assets to be uploaded and return a sub-chunk of the submission payload.
        """

        if not kwargs.get("with_assets"):
            return {
                "upload_paths": "Assets are only shown here if you use the Show Assets button above."
            }
        try:
            result = sorted([p.fslash() for p in self.get_all_assets_path_list()])
            return {"upload_paths": result}
        except ValueError as ex:
            return {"upload_paths": [str(ex)]}

 
    def get_all_assets_path_list(self):
        """Get a list of all assets to be uploaded.

        Returns a PathList object that has no missing files and globs have been expanded. We use the
        cached asset data here and we don't refresh it because, during submission, this function
        could be called after the asset paths in the scene have been manipulated for Linux, and are
        therefore invalid on the local system.
        """

        document = c4d.documents.GetActiveDocument()
        docpath = document.GetDocumentPath()
        path_list = PathList(*self.pathlist)

        for fn in [a["filename"] for a in asset_cache.data()]:
            if not (fn and fn.strip()):
                continue
            if Path(fn).relative:
                fn = os.path.join(docpath, fn)
            path_list.add(fn)

        path_list.add(*scrape_redshift_proxy_assets())

        docfile = Path(os.path.join(docpath, document.GetDocumentName())).fslash()

        path_list.add(docfile)

        missing = path_list.real_files()
        if missing:
            c4d.WriteConsole("The following assets are not on disk:\n")
            for fn in missing:
                c4d.WriteConsole(fn + "\n")
        return path_list


def scrape_redshift_proxy_assets():
    """Scrape Redshift proxy assets from the scene.

    We add the proxy file, although it's likely already in the asset cache. We also get its embedded
    texture list, which is not in the asset cache. 
    
    If the user chose to override the shaders then theoretically we don't need the embedded
    textures. Maybe a future version of the plugin will ignore the enmbedded textures if not needed.
    In the meantime, if they are missing we'll report them as missing during validation and carry
    on. 
    """
    result = []
    docpath =  c4d.documents.GetActiveDocument().GetDocumentPath()
    proxy_entries = [x for x in asset_cache.data() if x["owner"].GetType() == k.REDSHIFT_PROXY_TYPE]
    for proxy in proxy_entries:
        proxy_fn = proxy["assetname"]
        if not proxy_fn:
            continue
        if not os.path.isabs(proxy_fn):
            proxy_fn = os.path.join(docpath, proxy_fn)

        proxy_dir = os.path.dirname(proxy_fn)
        # get texture paths from the proxy
        textures = proxy["owner"][c4d.REDSHIFT_PROXY_MATERIAL_TEXTURES].split("\n")
        for tex in textures:
            if not tex:
                continue
            if not os.path.isabs(tex):
                # relative proxy textures are relative to the proxy file, not the c4d scene.
                tex = os.path.join(proxy_dir, tex)
            result.append(tex)
    return result
