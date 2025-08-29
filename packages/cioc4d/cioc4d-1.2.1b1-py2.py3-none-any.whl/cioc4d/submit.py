import c4d
import os
import sys
import json
import re
import datetime
import webbrowser
from contextlib import contextmanager
from ciocore import conductor_submit
from ciocore import config

import traceback
from ciocore.validator import Validator, ValidationError
from cioc4d.sections.assets_section import AssetsSection
from cioc4d import foot_grp
from cioc4d import asset_cache, validation
from cioc4d import const as k
from cioc4d import utils
from ciopath.gpath import Path


try:
    from urllib import parse
except ImportError:
    import urlparse as parse

SAVE_AS_DIALOG = 12218
FALLBACK_AUTOSAVE_NAME = "cio_renderfile.c4d"


@contextmanager
def save_render_file(filename, cleanup=True):
    """
    Do something after saving a file.
    """

    doc = c4d.documents.GetActiveDocument()
    originalname = doc.GetDocumentName()
    try:
        docpath = doc.GetDocumentPath()
        filepath = os.path.join(docpath, filename)
        doc.SetDocumentName(filename)
        c4d.documents.SaveDocument(
            doc,
            filepath,
            saveflags=c4d.SAVEDOCUMENTFLAGS_AUTOSAVE,
            format=c4d.FORMAT_C4DEXPORT,
        )
        yield

        if cleanup:
            try:
                os.remove(filepath)
            except OSError:
                c4d.WriteConsole("Couldn't cleanup file: {}\n".format(filepath))
    except BaseException:
        c4d.WriteConsole("Submission failed.\n")
        raise
    finally:
        doc.SetDocumentName(originalname)


def valid(dialog):
    """Make sure the scene is valid for submission."""
    results = {"success": True, "dialog_msg": None}
    try:
        result = validation.run(dialog)
        results["dialog_msg"] = result
    except ValidationError as ex:
        c4d.WriteConsole(str(ex))
        c4d.WriteConsole("\n")
        results["success"] = False
    return results

def submit(dialog):
    """Submit the scene.

    We may have to make some adjustments to the scene to make it work on Conductor. If we are on a
    Mac, we can submit the scene as-is. If we are on Windows, we need to make the paths posix
    compliant (In most cases relative.) The contextmanager: posix_filepaths() takes care of this and
    restores the project to it's original state afterwards.

    Before we make the scene posix compatible, we make a fresh cache of current asset scrape.
    """
    document = c4d.documents.GetActiveDocument()
    if not document.GetDocumentPath():
        c4d.gui.MessageDialog(
            "Can't determine document path. Please save the scene and try again.\n",
            type=c4d.GEMB_OK,
        )
        return

    asset_cache.clear()
    asset_cache.data()

    validation = valid(dialog)
    if not validation["success"]:
        dialog.hide_progress_bar()
        return

    filepath, cleanup = _resolve_autosave_template(dialog)

    asset_state = utils.asset_state()
    # NOTE : We used to check if we are on Mac OR if there are no absolute paths to be adjusted.
    # However, the  k.ASSETS_RELATIVE state might not be accurate. The only way we can be sure
    # there's nothing to adjust, is if we are on a posix compliant system (ASSETS_POSIX).
    if asset_state == k.ASSETS_POSIX:
        with save_render_file(filepath, cleanup=cleanup):
            handle_submissions(dialog, validation["dialog_msg"])
        return

    with utils.posix_filepaths():
        with save_render_file(filepath, cleanup=cleanup):
            handle_submissions(dialog, validation["dialog_msg"])


def _resolve_autosave_template(dialog):
    """
    Generate a filename to save, and determine whether to cleanup after.

    Use c4d's own tokens to generate the name.
    We dont cleanup if upload daemon is on.
    """

    render_path_data = utils.rpd()
    try:
        resolved_name = c4d.modules.tokensystem.StringConvertTokens(
            "cio_$prj", render_path_data
        )
    except SystemError:
        c4d.WriteConsole(
            "Error resolving autosave template. Changing name to '{}'.\n".format(
                FALLBACK_AUTOSAVE_NAME
            )
        )
        resolved_name = FALLBACK_AUTOSAVE_NAME

    if not resolved_name.endswith(".c4d"):
        resolved_name = "{}.c4d".format(resolved_name)

    cleanup = not dialog.section("UploadOptionsSection").use_daemon_widget.get_value()

    return (resolved_name, cleanup)


def handle_submissions(dialog, dialog_msg=None):
    """Handle the submission and show the results.
    
    Update UI's progress bar before and after submission."""

    # Message forces timely UI refresh
    if not dialog_msg:
        dialog.show_progress_bar()
        attempt = c4d.gui.MessageDialog(
                "Your submission will begin momentarily. Press 'OK' to proceed.",
                type=c4d.GEMB_ICONASTERISK,
                )

    submission = dialog.calculate_submission(with_assets=True)
    response = do_submission(dialog, submission)

    dialog.progress_bar_grp.finish_progress()
    show_submission_response(dialog, response)
    dialog.hide_progress_bar()

def do_submission(dialog, submission):
    """Submit the scene to Conductor."""
    show_tracebacks = dialog.section("DiagnosticsSection").widget.get_value()

    try:
        remote_job = conductor_submit.Submit(submission)
        response, response_code = remote_job.main()
        return {"code": response_code, "response": response}
    except BaseException as ex:
        if show_tracebacks:
            msg = traceback.format_exc()
        else:
            msg = str(ex)
        c4d.WriteConsole("{}\n".format(msg))

        return {"code": "undefined", "response": msg}


def show_submission_response(dialog, response):
    """Show the results of the submission in a panel with a link to the job on the Conductor dashboard."""
    cfg = config.get()
    if response.get("code") <= 201:
        # success
        success_uri = response["response"]["uri"].replace("jobs", "job")
        job_url = parse.urljoin(cfg["auth_url"], success_uri)
        job_id = success_uri.split("/")[-1]

        c4d.WriteConsole("Submission result {}\n".format("*" * 30))
        c4d.WriteConsole(
            "Use this URL to monitor your Conductor job:\n{}\n".format(job_url)
        )

        downloader_message = (
            "If you plan on using the command-line downloader to retrieve\n"
        )
        downloader_message += (
            "your files when they are done, then paste the following\n"
        )
        downloader_message += "string into the command prompt:\n"
        c4d.WriteConsole(downloader_message)

        location = (dialog.section("LocationSection").widget.get_value() or "").strip()
        if location:
            c4d.WriteConsole(
                "\n'{}' downloader --location '{}' --job_id {}\n".format(
                    k.CONDUCTOR_COMMAND_PATH, location, job_id
                )
            )
        else:
            c4d.WriteConsole(
                '"{}" downloader --job_id {}\n'.format(k.CONDUCTOR_COMMAND_PATH, job_id)
            )

        result = c4d.gui.MessageDialog(
            "Success: Click 'OK' to monitor the job on the Conductor dashboard:\n\n{}\n\nPlease see the console for download instructions".format(
                job_url
            ),
            type=c4d.GEMB_OKCANCEL,
        )
        if result == c4d.GEMB_R_V_OK:
            webbrowser.open_new(job_url)

        return

    c4d.gui.MessageDialog("Failure: {}".format(str(response["response"])))
