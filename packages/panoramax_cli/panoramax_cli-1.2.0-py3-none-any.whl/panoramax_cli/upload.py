from typing import List, Optional, Union, Dict, Any, Callable
from concurrent.futures import Future
import signal
import sys
import json
from panoramax_cli.http import Client, createClientWithRetry
from panoramax_cli.model import (
    UploadFileStatus,
    UploadSet,
    UploadParameters,
    UploadFile,
    Panoramax,
    Picture,
)
from pathlib import Path
import os
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
import httpx
from rich import print
from rich.console import Group
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from panoramax_cli.utils import (
    REQUESTS_CNX_TIMEOUT,
    REQUESTS_TIMEOUT,
    test_panoramax_url,
)
from panoramax_cli.auth import login
from panoramax_cli.exception import CliException, raise_for_status
from panoramax_cli.metadata import find_handler
from panoramax_cli.status import wait_for_upload_sets, get_uploadset_files, info
from geopic_tag_reader import reader
from geopic_tag_reader.sequence import (
    dispatch_pictures,
    Picture as TRPicture,
    sort_pictures,
    find_duplicates,
)


@dataclass
class UploadError:
    file: UploadFile
    error: Union[str, dict]
    status_code: Optional[int]


@dataclass
class UploadReport:
    uploaded_files: List[UploadFile] = field(default_factory=lambda: [])
    skipped_files: List[UploadFile] = field(default_factory=lambda: [])
    errors: List[UploadError] = field(default_factory=lambda: [])
    upload_sets: List[UploadSet] = field(default_factory=lambda: [])


def path_to_upload_sets(path: Path, params: UploadParameters, mergeSubfolders: Optional[bool] = False) -> List[UploadSet]:
    """
    Analyzes a given folder to find how many upload sets should be created

    Parameters
    ----------
        path (Path) : pointer to path to read
        params (UploadParameters) : parameters retrieved from users to inject in UploadSets
        mergeSubfolders (bool) : make all subfolder part of same upload set

    Returns
    -------
        UploadSet[]
    """

    uploadSets: List[UploadSet] = []

    # Recursively run through path
    for cwd, subdirs, files in os.walk(path):
        filesPaths = [Path(f) for f in files]
        pictures = [f for f in filesPaths if f.suffix.lower() in [".jpg", ".jpeg"]]
        metadata_handler = find_handler(path)

        # Create an upload set only if pictures are available in current directory
        if len(pictures) > 0:
            if mergeSubfolders and len(uploadSets) > 0:
                uset = uploadSets[0]
            else:
                uset = UploadSet(
                    path=path if mergeSubfolders else Path(cwd),
                    files=[],
                    parameters=params,
                    metadata_handler=metadata_handler,
                )
                uset.load_id()
                uploadSets.append(uset)

            for p in pictures:
                filePath = os.path.join(cwd, p)
                ufile = UploadFile(path=Path(filePath))
                if metadata_handler is not None:
                    ufile.externalMetadata = metadata_handler.get(ufile.path)
                uset.files.append(ufile)

    return uploadSets


