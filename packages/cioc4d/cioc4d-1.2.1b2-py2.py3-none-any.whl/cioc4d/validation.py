import os
import c4d
import sys
import re
from ciopath.gpath import Path
from ciopath.gpath_list import GLOBBABLE_REGEX, PathList
from ciocore.validator import ValidationError, Validator
from cioc4d import const as k
from ciocore import data as coredata
from cioc4d import utils
from cioc4d import asset_cache

DASHES = "-" * 30

RX_DRIVE = re.compile(r"^[A-Z]:(\\|/)", re.IGNORECASE)
class ValidateUploadDaemon(Validator):
    def run(self, _):
        dialog = self._submitter
        use_daemon = dialog.section("UploadOptionsSection").use_daemon_widget.get_value()
        if not use_daemon:
            return

        msg = "This submission expects an uploader daemon to be running.\n"
        msg += 'After you press submit you can open a shell and type:\n"{}" uploader'.format(
            k.CONDUCTOR_COMMAND_PATH
        )

        location = (dialog.section("LocationSection").widget.get_value() or "").strip()
        if location:
            msg = "This submission expects an uploader daemon to be running and set to a specific location tag."
            msg += 'After you press OK you can open a shell and type:\n"{}" uploader --location "{}"\n'.format(
                k.CONDUCTOR_COMMAND_PATH, location
            )
        # By also writing the message to the console, the user can copy paste
        # `conductor uploader --location blah`.
        c4d.WriteConsole(msg)
        c4d.WriteConsole("\n")

        msg += " \nYou'll also find this information in the console.\n"

        self.add_notice(msg)


# class ValidateTaskCount(Validator):
#     def run(self, _):
#         dialog = self._submitter
#         count = dialog.section("InfoSection").frame_count
#         if count > 1000:
#             self.add_notice(
#                 "This submission contains over 1000 tasks ({}). Are you sure this is correct?".format(
#                     count
#                 )
#             )

class ValidatePathLocalization(Validator):
    def run(self, _):
        """
        If the user is on a Mac, validate that asset and 
        rendered output paths match the current user's OS.
        """
        error_msg = ""

        doc = c4d.documents.GetActiveDocument()
        docpath = doc.GetDocumentPath()
        if not docpath:
            return

        # if user platform not "win32", is linux/mac compatible. 
        if sys.platform == "win32":
            return

        # Check asset paths
        windows_paths = utils.windows_paths()
        if windows_paths['assets']:
            error_msg += "All asset paths"
            c4d.WriteConsole(
                        "Please convert the following file asset path(s) to a Mac path:\n {}\n".format(
                            "\n ".join(windows_paths['assets'])
                )
            )
        
        # Check override destination path
        dialog = self._submitter
        tasks_section = dialog.section("TaskSection")
        is_override = tasks_section.override_widget.get_value()

        if is_override:
            try: 
                dest = tasks_section.get_custom_destination(resolve=False)
                if dest and utils.c4d_drive_letter(dest):
                    if error_msg:
                        error_msg += " and the destination override path"
                    else:
                        dest_error = True
                        error_msg = "The Task Template>Destination path on the Conductor Render plug-in"

                    c4d.WriteConsole(
                            "Please convert the following the destination path to a Mac path via Render>Conductor Render>Task Template>Destination:\n {}\n".format(
                                dest)
                    )

            except BaseException:
                return
                
        # Check rendered output paths
        else:
            if windows_paths['outputs']:
                if error_msg:
                    error_msg += " and rendered output paths"
                else:
                    error_msg = "All rendered output paths"

                c4d.WriteConsole(
                            "Please convert the following rendered output path(s) to a Mac path via Render>Edit Render Settings...:\n {}\n".format(
                                "\n ".join(windows_paths['outputs'])
                    )
                )

        if error_msg:
            error_msg += " must be Mac compatible, please see console for details."
            self.add_error(error_msg)
            
