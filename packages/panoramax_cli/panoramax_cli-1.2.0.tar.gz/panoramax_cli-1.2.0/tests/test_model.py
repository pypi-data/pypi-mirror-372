import pytest
from tests.conftest import FIXTURE_DIR, MOCK_API_URL

import os
import datetime
from panoramax_cli.model import (
    UploadFile,
    UploadSet,
    Picture,
    AggregatedUploadSetStatus,
    UploadFileStatus,
    UploadParameters,
    MergeParams,
    SplitParams,
    SortMethod,
    Panoramax,
)
from panoramax_cli.http import createClientWithRetry
from geopic_tag_reader.reader import GeoPicTags, PartialGeoPicTags


@pytest.mark.parametrize(
    ("picture", "is_ok"),
    (
        (
            Picture(overridden_metadata=PartialGeoPicTags(lon=12.2, lat=43.4, ts=1516589529.9)),
            True,
        ),
        (
            Picture(overridden_metadata=PartialGeoPicTags(lon=12.2, lat=43.4)),
            False,
        ),
        (
            Picture(overridden_metadata=PartialGeoPicTags(lon=12.2, ts=1516589529.9)),
            False,
        ),
        (
            Picture(
                metadata=GeoPicTags(
                    lon=12.2,
                    lat=43.4,
                    ts=1516589529.9,
                    type="flat",
                    model=None,
                    crop=None,
                    focal_length=None,
                    heading=None,
                    make=None,
                ),
                overridden_metadata=PartialGeoPicTags(),
            ),
            True,
        ),
    ),
)
def test_Picture_has_mandatory_metadata(picture, is_ok):
    assert picture.has_mandatory_metadata() == is_ok


def test_Picture_update_overriden_metadata():
    pic = Picture(overridden_metadata=PartialGeoPicTags(lon=12.2, ts=12, make="CANON", type="flat"))

    pic.update_overriden_metadata(PartialGeoPicTags(lat=43.4, ts=4242, model="Some model", type="flat"))

    # after override, fields should not have been changed if set initially
    assert pic.overridden_metadata == PartialGeoPicTags(lon=12.2, lat=43.4, ts=12, make="CANON", model="Some model", type="flat")


def test_toTRPicture_no_path():
    pic = Picture(
        metadata=GeoPicTags(
            lat=10,
            lon=20,
            ts=datetime.datetime.now(),
            type="flat",
            model=None,
            crop=None,
            focal_length=None,
            heading=None,
            make=None,
        )
    )
    with pytest.raises(Exception, match="No file path defined"):
        pic.toTRPicture()


def test_toTRPicture_no_metadata():
    pic = Picture(path="test.jpg")
    with pytest.raises(Exception, match="No metadata available"):
        pic.toTRPicture()


def test_toTRPicture_with_metadata():
    pic = Picture(
        path="test.jpg",
        metadata=GeoPicTags(
            lat=10,
            lon=20,
            ts=1234,
            type="flat",
            model=None,
            crop=None,
            focal_length=None,
            heading=None,
            make=None,
        ),
    )
    tr_pic = pic.toTRPicture()
    assert tr_pic.filename == "test.jpg"
    assert tr_pic.metadata.lat == 10
    assert tr_pic.metadata.lon == 20
    assert tr_pic.metadata.ts == 1234


def test_toTRPicture_with_overridden_metadata():
    pic = Picture(
        path="test.jpg",
        metadata=GeoPicTags(
            lat=10,
            lon=20,
            ts=1234,
            type="flat",
            model=None,
            crop=None,
            focal_length=None,
            heading=None,
            make=None,
        ),
        overridden_metadata=PartialGeoPicTags(lat=15),
    )
    tr_pic = pic.toTRPicture()
    assert tr_pic.filename == "test.jpg"
    assert tr_pic.metadata.lat == 15
    assert tr_pic.metadata.lon == 20
    assert tr_pic.metadata.ts == 1234


def test_toTRPicture_only_overridden_metadata():
    pic = Picture(path="test.jpg", overridden_metadata=PartialGeoPicTags(lat=15, lon=25, ts=1234))
    tr_pic = pic.toTRPicture()
    assert tr_pic.filename == "test.jpg"
    assert tr_pic.metadata.lat == 15
    assert tr_pic.metadata.lon == 25
    assert tr_pic.metadata.ts == 1234


