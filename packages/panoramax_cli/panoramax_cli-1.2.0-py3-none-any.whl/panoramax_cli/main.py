import typer
from typing_extensions import Annotated
from pathlib import Path
from geopic_tag_reader.sequence import SortMethod, MergeParams, SplitParams
from panoramax_cli import (
    exception,
    model,
    auth,
    utils,
    __version__,
    upload as gvs_upload,
    status,
    download as gvs_download,
    transfer as gvs_transfer,
)
from rich.panel import Panel
from rich.console import Console
from typing import Optional, List

import panoramax_cli.http


console = Console()
print = console.print
app = typer.Typer()


def version_callback(value: bool):
    if value:
        print(f"Panoramax command-line client (v{__version__})", highlight=False)
        utils.check_if_lastest_version()
        raise typer.Exit()


@app.callback(help=f"Panoramax command-line client (v{__version__})")
def common(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            callback=version_callback,
            is_eager=True,
            help="Show Panoramax command-line client version and exit",
        ),
    ] = None,
):
    pass


@app.command()
def upload(
    path: Path = typer.Argument(..., help="Local path to your sequence folder"),
    api_url: str = typer.Option(..., help="Panoramax endpoint URL"),
    user: str = typer.Option(
        default=None,
        hidden=True,
        help="""DEPRECATED: Panoramax user name if the panoramax instance needs it. If none is provided and the panoramax instance requires it, the username will be asked during run.""",
        envvar="GEOVISIO_USER",
    ),
    password: str = typer.Option(
        default=None,
        hidden=True,
        help="""DEPRECATED: Panoramax password if the panoramax instance needs it. If none is provided and the panoramax instance requires it, the password will be asked during run. Note: it is advised to wait for prompt without using this variable.""",
        envvar="GEOVISIO_PASSWORD",
    ),
    wait: bool = typer.Option(default=False, help="Wait for all pictures to be ready"),
    isBlurred: bool = typer.Option(
        False,
        "--is-blurred/--is-not-blurred",
        help="Define if sequence is already blurred or not",
    ),
    title: Optional[str] = typer.Option(
        default=None,
        help="Collection title. If not provided, the title will be the directory name.",
    ),
    token: Optional[str] = typer.Option(
        default=None,
        help="""Panoramax token if the panoramax instance needs it. If none is provided and the panoramax instance requires it, the token will be asked during run. Note: is is advised to wait for prompt without using this variable.""",
    ),
    sort_method: Optional[SortMethod] = typer.Option(
        default="time-asc",
        help="Strategy used for sorting your pictures. Either by filename or EXIF time, in ascending or descending order.",
    ),
    split_distance: Optional[int] = typer.Option(
        default=None,
        help="Maximum distance between two pictures to be considered in the same sequence (in meters). If not provided, the instance's default value will be used. Splitting can be disabled entirely with --no-split.",
    ),
    split_time: Optional[int] = typer.Option(
        default=None,
        help="Maximum time interval between two pictures to be considered in the same sequence (in seconds). If not provided, the instance's default value will be used. Splitting can be disabled entirely with --no-split.",
    ),
    no_split: bool = typer.Option(
        False,
        "--no-split/--split",
        help="If True, all pictures of this upload will be grouped in the same sequence. Is incompatible with split_distance / split_time.",
    ),
    duplicate_distance: Optional[float] = typer.Option(
        default=None,
        help="Maximum distance between two pictures to be considered as duplicates (in meters). If not provided, the instance's default value will be used. Deduplication can be disabled entirely with --no-deduplication.",
    ),
    duplicate_rotation: Optional[int] = typer.Option(
        default=None,
        help="Maximum angle of rotation for two too-close-pictures to be considered as duplicates (in degrees). If not provided, the instance's default value will be used. Deduplication can be disabled entirely with --no-deduplication.",
    ),
    no_deduplication: bool = typer.Option(
        False,
        "--no-deduplication/--deduplication",
        help="If True, no duplication will be done. Is incompatible with duplicate_distance / duplicate_rotation.",
    ),
    relative_heading: Optional[int] = typer.Option(
        default=None,
        help="The relative heading (in degrees), offset based on movement path (0° = looking forward, -90° = looking left, 90° = looking right). For single picture upload_sets, 0° is heading north). For example, use 90° if the camera was mounted on the vehicle facing right. If not set, the headings are either retreived using the pictures metadata or computed using the movement path if no metadata is set.",
    ),
    picture_upload_timeout: float = typer.Option(
        default=60.0,
        help="Timeout time to receive the first byte of the response for each picture upload (in seconds)",
    ),
    parallel_uploads: Optional[int] = typer.Option(default=1, help="Amount of pictures to send in parallel"),
    merge_subfolders: Annotated[
        bool,
        typer.Option(
            "--merge-subfolders/--separate-subfolders",
            help="Should subfolders be considered as independent sequences, or sent as a single upload set ?",
        ),
    ] = False,
    disable_duplicates_check: Annotated[
        bool,
        typer.Option(
            "--disable-duplicates-check/--enable-duplicates-check",
            help="""Disable locally checking for pictures duplicates (almost same time and coordinates).
Disabling this avoids long local processing (duplicates are checked on server-side), enabling avoids sending useless pictures to server.
Choose depending on if your Internet is faster than your hard drive.""",
        ),
    ] = False,
    disable_cert_check: Annotated[
        bool,
        typer.Option(
            "--disable-cert-check/--enable-cert-check",
            help="Disable SSL certificates checks while uploading. This should not be used unless you __really__ know what you are doing.",
        ),
    ] = False,
):
    """Uploads some files.

    Upload some files to a Panoramax instance. The files will be associated to one or many sequences.
    """

    def cmd():
        if user or password:
            raise exception.CliException("user/password authentication have been deprecated, use a token or `panoramax login` instead")
        panoramax = model.Panoramax(url=api_url, token=token)
        if no_deduplication and (duplicate_distance is not None or duplicate_rotation is not None):
            raise exception.CliException(
                "⛔ Deduplication (removing capture duplicates like when stopped at a traffic light) has been deactivated with --no-deduplication, therefore you cannot provide deduplication parameters (neither --duplicate-distance nor --duplicate-rotation)"
            )
        if no_split and (split_distance is not None or split_time is not None):
            raise exception.CliException(
                "⛔ Spliting in sequences has been deactivated with --no-split, therefore you cannot provide split parameters (neither --split-distance nor --split-time)"
            )
        uploadParameters = model.UploadParameters(
            SortMethod(sort_method),
            SplitParams(split_distance, split_time) if not no_split else None,
            (MergeParams(duplicate_distance, duplicate_rotation) if not no_deduplication else None),
            isBlurred,
            relative_heading=relative_heading,
        )
        gvs_upload.upload_path(
            path,
            panoramax,
            title,
            picture_upload_timeout,
            wait,
            uploadParameters,
            disable_cert_check,
            parallel_uploads,
            disable_duplicates_check,
            merge_subfolders,
        )

    _run_command(cmd, "upload pictures", path)