class ValidateGPU(Validator):
    """
    Validate the suitability of the chosen instance type.

    If the renderer configuration requires a GPU but no GPU-enabled instance type is selected, add a validation error.
    If a GPU instance type is selected, but the renderer doesn't require it, add a validation warning.
    """

    def run(self, _):
        dialog = self._submitter

        document = c4d.documents.GetActiveDocument()
        render_data = document.GetActiveRenderData()
        renderer = render_data[c4d.RDATA_RENDERENGINE]

        name = dialog.section("GeneralSection").instance_types_widget.get_selected_content_value()

        instance_type = coredata.data()["instance_types"].find(name)


        if renderer == k.RENDERERS["redshift"]:

            if not (instance_type and instance_type["gpu"]):
                msg = "The Redshift renderer is not compatible with the instance type: '{}' as it has no graphics card.\n".format(
                    instance_type["description"]
                )
                msg += "Please select a machine with a graphics card in the General section of the submitter. The submission is blocked as it would incur unexpected costs."
                self.add_error(msg)
            return

        # Not Redshift
        if instance_type and instance_type["gpu"]:

            msg = "You have selected an instance type with a graphics card: '{}', yet the chosen renderer in RenderSettings does not benefit from a GPU.".format(
                 instance_type["description"]
            )
            msg += " This could incur extra costs. Do not continue unless you are absolutely sure."
            self.add_warning(msg)


class ValidateDestinationDirectoryClash(Validator):
    def run(self, _):
        dialog = self._submitter
        bad_dest_msg = "There was an error while trying to resolve the destination directory."

        tasks_section = dialog.section("TaskSection")
        is_override = tasks_section.override_widget.get_value()

        if is_override:
            try:
                bad_dest_msg += (
                    "Please check the value for the destination folder in the submitter."
                )
                dest = tasks_section.get_custom_destination()
                dest_path = Path(dest).fslash(with_drive=False)
            except BaseException:
                self.add_error(bad_dest_msg)
                return
        else:
            try:
                bad_dest_msg += (
                    "Please check that your image paths all save to the same filesystem."
                )
                dest = utils.get_common_render_output_destination()
                dest_path = Path(dest).fslash(with_drive=False)
            except BaseException:
                self.add_error(bad_dest_msg)
                return

        path_list = dialog.section("AssetsSection").get_all_assets_path_list()

        for gpath in path_list:
            asset_path = gpath.fslash(with_drive=False)
            # NOTE: It's a gpath, so "startswith" is synonymous with "is contained in"
            if asset_path.startswith(dest_path):
                c4d.WriteConsole(
                    "Some of your upload assets exist in the specified output destination directory\n. {} contains {}.".format(
                        dest_path, asset_path
                    )
                )
                self.add_error(
                    "The destination directory for rendered output ({}) contains assets that are in the upload list. This can cause your render to fail. See the Python tab of the console for details.".format(
                        dest_path
                    )
                )
                break
            if dest_path.startswith(asset_path):
                c4d.WriteConsole(
                    "You are trying to upload a directory that contains your destination directory.\n. {} contains {}\n".format(
                        asset_path, dest_path
                    )
                )
                self.add_error(
                    "One of your assets is a directory that contains the specified output destination directory. This will cause your render to fail. See the Python tab of the console for details.\n"
                )
                break



class ValidatePortableRSProxy(Validator):
    def run(self, _):
        bad_assets = []
        assets = asset_cache.data()
        for asset in assets:
            
            if not asset["owner"].GetType() == k.REDSHIFT_PROXY_TYPE:
                continue
            
            if asset["owner"][c4d.REDSHIFT_PROXY_MATERIAL_MODE] > 0:
                # not using embedded materials/textures
                continue

            paramId = c4d.REDSHIFT_PROXY_MATERIAL_TEXTURES

            textures = asset["owner"][paramId].split("\n")
            for tex in textures:
                if RX_DRIVE.match(tex):
                    bad_assets.append((asset["owner"].GetName(), tex))

        if bad_assets:
        
            self.add_warning(
                """Some of your Redshift proxies are not portable as they contain absolute Windows texture paths. 
These textures won't show up on objects. See the Python console for details."""
                )
            c4d.WriteConsole(
                    "The following Redshift proxies are not portable as they contain absolute Windows texture paths:\n"
                )
            for proxy, tex in bad_assets:
                c4d.WriteConsole(
                    "Proxy: {} contains texture: {}\n".format(proxy, tex)
                )
            c4d.WriteConsole(
                    "Visit https://help.maxon.net/c4d/en-us/Default.htm#_REDSHIFT_/html/Intro+to+Proxies.html for more information on RS Proxy textures.\n"
                )