def create_upload_set(
    gvs: Panoramax,
    client: Client,
    uploadSet: UploadSet,
    estimated_nb_files: Optional[int] = None,
):
    # Create UploadSet
    if uploadSet.id is None:
        url = f"{gvs.url}/api/upload_sets"
        post_data: Dict[str, Any] = {
            "title": uploadSet.title,
            "estimated_nb_files": estimated_nb_files or len(uploadSet.files),
        }

        cli_config = {}
        if uploadSet.parameters is not None:
            # for the deduplication, we always tell the API not to do it as it has either already been done by the CLI or it has been deactivated
            post_data["no_deduplication"] = True
            # Note: for debug purpose, we still send the merge parameters as metadata
            if uploadSet.parameters.merge_params is not None:
                if uploadSet.parameters.merge_params.maxDistance is not None:
                    cli_config["duplicate_distance"] = uploadSet.parameters.merge_params.maxDistance

                if uploadSet.parameters.merge_params.maxRotationAngle is not None:
                    cli_config["duplicate_rotation"] = uploadSet.parameters.merge_params.maxRotationAngle
            else:
                cli_config["no_deduplication"] = True

            if uploadSet.parameters.split_params is not None:
                post_data["split_distance"] = uploadSet.parameters.split_params.maxDistance
                post_data["split_time"] = uploadSet.parameters.split_params.maxTime
            else:
                post_data["no_split"] = True
            if uploadSet.parameters.sort_method is not None:
                post_data["sort_method"] = uploadSet.parameters.sort_method
            if uploadSet.parameters.relative_heading is not None:
                post_data["relative_heading"] = uploadSet.parameters.relative_heading

        if cli_config:
            uploadSet.metadata["cli_configuration"] = cli_config
        if uploadSet.metadata:
            post_data["metadata"] = uploadSet.metadata

        post_response = client.post(url, json=post_data, timeout=REQUESTS_TIMEOUT)

        # Special message for 404/incompatible API
        if post_response.status_code == 404:
            raise CliException(
                "Panoramax API doesn't support Upload Set",
                """[bold red]API doesn't seem to support Upload Set 😰
You can either:
  - Try to use an older version of panoramax_cli called geovisio_cli
    [italic]pip install geovisio_cli==0.3.13[/italic]
  - If you are the API administrator or can contact them,
    make sure the API is running on latest version (>= 2.7)""",
            )

        raise_for_status(post_response, "Impossible to create Upload Set")
        uploadSet.id = post_response.json()["id"]
        uploadSet.persist()

    # Synchronize existing upload set
    else:
        info(gvs, client, uploadSet)
        print(f"🌐 Resume processing Upload Set: {uploadSet.id}")
        get_uploadset_files(gvs, client, uploadSet)


def send_upload_set_files(
    gvs: Panoramax,
    client: Client,
    report: UploadReport,
    uploadSet: UploadSet,
    onFileProcess: Callable[[UploadFile], None],
    onFileError: Callable[[UploadError], None],
    onAbort: Callable[[], None],
    uploadTimeout: float,
    max_workers: int = 1,
) -> None:
    if not uploadSet.files:
        return

    # Analyzing files status
    toProcess = []
    nbSkipped = 0
    for f in uploadSet.files:
        if f.status in [UploadFileStatus.synchronized, UploadFileStatus.ignored]:
            report.skipped_files.append(f)
            if f.status == UploadFileStatus.synchronized:
                nbSkipped += 1
        else:
            toProcess.append(f)

    if nbSkipped > 0:
        print(f"ℹ️ Skipped {nbSkipped} already sent picture(s)")
        if nbSkipped == len(uploadSet.files):
            return

    future_to_file: Dict[Future, UploadFile] = {}

    def shutdown_executor(executor):
        onAbort()
        for future in future_to_file.keys():
            future.cancel()
        executor.shutdown(wait=True)
        sys.exit()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        signal.signal(signal.SIGINT, lambda sig, frame: shutdown_executor(executor))

        try:
            future_to_file = {
                executor.submit(
                    upload_single_file,
                    gvs,
                    client,
                    uploadSet,
                    uploadFile,
                    uploadTimeout,
                ): uploadFile
                for uploadFile in toProcess
            }
            for future in as_completed(future_to_file):
                uploadFile = future_to_file[future]
                try:
                    response = future.result()
                    if response.status_code >= 200 and response.status_code < 300:
                        onFileProcess(uploadFile)
                        uploadFile.picture_id = response.json()["picture_id"]
                        report.uploaded_files.append(uploadFile)
                    else:
                        if response.status_code == 409:
                            report.skipped_files.append(uploadFile)
                        else:
                            errText = response.text
                            try:
                                rjson = response.json()
                                if rjson.get("message"):
                                    errText = rjson["message"]
                                if rjson.get("details") and rjson["details"].get("error"):
                                    errText += "\n" + rjson["details"]["error"]
                            except json.JSONDecodeError:
                                pass

                            onFileError(UploadError(uploadFile, errText, response.status_code))
                    response.close()
                except Exception as exc:
                    report.errors.append(UploadError(uploadFile, str(exc), None))
        except KeyboardInterrupt:
            shutdown_executor(executor)