@pytest.mark.datafiles(os.path.join(FIXTURE_DIR, "e1.jpg"))
def test_UploadFile_compute_hash(datafiles):
    p = os.path.join(datafiles, "e1.jpg")
    uf = UploadFile(p)
    assert uf.content_md5 is None
    uf.compute_hash()
    assert uf.content_md5 == "880644ea05d7b387c2c9531d1a1fdcb8"


@pytest.mark.parametrize(
    ("prepared", "preparing", "broken", "not_processed", "expected"),
    (
        (1, 2, 3, 4, 10),
        (1, None, None, None, 1),
    ),
)
def test_AggregatedUploadSetStatus_total(prepared, preparing, broken, not_processed, expected):
    a = AggregatedUploadSetStatus(prepared, preparing, broken, not_processed)
    assert a.total() == expected


def test_UploadSet_load_id(tmp_path):
    # No ID + no path
    us = UploadSet()
    assert not us.load_id()
    assert us.id is None

    # Path + no file
    us = UploadSet(path=tmp_path)
    assert not us.load_id()
    assert us.id is None

    # Path + file
    us = UploadSet(path=tmp_path)
    with open(os.path.join(tmp_path, "_panoramax.txt"), "w") as f:
        f.write("upload_set_id=blablabla")
    assert us.load_id()
    assert us.id == "blablabla"

    # Path + file (empty)
    us = UploadSet(path=tmp_path)
    with open(os.path.join(tmp_path, "_panoramax.txt"), "w") as f:
        f.write("")
    assert not us.load_id()
    assert us.id is None

    # No path + ID already set
    us = UploadSet(id="blabla")
    assert us.load_id()
    assert us.id == "blabla"


def test_UploadSet_persist(tmp_path):
    us = UploadSet(id="blablabla", path=tmp_path)
    us.persist()
    with open(os.path.join(tmp_path, "_panoramax.txt")) as f:
        assert f.read() == "upload_set_id=blablabla"


def test_UploadSet_nb_prepared():
    status = AggregatedUploadSetStatus(prepared=5, preparing=None, broken=None, not_processed=None)
    us1 = UploadSet(status=status)
    assert us1.nb_prepared() == 5
    us2 = UploadSet()
    assert us2.nb_prepared() == 0


def test_UploadSet_nb_not_processed():
    status = AggregatedUploadSetStatus(prepared=0, preparing=None, broken=None, not_processed=3)
    us1 = UploadSet(status=status)
    assert us1.nb_not_processed() == 3
    us2 = UploadSet()
    assert us2.nb_not_processed() == 0


def test_UploadSet_nb_preparing():
    status = AggregatedUploadSetStatus(prepared=0, preparing=2, broken=None, not_processed=None)
    us1 = UploadSet(status=status)
    assert us1.nb_preparing() == 2
    us2 = UploadSet()
    assert us2.nb_preparing() == 0


def test_UploadSet_nb_broken():
    status = AggregatedUploadSetStatus(prepared=0, preparing=None, broken=1, not_processed=None)
    us1 = UploadSet(status=status)
    assert us1.nb_broken() == 1
    us2 = UploadSet()
    assert us2.nb_broken() == 0


def test_UploadSet_nb_not_sent():
    files = [
        UploadFile(path="1.jpg", status=UploadFileStatus.not_sent),
        UploadFile(path="2.jpg", status="other_status"),
    ]
    us1 = UploadSet(files=files)
    assert us1.nb_not_sent() == 1
    us2 = UploadSet()
    assert us2.nb_not_sent() == 0


def test_UploadSet_nb_not_ignored():
    files = [
        UploadFile(path="1.jpg", status=UploadFileStatus.not_sent),
        UploadFile(path="2.jpg", status=UploadFileStatus.ignored),
        UploadFile(path="3.jpg", status="other_status"),
    ]
    us1 = UploadSet(files=files)
    assert us1.nb_not_ignored() == 2
    us2 = UploadSet()
    assert us2.nb_not_ignored() == 0


