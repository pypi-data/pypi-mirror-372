import panoramax_cli.http
from panoramax_cli.model import Panoramax, UploadSet, UploadFile, UploadParameters
from pathlib import Path
from typing import Optional, List
from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
    wait,
    FIRST_COMPLETED,
)
import signal
import sys
import json
from tempfile import TemporaryDirectory
from panoramax_cli.auth import login
from panoramax_cli.exception import CliException
from panoramax_cli.http import Client
from panoramax_cli.download import (
    _get_collection_meta,
    _get_collection_items,
    _get_collection_location,
    Quality,
    PicToDownload,
    get_user_collections,
)
from panoramax_cli.upload import (
    create_upload_set,
    upload_single_file,
)
from panoramax_cli import utils
import os
from rich import print
from rich.live import Live
from rich.progress import (
    BarColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
)


def transfer_picture(
    from_api: Panoramax,
    to_api: Panoramax,
    pic: PicToDownload,
    uploadSet: UploadSet,
    from_client: Client,
    to_client: Client,
    picture_request_timeout: float,
    tmp_path: Path,
):
    picName = f"{pic.id}.jpg"
    picPath = tmp_path / picName

    # set auth headers only for panoramax instance. Important since the picture url might be an external url,
    # like a s3 link where we don't want to set panoramax auth headers.
    headers = {}
    if pic.download_url.startswith(from_api.url) and "Authorization" in from_client.headers:
        headers["Authorization"] = from_client.headers["Authorization"]

    # Download single picture
    res_pic_dl = from_client.get(
        url=pic.download_url,
        follow_redirects=True,
        timeout=picture_request_timeout,
        headers=headers,
    )
    if res_pic_dl.status_code >= 400:
        raise CliException(
            f"Impossible to download picture {pic.download_url}",
            details=res_pic_dl.text,
        )
    with picPath.open("wb") as picFile:
        picFile.writelines(res_pic_dl.iter_bytes())

    # Upload downloaded picture
    uploadFile = UploadFile(picPath)
    uploadRes = upload_single_file(to_api, to_client, uploadSet, uploadFile, uploadTimeout=picture_request_timeout)

    # Remove picture from filesystem
    os.unlink(picPath)

    # Process upload response
    if uploadRes.status_code >= 400 and uploadRes.status_code != 409:
        errText = uploadRes.text
        errDetails = None
        try:
            rjson = uploadRes.json()
            if rjson.get("message"):
                errText = rjson["message"]
            if rjson.get("details") and rjson["details"].get("error"):
                errDetails = rjson["details"]["error"]
        except json.JSONDecodeError:
            pass
        raise CliException(errText, errDetails)

    return True


def _pic_list_iter(from_api, from_collection, client):
    for pic in _get_collection_items(client, _get_collection_location(from_api, from_collection), Quality.hd):
        yield pic