class ValidateCustomTaskTemplate(Validator):
    def run(self, _):
        dialog = self._submitter
        tasks_section = dialog.section("TaskSection")
        if not tasks_section.override_widget.get_value():
            return

        self.add_notice(
            "If you set any absolute paths here (e.g. -oimage or -omultipass), make sure they do not have drive letters since the tasks are be executed on Linux filesystems."
        )
        self.add_notice(
            "Please ensure the destination folder is an ancestor of all the output images. This is important, since the destination folder defines the only writable location on the Linux filesystem."
        )


class ValidateMissingAssets(Validator):
    def run(self, _):
        """
        Display a list of dependency assets that are not on disk.

        Don't include c4d files in the list because the doc itself may not have been saved yet.
        """
        document = c4d.documents.GetActiveDocument()
        docname =  document.GetDocumentName()
        docpath = document.GetDocumentPath()
        docfile = os.path.join(docpath, docname)
        missing_extra_assets = []
        assets_section = self._submitter.section("AssetsSection")
        for gpath in assets_section.pathlist:
            pp = gpath.fslash()
            if not os.path.exists(pp):
                missing_extra_assets.append(pp)

        if missing_extra_assets:
            self.add_warning(
                "Some of the assets specified in the Extra Assets section do not exist on disk. See the console for details. You can continue if you don't need them."
            )

        scraped_assets = asset_cache.data()

        missing_scraped_assets = []
        for a in scraped_assets:
            if a["exists"]:
                continue
            fn = a["assetname"]
            if not fn or not fn.strip():
                continue

            try:
                Path(fn)
            except ValueError:
                # Empty or invalid path, ignore
                continue
            
            # It might exist, but c4d doesn't know that due to a relative path bug
            if Path(fn).relative:
                fn = os.path.join(docpath, fn)
                if os.path.exists(fn):
                    continue

            if fn == docfile:
                continue
            missing_scraped_assets.append(fn)

        if missing_scraped_assets:
            self.add_warning(
                """Some of the scraped assets do not exist on disk. You can continue if you don't need them. See the console for details."""
            )
        if missing_scraped_assets or missing_extra_assets:
            c4d.WriteConsole("----- Conductor Asset Validation -------\n")

            for asset in missing_scraped_assets:
                c4d.WriteConsole("Missing scraped asset: {}\n".format(Path(asset).fslash()))

            for asset in missing_extra_assets:
                c4d.WriteConsole("Missing extra asset: {}\n".format(Path(asset).fslash()))



class ValidateDontSaveVideoPosts(Validator):

    GI_AUTOSAVE_ID = 3804
    AO_AUTOSAVE_ID = 2204
    AO_USE_CACHE_ID = 2000

    def run(self, _):
        document = c4d.documents.GetActiveDocument()
        render_data = document.GetActiveRenderData()
        vp = render_data.GetFirstVideoPost()
        while vp:
            if vp.CheckType(c4d.VPglobalillumination):
                self._validate_video_post(vp, "Global Illumination", self.GI_AUTOSAVE_ID)
            elif vp.CheckType(c4d.VPambientocclusion):
                self._validate_video_post(
                    vp, "Ambient occlusion", self.AO_AUTOSAVE_ID, self.AO_USE_CACHE_ID
                )
            vp = vp.GetNext()

    def _validate_video_post(self, vp, label, *ids):
        if vp.GetBit(c4d.BIT_VPDISABLED):
            return
        container = vp.GetDataInstance()
        for element_id in ids:
            if not container[element_id]:
                return

        self.add_warning(
            "{} Auto Save is set to ON. You should turn it off for the render, otherwise it may try to write files in a read-only directory and cause the render to fail".format(
                label
            )
        )


