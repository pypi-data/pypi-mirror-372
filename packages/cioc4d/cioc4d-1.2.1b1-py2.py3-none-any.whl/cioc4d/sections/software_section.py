
import re
from ciocore import data as coredata

from cioc4d.const import C4D_VERSION_FULL
from cioc4d.widgets.combo_box_grp import ComboBoxGrp
from cioc4d.sections.collapsible_section import CollapsibleSection
from ciocore.package_environment import PackageEnvironment


class SoftwareSection(CollapsibleSection):

    ORDER = 20

    def __init__(self, dialog):
        self.host_version_widget = None
        self.renderer_widget = None
        super(SoftwareSection, self).__init__(
            dialog, "Software", collapse=False)

    def build(self):
        self.host_version_widget = ComboBoxGrp(
            self.dialog, label="Cinema 4D Version")
        self.renderer_widget = ComboBoxGrp(self.dialog, label="Renderer")

    def populate_from_store(self):
        self.update_combo_items()

    def save_to_store(self):
        store = self.dialog.store
        store.set_host_version(self.host_version_widget.get_selected_value())
        store.set_renderer_version(self.renderer_widget.get_selected_value())
        store.commit()


    def on_plugin_message(self, widget_id, msg):

        if widget_id == self.dialog.foot_grp.connect_button_id:
            self.update_combo_items()
        elif widget_id == self.host_version_widget.combo_box_id:
            self.update_renderers_combo_items()
        
        if widget_id in self._store_affectors:
            self.save_to_store()

    def update_combo_items(self):
        self.host_version_widget.set_items(["-- Not Connected --"])
        self.renderer_widget.set_items(["-- Not Connected --"])
        if coredata.valid():
            store = self.dialog.store
            software_data = coredata.data()["software"]
            host_names = software_data.supported_host_names()
            major_minor_patch_sort = lambda x: [int(x.split(" ")[1].split(".")[0]), 
                                                int(x.split(" ")[1].split(".")[1])]
            host_names.sort(key=major_minor_patch_sort)
            if not host_names:
                return
            
            host_version = str(C4D_VERSION_FULL)
            version_match_index = self.match_software_version(host_names, 
                                                               host_version)
            self.host_version_widget.set_items(
                host_names, default_value=host_names[version_match_index])
            self.update_renderers_combo_items()

    def match_software_version(self, host_names, host_version):
        """Returns index of best version match from host_names.
        If there is no match found, returns the most recent software version 
        available.

        Ex.
        host_names = ["cinema4d 23.110 linux", "cinema4d 2023.3.5 linux"]
        host_version = "cinema4d 2024.2"
        Returns: -1

        Parameters:
            (str list) host_names: Sorted list of Conductor available software vers
            (str list) host_version: Software version of client's Cinema4D 
        Returns:
            (int): Index of best software version match from host_names
        """
        host_versions_parsed = []

        if len(host_version) == 5:
            #version is stored in format of  ##.### ex. 23.111
            major = host_version[0:2]
            minor = host_version[2:]
            host_versions_parsed.extend([".".join([major, minor]),
                                       major])
        else:
            #version is stored in format of ####.#.## ex. 2023.1.02
            major = host_version[0:4]
            minor = host_version[4]
            patch = str(int(host_version[5:])) # ex. "02" -> "2"
            host_versions_parsed.extend([".".join([major, minor,patch]),
                                       ".".join([major, minor]),
                                       major])

        host_names = [h.split(" ")[1] for h in host_names]

        for host_ver in host_versions_parsed:
            matches = list(filter(lambda x:x.startswith(host_ver), host_names))
            if matches:
                return host_names.index(matches[-1])

        return -1

    def update_renderers_combo_items(self):
        host = self.host_version_widget.get_selected_value()
        software_data = coredata.data()["software"]
        store = self.dialog.store

 
        renderers = software_data.supported_plugins(host)
        if not renderers:
            self.renderer_widget.set_items(["-- Default Renderer --"])
            return
        renderer_names = ["-- Default Renderer --"]
        for renderer in renderers:
            for version in renderer["versions"]:
                renderer_names.append("{} {}".format(
                    renderer["plugin"], version))
        self.renderer_widget.set_items(
            renderer_names, default_value=store.renderer_version())

    def resolve(self, expander, **kwargs):
        extra_env = self.dialog.section(
            "EnvironmentSection").get_entries(expander)

        packages_data = self.get_packages()
        if not packages_data:
            return {"software_package_ids": "INVALID"}

        packages_data["env"].extend(extra_env)
        return {
            "environment": dict(packages_data["env"]),
            "software_package_ids": packages_data["ids"]
        }

    def get_packages(self):
        if not coredata.valid():
            return
        tree_data = coredata.data()["software"]
        paths = []
        host_path = self.host_version_widget.get_selected_value()
        
        # we have to query the package-tree with the platform for both the host AND the renderer.
        # The renderer label does not contain the platform, so we have to add it.
        # Example:
        # tree.find_by_path('cinema4d 2023.2.1 linux/redshift-cinema4d 3.5.15 linux')
        renderer = self.renderer_widget.get_selected_value()
        platform = host_path.split()[-1] 
        if platform in ["windows", "linux"]:
            renderer = "{} {}".format(renderer, platform)
            
        renderer_path = "{}/{}".format(host_path, renderer)

        paths = [host_path, renderer_path]

        result = {
            "ids": [],
            "env": PackageEnvironment()
        }
        
        packages = [tree_data.find_by_path(path) for path in paths if path]
        
        for package in packages:
            if not package:
                continue
            result["ids"].append(package["package_id"])
            result["env"].extend(package)

        return result

    def get_preview_affectors(self):
        return [
            self.host_version_widget.combo_box_id,
            self.renderer_widget.combo_box_id
        ]

    def get_selected_renderer_name(self):
        """Returns the selected renderer name without version.
        """
        return self.renderer_widget.get_selected_value().split()[0]