def transfer_collection(
    from_collection: str,
    from_api: Panoramax,
    to_api: Panoramax,
    from_client: Client,
    to_client: Client,
    picture_request_timeout: float,
    parallel_transfers: int,
) -> str:
    print(f'📷 Retrieving collection "{from_collection}" metadata')
    coll_meta = _get_collection_meta(from_api, from_collection, from_client)
    nb_items = coll_meta["stats:items"]["count"]
    pic_generator = _pic_list_iter(from_api, from_collection, from_client)

    with TemporaryDirectory(prefix="gvs_") as tmp_dir_str:
        tmp_path = Path(tmp_dir_str)

        print("📦 Creating collection on destination API")
        uploadSet = UploadSet(
            title=coll_meta.get("title"),
            path=tmp_path,
            parameters=UploadParameters(already_blurred=True),
            metadata={
                "original:collection_id": from_collection,
                "original:instance": from_api.url,
            },
        )
        create_upload_set(to_api, to_client, uploadSet, nb_items)

        transfer_progress = Progress(
            TextColumn("{task.description}"),
            BarColumn(),
            TimeRemainingColumn(),
            TextColumn("[{task.completed}/{task.total}]"),
        )
        transfer_task = transfer_progress.add_task(
            "[green]🚀 Transferring pictures...",
            total=nb_items,
        )

        with (
            ThreadPoolExecutor(max_workers=parallel_transfers) as executor,
            Live(transfer_progress) as live_render,
        ):

            def shutdown_executor(executor, err=None):
                live_render.stop()
                if err:
                    print(f"❌ Something went wrong...\n{err}")
                else:
                    print("🛑 Stopping...")
                executor.shutdown(wait=True)
                sys.exit()

            signal.signal(signal.SIGINT, lambda sig, frame: shutdown_executor(executor))

            try:
                futures = set()
                for pic in pic_generator:
                    future = executor.submit(
                        transfer_picture,
                        from_api,
                        to_api,
                        pic,
                        uploadSet,
                        from_client,
                        to_client,
                        picture_request_timeout,
                        tmp_path,
                    )
                    futures.add(future)

                    # Wait for one task to end
                    if len(futures) >= parallel_transfers:
                        done, futures = wait(futures, return_when=FIRST_COMPLETED)
                        for future in done:
                            transfer_progress.advance(transfer_task)
                            future.result()

                # Wait for all other tasks to end
                for future in as_completed(futures):
                    transfer_progress.advance(transfer_task)
                    future.result()

            except KeyboardInterrupt:
                shutdown_executor(executor)
            except Exception as e:
                shutdown_executor(executor, e)

        print(f'🌠 Collection "{from_collection}" completely transferred')
        assert uploadSet.id is not None
        return uploadSet.id


def transfer_user(
    user: str,
    from_api: Panoramax,
    to_api: Panoramax,
    from_client: Client,
    to_client: Client,
    picture_request_timeout: float,
    parallel_transfers: int,
):
    usIds = []
    for coll_uuid in get_user_collections(from_client, from_api, user):
        print("")  # Spacing
        usId = transfer_collection(
            coll_uuid,
            from_api,
            to_api,
            from_client,
            to_client,
            picture_request_timeout,
            parallel_transfers,
        )
        usIds.append(usId)

    print("\n🌠 All collections transfered")
    return usIds


def transfer(
    from_api: Panoramax,
    to_api: Panoramax,
    from_user: Optional[str] = None,
    from_collection: Optional[str] = None,
    disable_cert_check: bool = False,
    picture_request_timeout: float = 60.0,
    parallel_transfers: int = 1,
) -> List[str]:
    if not (from_user or from_collection) or (from_user and from_collection):
        raise CliException("You must either provide a user ID or sequence ID")

    with (
        panoramax_cli.http.createClientWithRetry(disable_cert_check) as from_client,
        panoramax_cli.http.createClientWithRetry(disable_cert_check) as to_client,
    ):
        # Check both from/to APIs
        utils.test_panoramax_url(from_client, from_api.url)
        utils.test_panoramax_url(to_client, to_api.url)

        if from_user == "me":
            if not login(from_client, from_api):
                raise CliException(
                    "🔁 Computer not authenticated yet, impossible to transfer your pictures, but you can try again the same transfer command after finalizing the login"
                )

        if not login(to_client, to_api):
            raise CliException(
                "🔁 Computer not authenticated yet, impossible to transfer your pictures, but you can try again the same transfer command after finalizing the login"
            )

        if from_user:
            usIds = transfer_user(
                from_user,
                from_api,
                to_api,
                from_client=from_client,
                to_client=to_client,
                picture_request_timeout=picture_request_timeout,
                parallel_transfers=parallel_transfers,
            )
            return usIds
        else:
            assert from_collection
            usId = transfer_collection(
                from_collection,
                from_api,
                to_api,
                from_client=from_client,
                to_client=to_client,
                picture_request_timeout=picture_request_timeout,
                parallel_transfers=parallel_transfers,
            )
            return [usId]