def _read_picture_file(us: UploadSet, f: UploadFile) -> Picture:
    picture = Picture(path=f.path.name)
    if us.metadata_handler:
        picture.overridden_metadata = us.metadata_handler.get(f.path)

    try:
        with open(f.path, "rb") as img:
            meta = reader.readPictureMetadata(img.read())
            picture.metadata = meta
            return picture

    except reader.PartialExifException as e:
        # override picture metadata with the one found in the exif tags
        # if a tag is found in both exif and external metadata, the external ones are used
        picture.update_overriden_metadata(e.tags)
        if picture.has_mandatory_metadata():
            return picture
        else:
            raise reader.InvalidExifException(f"{str(os.path.relpath(f.path or Path('.'), us.path))} misses mandatory metadata\n" + str(e))

    except Exception as e:
        raise reader.InvalidExifException(f"{str(os.path.relpath(f.path or Path('.'), us.path))} has invalid metadata\n" + str(e))


def _get_overriden_metadata(uploadFile: UploadFile):
    """
    Convert the overriden metadata into panoramax API parameters
    """

    res: Dict[str, Any] = {}
    m = uploadFile.externalMetadata
    if m is None:
        return res

    if m.lon is not None:
        res["override_longitude"] = m.lon
    if m.lat is not None:
        res["override_latitude"] = m.lat
    if m.ts is not None:
        # date are send as iso 3339 formated datetime (like '2017-07-21T17:32:28Z')
        res["override_capture_time"] = m.ts.isoformat()
    if len(m.exif) > 0:
        for k in m.exif:
            res[f"override_{k}"] = m.exif[k]

    return res


def upload_single_file(
    gvs: Panoramax,
    client: Client,
    uploadSet: UploadSet,
    uploadFile: UploadFile,
    uploadTimeout: float,
):
    if uploadFile.path is None:
        raise CliException("Missing path for upload file")

    url = f"{gvs.url}/api/upload_sets/{uploadSet.id}/files"
    post_data = {
        "isBlurred": ("true" if uploadSet.parameters is not None and uploadSet.parameters.already_blurred is True else "false"),
    }
    post_data.update(_get_overriden_metadata(uploadFile))

    try:
        with open(uploadFile.path, "rb") as f:
            picture_response = client.post(
                url,
                files={"file": f},
                data=post_data,
                timeout=httpx.Timeout(connect=REQUESTS_CNX_TIMEOUT, read=uploadTimeout, write=30, pool=5),
            )
            return picture_response
    except httpx.TimeoutException as timeout_error:
        raise CliException(
            f"""Timeout while trying to post picture. Maybe the instance is overloaded? Please contact your instance administrator.

	[bold]Error:[/bold]
	{timeout_error}"""
        )
    except (httpx.HTTPError,) as cnx_error:
        raise CliException(
            f"""Impossible to reach Panoramax while trying to post a picture, connection was lost. Please contact your instance administrator.

	[bold]Error:[/bold]
	{cnx_error}"""
        )


def complete_upload_set(gvs: Panoramax, client: Client, uploadSet: UploadSet):
    """Close Upload Set on API"""

    if uploadSet.id is None:
        raise CliException("Can't complete Upload Set without ID")

    # Force retrieval of latest Upload Set status
    info(gvs, client, uploadSet)

    # Only call /complete if not already completed
    #   This make sure upload set is always dispatched on API side
    #   even if CLI messes up upload for some reason
    if not uploadSet.completed:
        url = f"{gvs.url}/api/upload_sets/{uploadSet.id}/complete"
        post_response = client.post(url, timeout=REQUESTS_TIMEOUT)
        raise_for_status(post_response, "Impossible to close Upload Set")


def _login_if_needed(client: Client, panoramax: Panoramax) -> bool:
    # Check if API needs login
    apiConf = client.get_instance_configuration(panoramax)
    if apiConf.get("auth", {}).get("enabled", False):
        logged_in = login(client, panoramax)
        if not logged_in:
            return False
    return True


def _print_folder_tree(uploadSets: List[UploadSet], path: Path) -> int:
    nbFiles = sum([len(us.files or []) for us in uploadSets])
    nbUs = len(uploadSets)
    if nbUs == 0:
        raise CliException("No pictures found in given folder")
    elif nbUs == 1:
        print(f"  - Found {nbFiles} files in given folder")
    else:
        print(f"  - Found {nbUs} subfolders")
        for us in uploadSets:
            usp = str(os.path.relpath(us.path or Path("."), path))
            if usp == ".":
                usp = "Main folder"
            print(f"    - {usp} : {len(us.files or [])} files")
    return nbFiles