class ValidateScoutFrames(Validator):
    def run(self, _):
        """
        Add a validation warning for a potentially costly scout frame configuration.
        """
        info_section = self._submitter.section("InfoSection")

        scout_count = info_section.scout_frame_count
        frame_count = info_section.frame_count

        if frame_count < 5:
            return

        if scout_count < 5 and scout_count > 0:
            return

        if scout_count == 0 or scout_count == frame_count:
            msg = "All tasks will start rendering."
            msg += " To avoid unexpected costs, we strongly advise you to configure scout frames so that most tasks are initially put on hold. This allows you to check a subset of frames and estimate costs before you commit a whole sequence."
            self.add_warning(msg)

        if scout_count and (info_section.task_count != info_section.frame_count):
            msg = "You have chunking set higher than 1."
            msg += " This can cause more scout frames to be rendered than you might expect. ({} scout frames).".format(
                scout_count
            )
            self.add_warning(msg)

class ValidateDestinationDirectoryTokens(Validator):
    def run(self, _):
            """
            Add a validation error if there are any error-causing tokens that
            should be filtered from the rendered output paths (Regular Image,
            Multipass Image, or the submitter override path.)

            Add a validation warning for all other tokens. Exception made for
            the $take token when 'Marked' takes are selected for rendering.
            """
            # check takes widget 
            general_section = self._submitter.section("GeneralSection")
            takes_widget_value = general_section.takes_widget.get_selected_value() 
            is_marked_takes = takes_widget_value == "Marked"

            # collect all image paths
            image_paths = {}

            dialog = self._submitter
            tasks_section = dialog.section("TaskSection")
            is_override = tasks_section.override_widget.get_value()

            if is_override:
                try:
                    override_path = tasks_section.destination_widget.get_value()
                    dest = tasks_section.get_custom_destination()
                    dest_path = Path(dest).fslash(with_drive=False)

                    image_paths = {
                        "override":
                            {
                                "unresolved_tokens": override_path,
                                "resolved_tokens": dest_path
                            }
                        }
                except BaseException:
                    return
                
            img_pths = utils.get_image_paths()

            if not img_pths:
                return
            
            img_pths = utils.get_image_paths(convert_tokens=False, filter_none=False)
            render_paths = utils.get_image_paths(filter_none=False)
            dest_path = ""

            if img_pths[0] is not None:
                image_paths['regular'] = {
                        "unresolved_tokens":img_pths[0], 
                        "resolved_tokens":render_paths[0]
                    }
            if img_pths[1] is not None:
                image_paths['multipass'] = {
                        "unresolved_tokens": img_pths[1],
                        "resolved_tokens":render_paths[1]
                    }           
            
            # categorize tokens into error and warning causing tokens
            error_tokens = ["$YYYY", "$MM", "$DD", "$hh", "$mm", "$ss", "$computer", "$username"]
            error_tokens_regex = {"$YY":"\$YY[^Y]|\$YY$"}

            all_tokens = ["${}".format(t['_token']) for t in c4d.modules.tokensystem.GetAllTokenEntries()]
            warning_tokens = list(filter(lambda token: token not in error_tokens, all_tokens))

            if is_marked_takes:
                warning_tokens.remove("$take")

            token_types = {"error": {"standard": error_tokens, "regex": error_tokens_regex},
                           "warning": warning_tokens
                           }
            
            # detect error and warning causing tokens in image paths
            found_tokens = {"error": {},
                            "warning": {}
                            }

            for path_name, path_info in image_paths.items():
                pth = path_info['unresolved_tokens']

                tokens = []
                for token in token_types['error']['standard']:
                    if token in pth and token not in tokens:
                        tokens.append(token)
                
                for token, token_regex in token_types['error']['regex'].items():
                    if re.search(token_regex, pth):
                        tokens.append(token)
                found_tokens['error'][path_name] = tokens

                tokens = []
                for token in token_types['warning']:
                    if token in pth and token not in tokens:
                        tokens.append(token)
                found_tokens['warning'][path_name] = tokens

            # create warning and error messages
            error_msg = ""
            warning_msg = ""

            for path_name, path_info in image_paths.items():
        
                pth = path_info['unresolved_tokens']

                found_error_tokens = found_tokens['error'][path_name]
                if found_error_tokens:
                    output_path_name = ""
                    if path_name == "override":
                        setting_path = "Conductor Renderer > Task Template > Destination"
                        output_path_name = "Conductor override"
                    else:
                        setting_path = "Render > Edit Render Settings... > Save > "
                        if path_name == "regular":
                            output_path_name = "Regular Image"
                        else:
                            output_path_name = "Multi-pass Image"
                        setting_path += output_path_name + " > File"

                    error_msg += ("\nError causing tokens were detected in the {} rendered output" \
                            " path ({}): {}.\nThis setting may be changed" \
                            " under {}.\n".format(
                                                output_path_name, 
                                                pth, 
                                                ", ".join(found_error_tokens), 
                                                setting_path
                                                )
                        )
                    
                found_warning_tokens = found_tokens['warning'][path_name]
                if found_warning_tokens:
                    warning_msg += ("The rendered output path ({}) contains the following token(s):" \
                            " {}.".format(pth, ", ".join(found_warning_tokens))
                        )
            
            if error_msg:
                c4d.WriteConsole(error_msg)
                self.add_error(("Error-causing tokens were detected in the rendered output path. Please" \
                                " remove these tokens, see the Python tab of the console for details.")
                )

            if warning_msg:
                self.add_warning(("{} These tokens will resolve according to your .c4d file settings at render download time," \
                            " which might vary from your settings at upload time.".format(warning_msg))
                            )
                