@app.command()
def check_sequences(
    path: Path = typer.Argument(..., help="Local path to your sequence folder"),
    report_file: Optional[Path] = typer.Option(
        default=None,
        help="Output JSON file to save report result. No JSON saved by default.",
    ),
    geojson_dir: Optional[Path] = typer.Option(
        default=None,
        help="""Output GeoJSON in a given directory. Each sequence is a GeoJSON file with all its pictures. 
        The duplicates are also outputed in a special duplicates.geojson file. No GeoJSON saved by default.""",
    ),
    sort_method: Optional[SortMethod] = typer.Option(
        default="time-asc",
        help="Strategy used for sorting your pictures. Either by filename or EXIF time, in ascending or descending order.",
    ),
    split_distance: Optional[int] = typer.Option(
        default=100,
        help="Maximum distance between two pictures to be considered in the same sequence (in meters).",
    ),
    split_time: Optional[int] = typer.Option(
        default=5 * 60,
        help="Maximum time interval between two pictures to be considered in the same sequence (in seconds).",
    ),
    no_split: bool = typer.Option(
        False,
        "--no-split/--split",
        help="If True, all pictures of this upload will be grouped in the same sequence. Is incompatible with split_distance / split_time.",
    ),
    duplicate_distance: Optional[float] = typer.Option(
        default=1,
        help="Maximum distance between two pictures to be considered as duplicates (in meters).",
    ),
    duplicate_rotation: Optional[int] = typer.Option(
        default=60,
        help="Maximum angle of rotation for two too-close-pictures to be considered as duplicates (in degrees).",
    ),
    no_deduplication: bool = typer.Option(
        False,
        "--no-deduplication/--deduplication",
        help="If True, no duplication will be done. Is incompatible with duplicate_distance / duplicate_rotation.",
    ),
    merge_subfolders: Annotated[
        bool,
        typer.Option(
            "--merge-subfolders/--separate-subfolders",
            help="Should subfolders be considered as independent sequences, or sent as a single upload set ?",
        ),
    ] = False,
):
    """
    Checks pictures and sequences.
    This simulates processing done by the server to reflect sequences splits,
    find pictures duplicates and missing metadata.
    This runs in local, nothing is sent to the server.
    """

    def cmd():
        if no_deduplication and (duplicate_distance is not None or duplicate_rotation is not None):
            raise exception.CliException(
                "⛔ Deduplication (removing capture duplicates like when stopped at a traffic light) has been deactivated with --no-deduplication, therefore you cannot provide deduplication parameters (neither --duplicate-distance nor --duplicate-rotation)"
            )
        if no_split and (split_distance is not None or split_time is not None):
            raise exception.CliException(
                "⛔ Spliting in sequences has been deactivated with --no-split, therefore you cannot provide split parameters (neither --split-distance nor --split-time)"
            )
        uploadParams = model.UploadParameters(
            SortMethod(sort_method),
            SplitParams(split_distance, split_time) if not no_split else None,
            (MergeParams(duplicate_distance, duplicate_rotation) if not no_deduplication else None),
        )
        gvs_upload.local_checks(
            path,
            uploadParams,
            merge_subfolders,
            report_file,
            geojson_dir=geojson_dir,
        )

    _run_command(cmd, "check sequences", path)


