from datetime import timedelta
from time import sleep
from typing import Optional, List
from rich import print
from rich.console import Group
from rich.live import Live
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table
from panoramax_cli.http import Client
from panoramax_cli.utils import REQUESTS_TIMEOUT_STATUS, REQUESTS_TIMEOUT
from panoramax_cli.exception import CliException
from panoramax_cli.model import (
    AggregatedUploadSetStatus,
    Panoramax,
    Collection,
    UploadFileStatus,
    UploadSet,
    UploadFile,
    UploadParameters,
)
from geopic_tag_reader.sequence import MergeParams, SplitParams, SortMethod
import os
from pathlib import Path


def get_uploadset_files(panoramax: Panoramax, client: Client, uploadSet: UploadSet) -> UploadSet:
    if uploadSet.id is None:
        raise CliException("Upload Set has no ID defined")

    s = client.get(
        f"{panoramax.url}/api/upload_sets/{uploadSet.id}/files",
        timeout=REQUESTS_TIMEOUT_STATUS,
    )

    if s.status_code == 404:
        raise CliException(f"Upload Set {uploadSet.id} not found")
    if s.status_code >= 400:
        raise CliException(f"Impossible to get Upload Set {uploadSet.id} files: {s.text}")

    r = s.json()

    # Add info from files already uploaded to existing local list of files
    for f in r["files"]:
        uf = next(
            (uf for uf in uploadSet.files if uf.path is not None and uf.path.name == f.get("file_name")),
            None,
        )
        status = UploadFileStatus.synchronized if "rejected" not in f else UploadFileStatus.rejected
        if uf:
            uf.picture_id = f.get("picture_id")
            uf.status = status
            uf.content_md5 = f["content_md5"]
        else:
            uploadSet.files.append(
                UploadFile(
                    picture_id=f.get("picture_id"),
                    status=status,
                    content_md5=f["content_md5"],
                    path=Path(os.path.join(uploadSet.path or "", f["file_name"])),
                )
            )

    return uploadSet


def info(panoramax: Panoramax, client: Client, uploadSet: UploadSet) -> UploadSet:
    if not uploadSet.id:
        raise CliException("Upload Set has no ID defined")

    url = f"{panoramax.url}/api/upload_sets/{uploadSet.id}"
    s = client.get(url, timeout=REQUESTS_TIMEOUT)
    if s.status_code == 404:
        raise CliException(f"Upload Set {uploadSet.id} not found")
    if s.status_code >= 400:
        raise CliException(f"Impossible to get Upload Set {uploadSet.id} info: {s.text}")
    r = s.json()

    uploadSet.completed = r.get("completed") or False
    uploadSet.dispatched = r.get("dispatched") or False
    uploadSet.ready = r.get("ready") or False
    uploadSet.title = r.get("title")
    uploadSet.parameters = UploadParameters(
        SortMethod(r["sort_method"].replace("_", "-")) if "sort_method" in r else None,
        SplitParams(r.get("split_distance"), r.get("split_time")),
        MergeParams(r.get("duplicate_distance"), r.get("duplicate_rotation")),
    )
    status = r.get("items_status")
    if status:
        uploadSet.status = AggregatedUploadSetStatus(
            prepared=status["prepared"],
            preparing=status["preparing"],
            broken=status["broken"],
            not_processed=status["not_processed"],
        )
    if r.get("associated_collections") is not None:
        uploadSet.associated_collections = [Collection(id=c["id"]) for c in r["associated_collections"]]

    return uploadSet


def _print_final_upload_sets_statuses(uploadSets: List[UploadSet]):
    nb_ready = sum([us.nb_prepared() for us in uploadSets])
    nb_broken = sum([us.nb_broken() for us in uploadSets])

    if nb_ready == 0:
        print("[repr.error]💥 No picture processed")
        return
    s = f"✅ {nb_ready} pictures processed"
    if nb_broken:
        s += f"([repr.error]{nb_broken}[/repr.error] cannot be processed)"
    print(s)


def wait_for_upload_sets(
    panoramax: Panoramax,
    client: Client,
    uploadSets: List[UploadSet],
    timeout: Optional[timedelta] = None,
):
    uploadSets = [info(panoramax, client, us) for us in uploadSets]

    # Are all sets ready ?
    if all((us.ready for us in uploadSets)):
        _print_final_upload_sets_statuses(uploadSets)
        return

    print("🔭 Waiting for pictures to be processed by the API")
    status_progress = Progress(
        TextColumn("{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        MofNCompleteColumn(),
        "•",
        TextColumn("{task.fields[processing]}"),
    )
    processing_task = status_progress.add_task(
        "[green]⏳ Processing ...",
        total=1,
        processing="",
    )
    progress_group = Group(
        status_progress,
    )
    waiting_time = timedelta(seconds=2)
    elapsed = timedelta(0)

    with Live(progress_group):
        while True:
            nb_preparing = sum([us.nb_preparing() for us in uploadSets])
            nb_waiting = sum([us.nb_not_processed() for us in uploadSets])
            nb_ready = sum([us.nb_prepared() for us in uploadSets])
            nb_files = sum([us.nb_not_ignored() for us in uploadSets])
            processing = f"{nb_preparing} picture(s) currently processed"
            status_progress.update(
                processing_task,
                total=nb_files,
                completed=nb_ready,
                processing=processing,
            )

            if nb_waiting + nb_preparing == 0:
                break

            elapsed += waiting_time
            if timeout is not None and elapsed > timeout:
                raise CliException(f"❌ Upload sets not ready after {elapsed}, stopping")

            sleep(waiting_time.total_seconds())
            uploadSets = [info(panoramax, client, us) for us in uploadSets]

    _print_final_upload_sets_statuses(uploadSets)


def display_upload_sets_statuses(panoramax: Panoramax, client: Client, uploadSets: List[UploadSet]):
    table = Table()
    table.add_column("Upload Set")
    table.add_column("Total")
    table.add_column("Ready", style="green")
    table.add_column("Waiting", style="magenta")
    table.add_column("Preparing", style="magenta")
    table.add_column("Broken", style="red")

    for us in uploadSets:
        us = info(panoramax, client, us)
        table.add_row(
            us.title or us.id,
            f"{us.status.total() if us.status else len(us.files)}",
            f"{us.nb_prepared()}",
            f"{us.nb_not_processed()}",
            f"{us.nb_preparing()}",
            f"{us.nb_broken()}",
        )

    print(table)
