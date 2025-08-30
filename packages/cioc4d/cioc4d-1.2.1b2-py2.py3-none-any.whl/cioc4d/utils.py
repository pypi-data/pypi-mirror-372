import c4d
import os
import sys
import re
from ciopath.gpath_list import PathList
from ciopath.gpath import Path
from cioc4d import const as k
from cioc4d import asset_cache
from contextlib import contextmanager

import logging

logger = logging.getLogger(__name__)

RX_PARAM_ID = re.compile(r".* with ID (\d+) at.*")


def rpd():
    """Get the render path data object, required for token replacement."""
    document = c4d.documents.GetActiveDocument()
    render_data = document.GetActiveRenderData()
    return {
        "_doc": document,
        "_rData": render_data,
        "_rBc": render_data.GetDataInstance(),
        "_take": document.GetTakeData().GetCurrentTake(),
    }


def get_common_render_output_destination():
    """
    Use common path of the outputs for destination directory.
    """
    document = c4d.documents.GetActiveDocument()
    doc_path = document.GetDocumentPath()

    image_paths = get_image_paths()
    out_paths = [
        Path(os.path.join(doc_path, pth)) if Path(pth).relative else Path(pth)
        for pth in image_paths
    ]

    if not out_paths:
        c4d.WriteConsole("No render output paths. Can't determine a common destination folder.\n")
        return ""

    out_dirs = [os.path.dirname(p.fslash()) for p in out_paths]

    try:
        common_path = PathList(*out_dirs).common_path()
    except BaseException:
        c4d.WriteConsole(
            "An error occurred while trying to determine a common destination folder.\n"
        )
        return ""

    return truncate_path_to_unresolved_token(common_path.fslash())


def truncate_path_to_unresolved_token(in_path):
    """
    Make sure the path contains no unresolved tokens (dollar signs).

    If it does, truncate the path up to the component containing the dollar sign.

    Args:
        in_path (str): The path to examine.

    Returns:
        [str]: Possibly truncated path
    """

    result = in_path
    while True:
        if not "$" in result:
            return result
        result = os.path.dirname(result)


def get_image_paths(convert_tokens=True, filter_none=True):
    """A list containing paths of active output images."""

    document = c4d.documents.GetActiveDocument()
    render_data = document.GetActiveRenderData()

    if filter_none:
        return list(
            filter(
                None,
                [
                    get_resolved_image_path(render_data, c4d.RDATA_PATH, convert_tokens),
                    get_resolved_image_path(render_data, c4d.RDATA_MULTIPASS_FILENAME, convert_tokens),
                ],
            )
        )
    return [
                get_resolved_image_path(render_data, c4d.RDATA_PATH, convert_tokens),
                get_resolved_image_path(render_data, c4d.RDATA_MULTIPASS_FILENAME, convert_tokens),
            ]


def set_image_path(render_data, path_key, value):
    render_data[path_key] = value


def get_resolved_image_path(render_data, path_key, convert_tokens=True):
    """Return the output image path as string if it is active.

    path_key determines whether we are dealing at single image field or multipass image.

    According to the convert_tokens flag, we convert any C4D tokens that are in context.
    """
    save_enabled = render_data[c4d.RDATA_GLOBALSAVE]
    if not save_enabled:
        return

    if path_key == c4d.RDATA_MULTIPASS_FILENAME:
        do_image_save = render_data[c4d.RDATA_MULTIPASS_SAVEIMAGE]
    else:
        do_image_save = render_data[c4d.RDATA_SAVEIMAGE]

    if not do_image_save:
        return

    try:
        if convert_tokens:
            image_path = c4d.modules.tokensystem.FilenameConvertTokens(render_data[path_key], rpd())
        else:
            image_path = render_data[path_key]
    except SystemError:
        return

    return image_path


def relative_path(original_value, docpath):
    """
    Convert absolute path to relative path.
    """
    relpath = Path(original_value)
    relpath.make_relative_to(docpath)
    return relpath.fslash()