API_MOCK_CONFIGURATION = {
    "auth": {
        "enabled": True,
        "enforce_tos_acceptance": True,
        "registration_is_open": True,
        "user_profile": {"url": "https://panoramax.ign.fr/oauth/realms/geovisio/account/#/personal-info"},
    },
    "color": "#bf360c",
    "defaults": {
        "collaborative_metadata": False,
        "duplicate_distance": 3.0,
        "duplicate_rotation": 62,
        "split_distance": 101,
        "split_time": 301.0,
    },
    "description": {
        "label": "The open source photo mapping solution",
        "langs": {"en": "The open source photo mapping solution"},
    },
    "email": "panoramax@panoramax.fr",
    "geo_coverage": {
        "label": "<b>Photos must be located in France.</b>\n\nThe photos you send to the IGN must be taken on French territory (including overseas territories) and outside certain sensitive areas such as military terrain.",
        "langs": {
            "en": "<b>Photos must be located in France.</b>\n\nThe photos you send to the IGN must be taken on French territory (including overseas territories) and outside certain sensitive areas such as military terrain.",
            "fr": "<b>Les photos doivent être localisées en France.</b>\n\nLes photos que vous envoyez à l'IGN doivent forcément être prises sur le territoire français (ce qui inclut les territoires ultra-marins) et en dehors de certaines zones sensibles comme les terrains militaires.",
        },
    },
    "license": {
        "id": "etalab-2.0",
        "url": "https://www.etalab.gouv.fr/licence-ouverte-open-licence/",
    },
    "logo": "https://design-system.ign.fr/img/styleguide/sg_logos/Logo_IGN_svg/IGN_logo-simplifie_Q.svg",
    "name": {"label": "IGN", "langs": {"en": "IGN", "fr": "IGN"}},
    "pages": ["end-user-license-agreement", "terms-of-service"],
    "version": "2.9.0",
}


@pytest.mark.parametrize(
    ("config", "expected"),
    [
        (
            UploadParameters(),
            UploadParameters(
                merge_params=MergeParams(maxDistance=3, maxRotationAngle=62),
                split_params=SplitParams(maxDistance=101, maxTime=301),
            ),
        ),
        (
            UploadParameters(
                merge_params=None
            ),  # explicitly setting it to None deactivate all merge params, we do not use the default value
            UploadParameters(
                merge_params=None,
                split_params=SplitParams(maxDistance=101, maxTime=301),
            ),
        ),
        (
            UploadParameters(
                merge_params=MergeParams(maxDistance=1, maxRotationAngle=None),
                split_params=SplitParams(maxDistance=10, maxTime=None),
                sort_method=SortMethod.filename_asc,
                relative_heading=90,
            ),
            UploadParameters(
                merge_params=MergeParams(maxDistance=1, maxRotationAngle=62),
                split_params=SplitParams(maxDistance=10, maxTime=301),
                sort_method=SortMethod.filename_asc,
                relative_heading=90,
            ),
        ),
        (
            UploadParameters(split_params=SplitParams(), merge_params=None),
            UploadParameters(
                split_params=SplitParams(maxDistance=101, maxTime=301),
                merge_params=None,
            ),
        ),
        (
            # Note: for the moment we do not get the instance's default value for sort_method (because the API does not expose it)
            UploadParameters(
                merge_params=MergeParams(maxDistance=None, maxRotationAngle=12),
                split_params=SplitParams(maxDistance=None, maxTime=12),
                sort_method=None,
            ),
            UploadParameters(
                merge_params=MergeParams(maxDistance=3, maxRotationAngle=12),
                split_params=SplitParams(maxDistance=101, maxTime=12),
                sort_method=None,
            ),
        ),
    ],
)
def test_UploadSet_update_with_default(respx_mock, config, expected):
    pano = Panoramax(url=MOCK_API_URL)
    respx_mock.get(f"{MOCK_API_URL}/api/configuration").mock().respond(json=API_MOCK_CONFIGURATION)

    with createClientWithRetry() as c:
        config.update_with_instance_defaults(c, pano)
        assert config == expected