def upload_path(
    path: Path,
    panoramax: Panoramax,
    title: Optional[str],
    uploadTimeout: float,
    wait: bool = False,
    uploadParameters: UploadParameters = UploadParameters(),
    disableCertCheck=False,
    parallelUploads: int = 1,
    disableDuplicatesCheck: bool = False,
    mergeSubfolders: bool = False,
) -> UploadReport:
    # early test that the given url is correct
    with createClientWithRetry(disableCertCheck) as c:
        test_panoramax_url(c, panoramax.url)

        # early test login
        if not _login_if_needed(c, panoramax):
            raise CliException(
                "🔁 Computer not authenticated yet, impossible to upload pictures, but you can try again the same upload command after finalizing the login"
            )

        uploadParameters.update_with_instance_defaults(c, panoramax)

        report = UploadReport()

        #####################################################
        # Read folder tree to find all pictures
        #

        print(f"🔍 Finding all pictures to upload in {path}")
        uploadSets = path_to_upload_sets(path, uploadParameters, mergeSubfolders)
        nbFiles = _print_folder_tree(uploadSets, path)
        print()  # For spacing

        # Titles
        for uploadSet in uploadSets:
            if title is not None:
                uploadSet.title = title
            elif uploadSet.path:
                uploadSet.title = str(uploadSet.path)

        # Duplicates
        if not disableDuplicatesCheck:
            dups_progress = Progress(
                TextColumn("{task.description}"),
                BarColumn(),
                TimeElapsedColumn(),
                TextColumn("[{task.completed}/{task.total}]"),
            )
            dups_task = dups_progress.add_task(
                "👀 Looking for duplicates...",
                total=nbFiles,
            )
            found_dups: Dict[str, int] = {}
            with Live(dups_progress):
                for uploadSet in uploadSets:
                    myPics: List[TRPicture] = []
                    for f in uploadSet.files:
                        try:
                            picture = _read_picture_file(uploadSet, f)
                            myPics.append(picture.toTRPicture())
                        except reader.InvalidExifException:
                            f.status = UploadFileStatus.ignored
                        dups_progress.advance(dups_task)

                    myPics = sort_pictures(myPics, uploadParameters.sort_method)
                    myPics, dupsPics = find_duplicates(myPics, uploadParameters.merge_params)
                    if len(dupsPics) > 0:
                        assert uploadSet.title is not None
                        found_dups[uploadSet.title] = len(dupsPics)

                        # Make corresponding upload files as ignored
                        for dp in dupsPics:
                            uf = next(
                                (uf for uf in uploadSet.files if uf.path == dp.picture.filename),
                                None,
                            )
                            if uf is not None:
                                uf.status = UploadFileStatus.ignored

            for ust, nb in found_dups.items():
                print(f'  - "{ust}": found {nb} duplicate picture(s)')

            print()  # Spacing

        #####################################################
        # Upload loop
        #

        uploading_progress = Progress(
            TextColumn("{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            TextColumn("[{task.completed}/{task.total}]"),
        )
        current_set_progress = Progress(
            TextColumn("📂 Processing folder [purple]{task.fields[title]}"),
            TextColumn("[{task.completed}/{task.total}]"),
        )
        current_pic_progress = Progress(
            TextColumn("  📷 Sending [bold purple]{task.fields[file]}"),
            SpinnerColumn("simpleDots"),
        )
        error_progress = Progress(TextColumn("{task.description}"))
        last_error = Progress(
            TextColumn("🔎 Last error 🔎\n{task.description}"),
        )
        error_panel = Panel(Group(error_progress, last_error), title="Errors")
        uploading_task = uploading_progress.add_task(
            "[green]🚀 Uploading pictures...",
            total=nbFiles,  # "Dumb" count as upload sets are not synced with API yet
        )
        current_set_task = current_set_progress.add_task("", completed=0, total=len(uploadSets), title="")
        current_pic_task = current_pic_progress.add_task("", file="")
        progress_group = Group(
            uploading_progress,
            current_set_progress,
            current_pic_progress,
            error_panel,
        )
        error_task = error_progress.add_task("[green]No errors")
        last_error_task = last_error.add_task("", visible=False)

        with Live(progress_group) as live_render:

            def onFileProcess(uf: UploadFile) -> None:
                uploading_progress.advance(uploading_task)
                if uf.path:
                    current_pic_progress.update(current_pic_task, file=uf.path.name)

            def onFileError(ue: UploadError) -> None:
                report.errors.append(ue)
                uploading_progress.advance(uploading_task)
                last_error.update(last_error_task, description=str(ue.error), visible=True)
                error_progress.update(
                    error_task,
                    description=f"[bold red]{len(report.errors)} errors",
                )

            def onAbort() -> None:
                live_render.stop()
                print("🛑 Stopping...")

            for uploadSet in uploadSets:
                current_set_progress.advance(current_set_task)
                current_set_progress.update(current_set_task, title=uploadSet.title)
                create_upload_set(panoramax, c, uploadSet)
                uploading_progress.update(uploading_task, total=sum([us.nb_not_sent() for us in uploadSets]))
                report.upload_sets.append(uploadSet)

                # Check if upload set still open
                send_upload_set_files(
                    panoramax,
                    c,
                    report,
                    uploadSet,
                    onFileProcess,
                    onFileError,
                    onAbort,
                    uploadTimeout,
                    parallelUploads,
                )

                # Mark UploadSet as complete (can be reopened later)
                try:
                    complete_upload_set(panoramax, c, uploadSet)
                except CliException:
                    print(f"⚠️ [repr.error]Upload Set {uploadSet.id} can't be marked as completed")

        print()  # Spacing

        #####################################################
        # Post-upload report
        #

        # Only failures
        manyErrors = False
        if len(report.errors) == nbFiles and nbFiles > 0:
            print(f'[repr.error]💥 All pictures upload in "{uploadSet.title}" failed! 💥[/repr.error]')
            firstMsg = str(report.errors[0].error)
            for e1 in report.errors[1:]:
                if firstMsg != str(e1.error):
                    manyErrors = True
                    break

            if not manyErrors:
                print(firstMsg)

        # Nothing done
        elif len(report.uploaded_files) == 0 and len(report.errors) == 0:
            print("🎉 [bold green]Everything already uploaded")

        # Uploads done
        else:
            print(f"🎉 [bold green]{len(report.uploaded_files)}[/bold green] pictures uploaded")

        # Pictures errors display
        if report.errors and manyErrors:
            print(f"[repr.error]{len(report.errors)}[/repr.error] pictures not uploaded:")
            for e2 in report.errors:
                msg = f" - {str(os.path.relpath(e2.file.path, path))}"
                if e2.status_code:
                    msg += f" (HTTP status {e2.status_code})"
                if isinstance(e2.error, str):
                    msg += "\n    " + e2.error.replace("\n", "\n    ")
                print(msg)

        # Wait or status command
        if report.uploaded_files:
            print()  # Spacing

            if wait:
                wait_for_upload_sets(panoramax, c, uploadSets)
            else:
                id_list = " ".join([us.id or "" for us in uploadSets]).strip()
                print("Note: You can follow the picture processing with the command:")
                print(f"  [bold]panoramax_cli upload-status --api-url {panoramax.url} --wait {id_list}")

        return report


def local_checks(
    path: Path,
    uploadParameters: Optional[UploadParameters] = UploadParameters(),
    mergeSubfolders: Optional[bool] = False,
    reportFile: Optional[Path] = None,
    geojson_dir: Optional[Path] = None,
):
    """Checks validity of UploadSet without upload"""

    print(f'🔍 Finding all pictures to check in "{path}"')
    uploadParameters = uploadParameters or UploadParameters()
    uploadSets = path_to_upload_sets(path, uploadParameters, mergeSubfolders)
    nbFiles = _print_folder_tree(uploadSets, path)
    allErrors: List[Union[str, str]] = []
    allWarnings: Dict[str, List[str]] = {}
    jsonReport: Dict[str, Any] = {
        "pictures_exif_issues": [],
        "pictures_duplicates": [],
        "folders": [],
    }
    feature_collections = []
    geojson_duplicates = []
    print()  # Spacing 🚀

    if next((us for us in uploadSets if us.id is not None), None) is not None:
        print("⚠️ [bold]Some upload sets already exists on server and could have different parameters")
        print()

    process_progress = Progress(
        TextColumn("{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        TextColumn("[{task.completed}/{task.total}]"),
    )
    current_set_progress = Progress(
        TextColumn("📂 Processing folder [purple]{task.fields[title]}"),
        TextColumn("[{task.completed}/{task.total}]"),
    )
    error_progress = Progress(TextColumn("{task.description}"))
    process_task = process_progress.add_task(
        "⚙️ Checking pictures...",
        total=nbFiles,
    )
    current_set_task = current_set_progress.add_task("", completed=0, total=len(uploadSets), title="")
    progress_group = Group(
        process_progress,
        current_set_progress,
        error_progress,
    )
    error_task = error_progress.add_task("[bold green]✅ All pictures have valid EXIF metadata !")

    usablePictures: Dict[str, Union[bool, List[Picture]]] = {}

    with Live(progress_group):

        def relPath(p):
            return str(os.path.relpath(p or Path("."), path))

        def onPicError(short, long):
            allErrors.append((short, long))
            error_progress.update(
                error_task,
                description=f"[bold red]🛑 {len(allErrors)} picture(s) with blocking metadata issues",
            )

        for uploadSet in uploadSets:
            current_set_progress.advance(current_set_task)
            relp = relPath(uploadSet.path)
            current_set_progress.update(current_set_task, title="Main folder" if relp == "." else relp)
            if uploadSet.id:
                usablePictures[relp] = False
                process_progress.advance(process_task, len(uploadSet.files))
            else:
                us_pics = []

                for f in uploadSet.files or []:
                    try:
                        picture = _read_picture_file(uploadSet, f)
                        us_pics.append(picture)
                        if picture.metadata is not None:
                            for w in picture.metadata.tagreader_warnings:
                                if picture.path is not None:
                                    if w not in allWarnings:
                                        allWarnings[w] = []
                                    allWarnings[w].append(Path(picture.path).stem)

                    except reader.InvalidExifException as e:
                        errorParts = str(e).split("\n", 1)
                        onPicError(*errorParts)
                        jsonReport["pictures_exif_issues"].append(
                            {
                                "path": str(f.path),
                                "issue": errorParts[-1],
                            }
                        )

                    process_progress.advance(process_task)
                usablePictures[relp] = us_pics

    if len(allErrors) > 0:
        for err in allErrors:
            print(f"  - [bold]{err[0]}")
            print(f"    {err[1]}")

    if len(allWarnings) > 0:
        print("")
        print("⚠️ [logging.level.warning]Some pictures have non-blocking issues that could reduce their usability:")
        for w, geojson_file_path in allWarnings.items():
            print(f"  - [bold]{w}")
            print(f"    Concerned pictures: {', '.join(geojson_file_path) if len(geojson_file_path) < nbFiles else 'all'}")

    # Display splits and duplicates
    print()
    print("✂️ [bold]Sequences splits:")
    for relp, pics in usablePictures.items():
        folderName = "Main folder" if relp == "." else f'Folder "{relp}"'
        jsonFolderReport: Dict[str, Any] = {
            "path": os.path.abspath(os.path.join(path, relp)),
        }

        if pics is False:
            print(f"  - {folderName}: [logging.level.warning]skipped because upload set already exists on server[/logging.level.warning]")
            jsonFolderReport["skipped"] = True
        else:
            assert pics is not True  # needed for the type checker
            report = dispatch_pictures(
                [p.toTRPicture() for p in pics],
                uploadParameters.sort_method,
                uploadParameters.merge_params,
                uploadParameters.split_params,
            )

            if len(report.sequences) > 1 or len(report.sequences[0].pictures) > 0:
                print(f"  - {folderName}: {len(report.sequences)} sequence(s)")
                jsonFolderReport["sequences"] = []
                jsonFolderReport["sequences_splits"] = []

                def printPart(i, s, split_reason=None):
                    jsonFolderReport["sequences"].append(
                        {
                            "pictures_nb": len(s.pictures),
                            "pictures_files": [p.filename for p in s.pictures],
                        }
                    )
                    feature_collections.append(
                        {
                            "type": "FeatureCollection",
                            "features": [pic_to_feature(p) for p in s.pictures],
                            "properties": {
                                "interval": [str(s.from_ts()), str(s.to_ts())],
                                **(split_reason or {}),
                            },
                        },
                    )
                    print(f"    - Part {i + 1}: {len(s.pictures)} picture(s) - {str(s.from_ts())} to {str(s.to_ts())}")

                printPart(0, report.sequences[0])
                for i, split in enumerate(report.sequences_splits or []):
                    prevSeq = report.sequences[i]
                    nextSeq = report.sequences[i + 1]
                    delta = prevSeq.delta_with(nextSeq)
                    if delta is None:
                        continue
                    timedelta, distdelta = delta

                    if split.reason == "time":
                        print(f"     ✂️🕓 Split due to excessive time ({round(timedelta.total_seconds())} seconds)")
                    else:
                        print(f"     ✂️📏 Split due to excessive distance ({round(distdelta)} meters)")
                    split_reason = {
                        "reason": split.reason.name,
                        "prev_picture_ts": split.prevPic.metadata.ts.isoformat(),
                        "prev_picture_latlon": [
                            split.prevPic.metadata.lat,
                            split.prevPic.metadata.lon,
                        ],
                        "next_picture_ts": split.nextPic.metadata.ts.isoformat(),
                        "next_picture_latlon": [
                            split.nextPic.metadata.lat,
                            split.nextPic.metadata.lon,
                        ],
                        "delta_seconds": timedelta.total_seconds(),
                        "delta_meters": round(distdelta),
                    }
                    printPart(i + 1, nextSeq, split_reason=split_reason)

                    jsonFolderReport["sequences_splits"].append(split_reason)

            else:
                jsonFolderReport["empty"] = True
                print(f"  - {folderName}: no valid pictures found")

            if report.duplicate_pictures:
                print()
                print("📏 [bold]Duplicate pictures:")
                print("  " + ", ".join([p.picture.filename for p in report.duplicate_pictures]))
                jsonReport["pictures_duplicates"] = [p.picture.filename for p in report.duplicate_pictures]
                geojson_duplicates.extend(
                    [
                        pic_to_feature(
                            TRPicture(filename=d.picture.filename, metadata=d.picture.metadata),
                            properties={
                                "duplicate_of": d.duplicate_of.filename,
                                "distance": d.distance,
                                "angle": d.angle,
                            },
                        )
                        for d in report.duplicate_pictures
                    ]
                )

        jsonReport["folders"].append(jsonFolderReport)

    # Export as JSON file
    if reportFile is not None:
        print()
        with reportFile.open("w", encoding="utf-8") as f2:
            json.dump(jsonReport, f2, ensure_ascii=False, indent=2)
            print(f'🗃️ Exported results as JSON in "{str(reportFile)}"')

    if geojson_dir:
        for i, f in enumerate(feature_collections):
            geojson_dir.mkdir(parents=True, exist_ok=True)
            geojson_file = geojson_dir / f"col_{i}.geojson"
            with geojson_file.open("w", encoding="utf-8") as file:
                json.dump(f, file, ensure_ascii=False, indent=2)
        if geojson_duplicates:
            with Path(geojson_dir / "duplicates.geojson").open("w", encoding="utf-8") as file:
                json.dump(
                    {
                        "type": "FeatureCollection",
                        "features": geojson_duplicates,
                        "properties": {
                            "is_duplicates": True,
                        },
                    },
                    file,
                    ensure_ascii=False,
                    indent=2,
                )
        print(f'🗺️🗃️ Exported results as GeoJSON in "{geojson_dir}"')


def pic_to_feature(p: TRPicture, properties: Dict[str, Any] = {}):
    if not p.metadata:
        print(f"impossible to transform picture {p.filename} to geojson")
        return {}
    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [p.metadata.lon, p.metadata.lat],
        },
        "properties": {
            "filename": p.filename,
            "ts": p.metadata.ts.isoformat(),
            "heading": p.metadata.heading,
            **properties,
        },
    }