class ValidateResolvedChunkSize(Validator):
    def run(self, _):
        """
        Add a validation notice when auto-chunking has occured.
        """
        frames_section = self._submitter.section("FramesSection")
        chunk_size = frames_section.chunk_size_widget.get_value()

        try: 
            main_sequence = frames_section.get_sequence()
        except (ValueError, TypeError):
            return

        general_section = self._submitter.section("GeneralSection")
        takes_widget_value = general_section.takes_widget.get_selected_value() 
        is_marked_takes = takes_widget_value == "Marked"

        if chunk_size < main_sequence.chunk_size: 
            total_tasks = main_sequence.chunk_count()

            if is_marked_takes:
                num_takes = len(general_section.resolve_marked_takes())
                if num_takes > 1:
                    total_tasks = total_tasks * num_takes

            self.add_notice(("The number of frames per task has been automatically" \
                            " adjusted from {} to {} to bring the total number of " \
                            "tasks below {} ({}). If you have a critical deadline" \
                            " and need each frame to run on a single instance, " \
                            " consider splitting the frame range. Alternatively, " \
                            "contact Conductor customer support.").format(
                                 chunk_size,
                                 main_sequence.chunk_size,
                                 k.MAX_TASKS, 
                                 total_tasks)
                                 )

class ValidateDocumentDirectorySpaces(Validator):
    def run(self, _):
        """
        Add a validation error for consecutive spaces in file path.
        """

        doc = c4d.documents.GetActiveDocument()
        ciodoc = doc.GetDocumentPath()

        if ciodoc:
            ciodoc = Path(ciodoc).fslash(with_drive=False)
        else:
            return

        if "  " in ciodoc:
            folders = ciodoc.split(os.sep)
            error_folders = [f for f in folders if "  " in f]
            add_quotes = lambda s: "'" + s + "'"
            c4d.WriteConsole(
                    ("\nDouble spaces were detected in the following folder name(s) of the document path: {}." \
                    "\nPlease re-save your file to a path with no spaces.\n".format(" ,".join(
                        list(map(add_quotes, error_folders))))
                    )
                )
            self.add_error(
                    ("Please remove all double spaces from the file path ({})." \
                        " Double spaces will cause the render to fail. See the Python tab of the console for" \
                        " details.".format(ciodoc)
                    )
                )

class ValidateDestinationDirectorySpaces(Validator):
    def run(self, _):
        """
        Add a validation error for consecutive spaces in file output path.
        """
        dialog = self._submitter
        tasks_section = dialog.section("TaskSection")
        is_override = tasks_section.override_widget.get_value()

        dest_path = ""

        if is_override:
            try:
                dest = tasks_section.get_custom_destination()
                dest_path = Path(dest).fslash(with_drive=False)
            except BaseException:
                return
        else:
            try:
                dest = utils.get_common_render_output_destination()
                dest_path = Path(dest).fslash(with_drive=False)
            except BaseException:
                return

        if "  " in dest_path:
            folders = dest_path.split(os.sep)
            error_folders = [f for f in folders if "  " in f]
            add_quotes = lambda s: "'" + s + "'"
            c4d.WriteConsole(
                    ("\nDouble spaces were detected in the following folder name(s) of the render output path: {}." \
                    "\nThis setting may be changed under Render > Edit Render Settings... > Save > " \
                    "File.\n".format(" ,".join(list(map(add_quotes, error_folders))))
                    )
                )
            self.add_error(
                    ("Please remove all double spaces from the destination directory for rendered output ({})." \
                        " Double spaces will cause the render to fail. See the Python tab of the console for" \
                        " details.".format(dest_path)
                    )
                )