@contextmanager
def posix_filepaths(dry_run=False):
    """
    Do some work in the context of a scene that has posix compatible filepaths.

    We make all paths relative and replace backslashes with forward slashes for asset paths and
    active output paths. While the scene has posix paths, it is not guaranteed to maintain
    commpatibility with Windows. It should be used to create a scene to ship to Linux only.

    NOTE: We can't simply strip drive letters to make absolute posix paths because the forward
    slashes for absolute paths are converted back to backslashes by c4d, leaving the file in a state
    that will not be valid on Linux.

    Assets can be anything in the asset_cache, i.e. anything returned by GetAllAssets(). If an asset
    has paramId = -1, it's possibly a redshift proxy or shader, and needs to be handled differently.

    We also adjust the output paths stored in render data.

    Args:
        dry_run (bool): If True, do not change the scene.

    Redshift Proxy: abs path without drive letters

    If you want to test this function and see what would be changed, you can use the following
    commands:

    from cioc4d import utils
    with utils.posix_filepaths(dry_run=True) as changes:
        for change in changes:
            print(change)
    # TODO: Add the above function as a menu item. Also, have it log assets that could not be resolved.
    """
    doc = c4d.documents.GetActiveDocument()
    docpath = Path(doc.GetDocumentPath())

    assets = asset_cache.data()
    changes = []
    for asset in assets:

        if asset["owner"].GetType() == k.REDSHIFT_PROXY_TYPE:
            
            try:
                param_tuple = (c4d.REDSHIFT_PROXY_FILE, c4d.REDSHIFT_FILE_PATH)
                original_value = asset["owner"][param_tuple]
                if original_value and os.path.isabs(original_value):
                    changes.append(
                        {
                            "owner": asset["owner"],
                            "paramId": param_tuple,
                            "original_value": original_value,
                            "new_value": Path(original_value).fslash(with_drive=False),
                        }
                    )
                continue

            except AttributeError:
                logger.warning("It loos like REDSHIFT_PROXY_TYPE is being shared by some other object/plugin")
                # This means k.REDSHIFT_PROXY_TYPE is being shared by some other object/plugin.
                

        if asset["owner"].GetType() == k.REDSHIFT_TEXTURE_TYPE:            
            try:
                # These Redshift variables are only present if the plugin is loaded
                # k.REDSHIFT_TEXTURE_TYPE actually represents a generic C4D node
                # see the const.py module for a complete explanation
                param_tuple = (c4d.REDSHIFT_SHADER_TEXTURESAMPLER_TEX0, c4d.REDSHIFT_FILE_PATH)
                original_value = asset["owner"][param_tuple]
                if original_value and os.path.isabs(original_value):
                    changes.append(
                        {
                            "owner": asset["owner"],
                            "paramId": param_tuple,
                            "original_value": original_value,
                            "new_value": Path(original_value).fslash(with_drive=False),
                        }
                    )
                continue

            except AttributeError:
                logger.warning("It looks like REDSHIFT_TEXTURE_TYPE is being shared by some other object/plugin")
                # This means k.REDSHIFT_TEXTURE_TYPE is being shared by some other object/plugin
            except TypeError:
                # This error occurs when os.path.isabs() is given a non-string value
                logger.warning("It looks like the REDSHIFT_TEXTURE_TYPE asset has an invalid file path.")
                continue

            # NOTE: Previously at this point, we tried to detect absolute Windows texture paths in
            # RS proxies and override them. However, this is simply not possible. If customers have
            # proxies with absolute Windows paths they must override the texture in the scene. We
            # provide a validation step instead to warn them if we find proxy textures that have
            # not been overridden.

            # The paramId, in case it turns out that it is possible, is
            # c4d.REDSHIFT_PROXY_MATERIAL_TEXTURES and the value is a multiline list, so you have to
            # split and iterate.

        paramId = asset["paramId"]
        
        if paramId == -1:
            # This is probably not useful. If paramId is -1, it most likely means it is an asset
            # that needs a tuple, and therefore needs to be handled explicitly like Redshift
            # proxies and shaders above. We'll have to add cases as they arise.
            paramId = asset["owner"].GetType()
        try:
            original_value = asset["owner"][paramId]
            if original_value and os.path.isabs(original_value):
                changes.append(
                    {
                        "owner": asset["owner"],
                        "paramId": paramId,
                        "original_value": original_value,
                        "new_value": relative_path(original_value, docpath),
                    }
                )
            continue

        except AttributeError:
            msg = "Couldn't determine the path for asset: '{}'".format(asset)
            logger.exception(msg)
            # This probably means the paramId is invalid. Cant get the filename for this texture. If it
            # was relative, then it doesn't matter anyway.

        changes.append({"owner": asset["owner"]})

    render_data = doc.GetActiveRenderData()
    for paramId in [c4d.RDATA_PATH, c4d.RDATA_MULTIPASS_FILENAME]:
        original_value = render_data[paramId]
        if original_value and os.path.isabs(original_value):
            changes.append(
                {
                    "owner": render_data,
                    "paramId": paramId,
                    "original_value": original_value,
                    "new_value": relative_path(original_value, docpath),
                }
            )

    # Now change all the paths
    if not dry_run:
        for change in changes:
            if change.get("paramId") is None:
                logger.warning(
                    "Can't adjust path for object: '{}' for Linux. Check to make sure the path is relative to the c4d doc for this object".format(change["owner"])
                )
                continue
            change["owner"][change["paramId"]] = change["new_value"]
            logger.debug(
                "Changed: '{}' to '{}'.".format(change["original_value"], change["new_value"])
            )
        c4d.EventAdd()  # not sure if needed
    try:
        yield changes
    finally:
        if not dry_run:
            # Restore the original paths
            for change in changes:
                if change.get("paramId") is None:
                    continue
                change["owner"][change["paramId"]] = change["original_value"]
                logger.debug(
                    "Restored: '{}' to '{}'.".format(change["new_value"], change["original_value"])
                )
            c4d.EventAdd()