@app.command()
def download(
    api_url: str = typer.Option(..., help="Panoramax endpoint URL"),
    collection: Optional[str] = typer.Option(
        default=None,
        help="Collection ID. Either use --collection or --user depending on your needs.",
    ),
    user: Optional[str] = typer.Option(
        default=None,
        help="User ID, to get all collections from this user. Either use --collection or --user depending on your needs. The special value 'me' can be provided to get you own sequences, if you're logged in.",
    ),
    path: Path = typer.Option(default=Path("."), help="Folder where to store downloaded collections."),
    picture_download_timeout: float = typer.Option(
        default=60.0,
        help="Timeout time to receive the first byte of the response for each picture upload (in seconds)",
    ),
    disable_cert_check: Annotated[
        bool,
        typer.Option(
            "--disable-cert-check/--enable-cert-check",
            help="Disable SSL certificates checks while downloading. This should not be used unless you __really__ know what you are doing.",
        ),
    ] = False,
    file_name: model.FileName = typer.Option(
        default=model.FileName.original_name,
        help="Strategy used for naming your downloaded pictures. Either by 'original-name' (by default) or by 'id' in Panoramax server.",
    ),
    token: Optional[str] = typer.Option(
        default=None,
        help="""Panoramax token if the panoramax instance needs it. If none is provided and the panoramax instance requires it, the token will be asked during run. Note: is is advised to wait for prompt without using this variable.""",
    ),
    external_metadata_dir_name: Optional[Path] = typer.Option(
        default=None,
        help="""Name of the folder where to store Panoramax API responses corresponding to each picture. 
This folder will be created in the pictures folder (so you can use '.' to download pictures in the same folder as the pictures).
If not provided, the API responses will not be persisted.""",
    ),
    quality: Optional[gvs_download.Quality] = typer.Option(
        default=gvs_download.Quality.hd.value,
        help="Quality of the pictures to download. Choosing a lower quality will reduce the download time.",
    ),
):
    """Downloads one or many sequences."""

    def cmd():
        panoramax = model.Panoramax(url=api_url, token=token)

        gvs_download.download(
            panoramax,
            user=user,
            collection=collection,
            disable_cert_check=disable_cert_check,
            path=path,
            file_name=file_name,
            picture_dl_timeout=picture_download_timeout,
            external_metadata_dir_name=external_metadata_dir_name,
            quality=quality,
        )

    _run_command(cmd, "downloading pictures", None)