class ValidateMarkedTakes(Validator):
    def run(self, _):
        """
        Add a validation warning to check that the user has selected
        at least one marked take, if they selected "Marked" takes for rendering.
        """
        dialog = self._submitter
        general_section = dialog.section("GeneralSection")
        takes_widget_value = general_section.takes_widget.get_selected_value() 

        if takes_widget_value == "Marked":
            marked_takes = general_section.resolve_marked_takes()

            if len(marked_takes) == 0:
                c4d.WriteConsole(("'Marked' takes have been selected in the General Section,\n" \
                    "but no takes have been marked for submission. Please mark (checkbox) a take.")
                )
                self.add_warning(("'Marked' takes have been selected in the General Section, " \
                    "but no takes have been marked for submission. Please mark (checkbox) a take.")
                )

class ValidateMarkedTakesOutputPathToken(Validator):
    def run(self, _):
        """
        Add a validation error requiring user include the $take token in their
        output path filename if they selected "Marked" takes for rendering.
        """
        dialog = self._submitter
        general_section = dialog.section("GeneralSection")
        takes_widget_value = general_section.takes_widget.get_selected_value() 

        if takes_widget_value == "Marked":
            image_paths = {}

            tasks_section = dialog.section("TaskSection")
            is_override = tasks_section.override_widget.get_value()

            # Assess override output path
            if is_override:
                try:
                    # Get path head and tail
                    override_path = tasks_section.destination_widget.get_value()

                    pth_head = ""
                    pth_components = Path(override_path).components
                    if len(pth_components) > 1:
                        pth_head = Path(pth_components[:-1]).fslash(with_drive=False)
                
                    pth_tail = Path(pth).tail

                    # Generate error msg
                    if "$take" not in pth_tail:
                        msg = ("Please include the $take token in" \
                            " your override output path ({}) filename.")

                        if "$take" in pth_head:
                            msg += ("Do not include" \
                            " $take in the name of a folder, this will result" \
                            " in a failed render.")
                        c4d.WriteConsole(msg.format(override_path))
                        self.add_error(msg.format(override_path))
                    return
                except BaseException:
                    return
                
            # Assess regular/multi-pass output paths
            img_pths = utils.get_image_paths()

            if not img_pths:
                return
            
            img_pths = utils.get_image_paths(convert_tokens=False, filter_none=False)
            image_paths = {}

            regular_path = img_pths[0]
            multipass_path = img_pths[1]

            if regular_path:
                image_paths['regular'] = img_pths[0]
            if multipass_path:
                image_paths['multipass'] = img_pths[1]

            # Generate error message
            msg = "Please include the $take token in your "
            is_token_in_path_head = False
            error_paths = []

            for pth_name, pth in image_paths.items():
                # Get path head and tail
                pth_head = ""
                pth_components = Path(pth).components
                if len(pth_components) > 1:
                    pth_head = Path(pth_components[:-1]).fslash(with_drive=False)
                
                pth_tail = Path(pth).tail

                # Data for error msg
                if "$take" not in pth_tail:
                    error_paths.append("{} ({})".format(pth_name, pth))

                if "$take" in pth_head:
                    is_token_in_path_head=True

            if error_paths:
                if len(error_paths) == 1:
                    msg += error_paths[0] + " output path's filename." 
                else:
                    msg += " and ".join(error_paths) +  " output paths' filenames."
                
                if is_token_in_path_head:
                    msg_footer = " Do not include it in the name of a folder, this will result in a failed render."
                    msg += msg_footer

                c4d.WriteConsole(msg)
                self.add_error(msg)