def asset_state():
    """
    Check path state of assets.

    ASSETS_POSIX: We are not on Windows (scene will work on Linux.)
    ASSETS_RELATIVE: We are on Windows but all paths are relative (Likely fully portable scene.)
    ASSETS_SAME_DRIVE: We are on Windows some paths are absolute but on the same drivve as the c4d scene.
    ASSETS_DIFFERENT_DRIVE: We are on Windows some paths are on different drives to the c4d scene.
    """

    if not sys.platform == "win32":
        return k.ASSETS_POSIX

    doc = c4d.documents.GetActiveDocument()
    docpath = Path(doc.GetDocumentPath())
    doc_drive_letter = docpath.drive_letter
    if not doc_drive_letter:
        raise ValueError("Invalid Windows document path: '{}'.".format(docpath.fslash()))

    # assets
    all_paths = [asset["assetname"] for asset in asset_cache.data()]
    # + outputs
    render_data = doc.GetActiveRenderData()
    all_paths += [
        get_resolved_image_path(render_data, paramId)
        for paramId in [c4d.RDATA_PATH, c4d.RDATA_MULTIPASS_FILENAME]
    ]
    all_paths = [Path(a) for a in all_paths if a]

    result = k.ASSETS_RELATIVE
    for path in all_paths:
        if path.absolute:
            result = k.ASSETS_SAME_DRIVE
            if path.drive_letter != doc_drive_letter:
                return k.ASSETS_DIFFERENT_DRIVE
    return result

def windows_paths():
    """
    Return list of Windows compatible 
    asset and rendered output paths.

    Returns:
        (dict) Dictionary of encountered Windows paths
    """
    doc = c4d.documents.GetActiveDocument()
    docpath = Path(doc.GetDocumentPath())

    all_paths = {}
    # assets
    all_paths['assets'] = [asset["assetname"] for asset in asset_cache.data()]
    # + outputs
    render_data = doc.GetActiveRenderData()
    all_paths['outputs'] = get_image_paths(convert_tokens=False)

    windows_paths = {}
    for path_type, path_list in all_paths.items():
        w_paths = []
        for p in path_list:
            if p and c4d_drive_letter(p):
                w_paths.append(p)
        windows_paths[path_type] = w_paths
    
    return windows_paths

def c4d_drive_letter(path):
    """
    Checks path for a drive letter. C4D converts Windows
    file paths to /some/path/C:/original/path when a file
    with Windows paths is opened on a posix machine.

    Ex. path="/mac/path/C:/Imported/Windows/File/"
    returns: True

    Ex. path="/mac/path"
    returns: False

    Ex. path="C:\Windows\Path"
    returns: True
    """
    REGEX_DRIVE = re.compile(r"(.*\\|.*\/|^)[a-zA-Z]:")

    return bool(REGEX_DRIVE.match(path))
    
    