@app.command()
def transfer(
    from_api_url: str = typer.Option(..., help="Origin Panoramax endpoint URL"),
    from_collection: Optional[str] = typer.Option(
        default=None,
        help="Collection ID to transfer. Either use --from-collection or --from-user depending on your needs.",
    ),
    from_user: Optional[str] = typer.Option(
        default=None,
        help="User ID (technical ID, not user name), to transfer all collections from this user. Either use --from-collection or --from-user depending on your needs. The special value 'me' can be provided to get you own sequences, if you're logged in.",
    ),
    from_token: Optional[str] = typer.Option(
        default=None,
        help="""Token on origin Panoramax instance if required. If none is provided and the panoramax instance requires it, the token will be asked during run. Note: is is advised to wait for prompt without using this variable.""",
    ),
    to_api_url: str = typer.Option(..., help="Destination Panoramax endpoint URL"),
    to_token: Optional[str] = typer.Option(
        default=None,
        help="""Token on destination Panoramax instance if required. If none is provided and the panoramax instance requires it, the token will be asked during run. Note: is is advised to wait for prompt without using this variable.""",
    ),
    picture_request_timeout: float = typer.Option(
        default=60.0,
        help="Timeout for getting the first byte of the response for each picture upload/download (in seconds)",
    ),
    parallel_transfers: Optional[int] = typer.Option(default=1, help="Amount of pictures to transfer in parallel"),
    disable_cert_check: Annotated[
        bool,
        typer.Option(
            "--disable-cert-check/--enable-cert-check",
            help="Disable SSL certificates checks while downloading. This should not be used unless you __really__ know what you are doing.",
        ),
    ] = False,
):
    """
    Transfer one or many sequences.
    This command copy sequences from origin API to destination API.
    Note that it doesn't delete sequences on origin API.
    """

    def cmd():
        from_api = model.Panoramax(url=from_api_url, token=from_token)
        to_api = model.Panoramax(url=to_api_url, token=to_token)

        gvs_transfer.transfer(
            from_api,
            to_api,
            from_user=from_user,
            from_collection=from_collection,
            disable_cert_check=disable_cert_check,
            picture_request_timeout=picture_request_timeout,
            parallel_transfers=parallel_transfers,
        )

    _run_command(cmd, "transfering pictures", None)


@app.command()
def upload_status(
    ids: List[str] = typer.Argument(help="One or many Upload Set IDs"),
    api_url: str = typer.Option(default=None, help="Panoramax endpoint URL"),
    token: Optional[str] = typer.Option(
        default=None,
        help="""Panoramax token if the panoramax instance needs it. If none is provided and the panoramax instance requires it, the token will be asked during run. Note: is is advised to wait for prompt without using this variable.""",
    ),
    wait: bool = typer.Option(default=False, help="Wait for all pictures to be ready"),
    disable_cert_check: Annotated[
        bool,
        typer.Option(
            "--disable-cert-check/--enable-cert-check",
            help="Disable SSL certificates checks while uploading. This should not be used unless you __really__ know what you are doing.",
        ),
    ] = False,
):
    """
    Status of one or many Upload Sets.
    """

    def cmd():
        panoramax = model.Panoramax(url=api_url, token=token)
        uploadSets = [model.UploadSet(id=id) for id in ids]

        with panoramax_cli.http.createClientWithRetry(disable_cert_check) as c:
            status.display_upload_sets_statuses(panoramax, c, uploadSets)

            # Only call wait if one of sets is not ready (to avoid useless prints)
            if wait:
                status.wait_for_upload_sets(panoramax, c, uploadSets)

    _run_command(cmd, "getting upload status")


@app.command(
    help=f"""
    Authenticate to the given instance.

    This will generate credentials and ask the user to visit a page to associate those credentials to the user's account.

    The credentials will be stored in {auth.get_config_file_path()}
    """
)
def login(
    api_url: str = typer.Option(..., help="Panoramax endpoint URL"),
    disable_cert_check: Annotated[
        bool,
        typer.Option(
            "--disable-cert-check/--enable-cert-check",
            help="Disable SSL certificates checks while uploading. This should not be used unless you __really__ know what you are doing.",
        ),
    ] = False,
):
    return _run_command(
        lambda: auth.create_auth_credentials(model.Panoramax(url=api_url), disable_cert_check),
        "authenticating",
    )


def _run_command(command, command_name_for_error, path: Optional[Path] = None):
    try:
        utils.check_if_lastest_version()
        command()
    except exception.CliException as e:
        print(
            Panel(
                f"{e}",
                title=f"Error while {command_name_for_error}" + (f" ({str(path.resolve())})" if path is not None else ""),
                style="traceback.error",
                border_style="traceback.border",
            )
        )
        return 1
    except Exception as e:
        import datetime

        trace_file = f"trace_panoramax_cli_{datetime.datetime.now().strftime('%Y%m%d-%H_%M_%S')}.txt"
        print(
            Panel(
                f"{e}",
                title=f"Error while {command_name_for_error}" + (f" ({str(path.resolve())})" if path is not None else ""),
                style="traceback.error",
                border_style="traceback.border",
            )
        )
        print(f"ℹ️ You can find more details in the file {trace_file}")
        _print_stack_trace(e, trace_file)

        return 1


def _print_stack_trace(e, file_name):
    try:
        import traceback

        with open(file_name, "w") as f:
            traceback.print_exception(e, file=f, value=e, tb=e.__traceback__)
    except Exception as other_exception:
        print(
            f"An error occur while saving the stack trace to {file_name}: {str(other_exception)}",
            style="traceback.error",
        )
        raise e  # raise initial exception if we did not manage to print the trace