class ValidateUniqueTakeNames(Validator):
    def run(self, _):
        """
        Add a validation error when user tries to submit multiple takes
        with the same name.
        """
        dialog = self._submitter
        general_section = dialog.section("GeneralSection")
        takes_widget_value = general_section.takes_widget.get_selected_value() 

        repeating_takes = set()
        takes_set = set()

        if takes_widget_value == "Marked":

            marked_takes = general_section.resolve_marked_takes_names() 
            for mt in marked_takes:
                if mt not in takes_set:
                    takes_set.add(mt)
                else:
                    repeating_takes.add(mt)
        
        if repeating_takes:
            c4d.WriteConsole(
                        ("All marked takes must have unique names. Please modify " \
                            "the following take(s):\n{}.".format(", ".join(repeating_takes))
                        )
                    )
            self.add_error(
                        ("All marked takes must have unique names. Please modify " \
                            "the following take(s): {}.".format(", ".join(repeating_takes))
                        )
                    )

class ValidateTakeNamesQuotations(Validator):
    def run(self, _):
        """
        Add a validation error when user tries to submit takes with quotes
        in the name. 
        """
        dialog = self._submitter
        general_section = dialog.section("GeneralSection")
        takes_widget_value = general_section.takes_widget.get_selected_value() 

        quotes = ['"', "'"]

        if takes_widget_value == "Current":

            take_name = general_section.resolve_current_take_name()

            for q in quotes:
                if q in take_name:
                    c4d.WriteConsole(
                        ("Please remove all quotes from your currently selected" \
                        " take: {}.").format(take_name)
                    )
                    self.add_error(
                        ("Please remove all quotes from your currently selected" \
                        " take: {}.").format(take_name)
                    )
                    return
        else:

            takes_with_quotes = set()
            marked_takes = general_section.resolve_marked_takes_names() 

            for mt in marked_takes:
                for q in quotes:
                    if q in mt:
                        takes_with_quotes.add(mt)
            
            if takes_with_quotes:
                c4d.WriteConsole(
                    ("Please remove all quotes from these marked take(s): " \
                    "{}.").format(", ".join(takes_with_quotes))
                )
                self.add_error(
                    ("Please remove all quotes from these marked take(s): " \
                    "{}.").format(", ".join(takes_with_quotes))
                )


# Implement more validators here
####################################
####################################


def run(dialog, submitting=True):

    errors, warnings, notices = _run_validators(dialog)
    msg = ""
    if errors:
        errstr = "\n\n".join(errors)
        msg += "\nSome errors would cause the submission to fail:\n\n{}\n".format(errstr)
        c4d.gui.MessageDialog(msg, type=c4d.GEMB_OK)
        raise ValidationError(msg)
    if notices or warnings:
        if submitting:
            msg += "Would you like to continue this submission?\n\n"
            dialog_type = c4d.GEMB_OKCANCEL
        else:
            msg = "Validate only.\n\n"
            dialog_type = c4d.GEMB_OK

        if warnings:
            msg += (
                "Please check the warnings below:\n\n"
                + "\n\n".join(["[WARN]:{}".format(w) for w in warnings])
                + "\n\n"
            )
        if notices:
            msg += (
                "Please check the notices below:\n\n"
                + "\n\n".join(["[INFO]:{}".format(n) for n in notices])
                + "\n\n"
            )

        if submitting:
            dialog.show_progress_bar()

        result = c4d.gui.MessageDialog(msg, type=dialog_type)
        if result != c4d.GEMB_R_OK:
            c4d.WriteConsole("[Conductor] Submission cancelled by user.\n")
            raise ValidationError(msg)
        return result
    else:
        if not submitting:
            msg = "No issues found!"
            result = c4d.gui.MessageDialog(msg, type=c4d.GEMB_OK)


def _run_validators(dialog):

    takename = "Main"
    validators = [plugin(dialog) for plugin in Validator.plugins()]
    for validator in validators:
        validator.run(takename)

    errors = list(set.union(*[validator.errors for validator in validators]))
    warnings = list(set.union(*[validator.warnings for validator in validators]))
    notices = list(set.union(*[validator.notices for validator in validators]))
    return errors, warnings, notices
