from uuid import UUID
import pytest
from geovisio.utils import db
from geovisio.utils import semantics
from geovisio.utils.annotations import Annotation
from geovisio.utils.semantics import QualifierSemantic
from geovisio.utils.tags import SemanticTag
from . import conftest


@pytest.fixture
def create_test_app(dburl, tmp_path):
    with conftest.create_test_app(
        {
            "TESTING": True,
            "API_BLUR_URL": conftest.MOCK_BLUR_API,
            "PICTURE_PROCESS_DERIVATES_STRATEGY": "PREPROCESS",
            "DB_URL": dburl,
            "FS_URL": str(tmp_path),
            "FS_TMP_URL": None,
            "FS_PERMANENT_URL": None,
            "FS_DERIVATES_URL": None,
            "SECRET_KEY": "a very secret key",
        }
    ) as app:
        yield app


def get_annotation_semantics(client, seq, pic):
    item = client.get(f"/api/collections/{seq.id}/items/{pic}")
    assert item.status_code == 200, item.text
    return conftest.cleanup_annotations(item.json["properties"]["annotations"])


def simplify_pic_history(history):
    h = history["pictures"]
    # we remove the annotation shape from the history, to simplify asserts
    return [(str(change[0]), change[1], [{k: v for k, v in s.items() if k != "annotation_shape"} for s in change[2]]) for change in h]


@conftest.SEQ_IMGS
def test_delete_annotation_tags_from_service(
    dburl, datafiles, create_test_app, bobAccountToken, bobAccountID, defaultAccountID, defaultAccountToken
):
    with create_test_app.test_client() as client:
        conftest.insert_db_model(
            conftest.ModelToInsert(
                upload_sets=[
                    conftest.UploadSetToInsert(
                        sequences=[
                            conftest.SequenceToInsert(
                                pictures=[
                                    conftest.PictureToInsert(original_file_name="1.jpg"),
                                    conftest.PictureToInsert(original_file_name="2.jpg"),
                                ]
                            )
                        ],
                        account_id=bobAccountID,
                    )
                ]
            )
        )
        seq = conftest.getPictureIds(dburl)[0]
        first_pic = str(seq.pictures[0].id)

        response = client.post(
            f"/api/collections/{seq.id}/items/{first_pic}/annotations",
            headers={"Authorization": f"Bearer {defaultAccountToken()}"},
            json={
                "shape": [1, 1, 10, 10],
                "semantics": [
                    {"key": "osm|traffic_sign", "value": "yes"},
                    {"key": "detection_confidence[osm|traffic_sign=yes]", "value": "0.313"},
                    {"key": "detection_model[osm|traffic_sign=yes]", "value": "SGBlur-yolo11n/0.1.0"},
                ],
            },
        )
        assert response.status_code == 200
        response = client.post(
            f"/api/collections/{seq.id}/items/{first_pic}/annotations",
            headers={"Authorization": f"Bearer {defaultAccountToken()}"},
            json={
                "shape": [2, 2, 20, 20],
                "semantics": [
                    {"key": "osm|another_tag", "value": "some_value"},
                    {"key": "detection_model[osm|another_tag=some_value]", "value": "SGBlur-yolo11n/0.1.0"},
                    {"key": "a tag that should not be deleted", "value": "👑"},
                ],
            },
        )
        response = client.post(
            f"/api/collections/{seq.id}/items/{first_pic}/annotations",
            headers={"Authorization": f"Bearer {defaultAccountToken()}"},
            json={
                "shape": [2, 2, 20, 20],
                "semantics": [
                    {"key": "osm|tag", "value": "val"},
                    {"key": "detection_confidence[osm|tag=val]", "value": "0.313"},
                    {"key": "detection_model[osm|tag=val]", "value": "AnotherService-yolo11n/0.1.0"},
                ],
            },
        )
        # also add an annotation to the second pic, that should not be updated
        response = client.post(
            f"/api/collections/{seq.id}/items/{str(seq.pictures[1].id)}/annotations",
            headers={"Authorization": f"Bearer {defaultAccountToken()}"},
            json={
                "shape": [5, 5, 50, 50],
                "semantics": [
                    {"key": "osm|traffic_sign", "value": "yes"},
                    {"key": "detection_confidence[osm|traffic_sign=yes]", "value": "0.313"},
                    {"key": "detection_model[osm|traffic_sign=yes]", "value": "SGBlur-yolo11n/0.1.0"},
                ],
            },
        )
        assert response.status_code == 200

        with db.conn(create_test_app) as conn:
            annotations_tags = semantics.delete_annotation_tags_from_service(
                conn, first_pic, service_name="SGBlur", account=defaultAccountID
            )

            assert sorted([t for a in annotations_tags for t in a.semantics], key=lambda x: x.key) == sorted(
                [
                    SemanticTag(key="osm|traffic_sign", value="yes"),
                    SemanticTag(key="detection_confidence[osm|traffic_sign=yes]", value="0.313"),
                    SemanticTag(key="detection_model[osm|traffic_sign=yes]", value="SGBlur-yolo11n/0.1.0"),
                    SemanticTag(key="osm|another_tag", value="some_value"),
                    SemanticTag(key="detection_model[osm|another_tag=some_value]", value="SGBlur-yolo11n/0.1.0"),
                ],
                key=lambda x: x.key,
            )

        first_pic_annotations = get_annotation_semantics(client, seq, first_pic)

        assert first_pic_annotations == [
            {
                "semantics": [
                    {"key": "a tag that should not be deleted", "value": "👑"},
                    {"key": "detection_confidence[osm|tag=val]", "value": "0.313"},
                    {"key": "detection_model[osm|tag=val]", "value": "AnotherService-yolo11n/0.1.0"},
                    {"key": "osm|tag", "value": "val"},
                ],
                "shape": {"coordinates": [[[2, 2], [20, 2], [20, 20], [2, 20], [2, 2]]], "type": "Polygon"},
            }
        ]

        # the second picture semantics has not be updated
        second_pic_annotations = get_annotation_semantics(client, seq, seq.pictures[1].id)
        assert second_pic_annotations == [
            {
                "semantics": [
                    {"key": "detection_confidence[osm|traffic_sign=yes]", "value": "0.313"},
                    {"key": "detection_model[osm|traffic_sign=yes]", "value": "SGBlur-yolo11n/0.1.0"},
                    {"key": "osm|traffic_sign", "value": "yes"},
                ],
                "shape": {"coordinates": [[[5, 5], [50, 5], [50, 50], [5, 50], [5, 5]]], "type": "Polygon"},
            }
        ]

        history = conftest.get_tags_history()
        simplify_history = simplify_pic_history(history)
        assert simplify_history[:4] == [
            (
                first_pic,
                "Default account",
                [
                    {"key": "osm|traffic_sign", "value": "yes", "action": "add"},
                    {"key": "detection_confidence[osm|traffic_sign=yes]", "value": "0.313", "action": "add"},
                    {"key": "detection_model[osm|traffic_sign=yes]", "value": "SGBlur-yolo11n/0.1.0", "action": "add"},
                ],
            ),
            (
                first_pic,
                "Default account",
                [
                    {"key": "osm|another_tag", "value": "some_value", "action": "add"},
                    {"key": "detection_model[osm|another_tag=some_value]", "value": "SGBlur-yolo11n/0.1.0", "action": "add"},
                    {"key": "a tag that should not be deleted", "value": "👑", "action": "add"},
                ],
            ),
            (
                first_pic,
                "Default account",
                [
                    {"key": "osm|tag", "value": "val", "action": "add"},
                    {"key": "detection_confidence[osm|tag=val]", "value": "0.313", "action": "add"},
                    {"key": "detection_model[osm|tag=val]", "value": "AnotherService-yolo11n/0.1.0", "action": "add"},
                ],
            ),
            (
                seq.pictures[1].id,
                "Default account",
                [
                    {"key": "osm|traffic_sign", "value": "yes", "action": "add"},
                    {"key": "detection_confidence[osm|traffic_sign=yes]", "value": "0.313", "action": "add"},
                    {"key": "detection_model[osm|traffic_sign=yes]", "value": "SGBlur-yolo11n/0.1.0", "action": "add"},
                ],
            ),
        ]

        a1_edit = (
            first_pic,
            "Default account",
            [
                {"action": "delete", "key": "osm|traffic_sign", "value": "yes"},
                {"action": "delete", "key": "detection_confidence[osm|traffic_sign=yes]", "value": "0.313"},
                {"action": "delete", "key": "detection_model[osm|traffic_sign=yes]", "value": "SGBlur-yolo11n/0.1.0"},
            ],
        )
        a2_edit = (
            first_pic,
            "Default account",
            [
                {"action": "delete", "key": "osm|another_tag", "value": "some_value"},
                {"action": "delete", "key": "detection_model[osm|another_tag=some_value]", "value": "SGBlur-yolo11n/0.1.0"},
            ],
        )
        # no ordering on the edits between annotations
        assert simplify_history[4:] == [a1_edit, a2_edit] or simplify_history[4:] == [a2_edit, a1_edit]


@pytest.mark.parametrize(
    "semantic_tag, expected_qualifiers",
    [
        (SemanticTag(key="osm|traffic_sign", value="yes"), None),
        (
            SemanticTag(key="detection_confidence[osm|traffic_sign=yes]", value="0.313"),
            QualifierSemantic(
                qualifier="detection_confidence",
                associated_key="osm|traffic_sign",
                associated_value="yes",
                raw_tag=SemanticTag(key="detection_confidence[osm|traffic_sign=yes]", value="0.313"),
            ),
        ),
        (
            SemanticTag(key="detection_confidence[osm|traffic_sign=*]", value="0.313"),
            QualifierSemantic(
                qualifier="detection_confidence",
                associated_key="osm|traffic_sign",
                associated_value="*",
                raw_tag=SemanticTag(key="detection_confidence[osm|traffic_sign=*]", value="0.313"),
            ),
        ),
        (
            SemanticTag(key="detection_model[osm|traffic_sign=yes]", value="SGBlur-yolo11n/0.1.0"),
            QualifierSemantic(
                qualifier="detection_model",
                associated_key="osm|traffic_sign",
                associated_value="yes",
                raw_tag=SemanticTag(key="detection_model[osm|traffic_sign=yes]", value="SGBlur-yolo11n/0.1.0"),
            ),
        ),
        (SemanticTag(key="some_invalid_qualifier[]", value="SGBlur-yolo11n/0.1.0"), None),  # [] is not a valid qualifier
        (
            SemanticTag(key="detection_model[osm|traffic_sign]", value="some_value"),
            QualifierSemantic(
                qualifier="detection_model",
                associated_key="osm|traffic_sign",
                associated_value=None,
                raw_tag=SemanticTag(key="detection_model[osm|traffic_sign]", value="some_value"),
            ),
        ),
        (
            SemanticTag(key="detection_model[osm|traffic_sign=FR:A13b;FR:M9z[Passage surélevé]]", value="PanierAvide/1.0.0"),
            QualifierSemantic(
                qualifier="detection_model",
                associated_key="osm|traffic_sign",
                associated_value="FR:A13b;FR:M9z[Passage surélevé]",
                raw_tag=SemanticTag(key="detection_model[osm|traffic_sign=FR:A13b;FR:M9z[Passage surélevé]]", value="PanierAvide/1.0.0"),
            ),
        ),
    ],
)
def test_as_qualifiers(semantic_tag, expected_qualifiers):
    assert semantics.as_qualifier(semantic_tag) == expected_qualifiers


def test_get_qualifiers():
    assert semantics.get_qualifiers(
        [
            SemanticTag(key="osm|traffic_sign", value="yes"),
            SemanticTag(key="detection_confidence[osm|traffic_sign=yes]", value="0.313"),
            SemanticTag(key="detection_model[osm|traffic_sign=yes]", value="SGBlur-yolo11n/0.1.0"),
        ]
    ) == [
        QualifierSemantic(
            qualifier="detection_confidence",
            associated_key="osm|traffic_sign",
            associated_value="yes",
            raw_tag=SemanticTag(key="detection_confidence[osm|traffic_sign=yes]", value="0.313"),
        ),
        QualifierSemantic(
            qualifier="detection_model",
            associated_key="osm|traffic_sign",
            associated_value="yes",
            raw_tag=SemanticTag(key="detection_model[osm|traffic_sign=yes]", value="SGBlur-yolo11n/0.1.0"),
        ),
    ]


@pytest.mark.parametrize(
    "semantic_tag, qualifier_tag, is_qualified",
    [
        (
            SemanticTag(key="osm|traffic_sign", value="yes"),
            SemanticTag(key="detection_model[osm|traffic_sign]", value="X"),
            True,
        ),
        (
            SemanticTag(key="osm|traffic_sign", value="yes"),
            SemanticTag(key="detection_model[osm|traffic_sign=yes]", value="X"),
            True,
        ),
        (
            SemanticTag(key="osm|traffic_sign", value="yes"),
            SemanticTag(key="detection_model[osm|traffic_sign=no]", value="X"),
            False,
        ),
        (
            SemanticTag(key="osm|traffic_sign", value="yes"),
            SemanticTag(key="detection_model[osm|traffic_sign=*]", value="X"),
            True,
        ),
        (
            SemanticTag(key="osm|traffic_sign", value="yes"),
            SemanticTag(key="detection_model[other_key=*]", value="X"),
            False,
        ),
    ],
)
def test_tag_is_qualified_by(semantic_tag, qualifier_tag, is_qualified):
    q = semantics.as_qualifier(qualifier_tag)
    assert q is not None
    assert q.qualifies(semantic_tag) == is_qualified


def test_find_semantics_from_service():
    assert sorted(
        semantics.find_semantics_from_service(
            Annotation(
                id=UUID("00000000-0000-0000-0000-000000000001"),
                picture_id=UUID("00000000-0000-0000-0000-000000000002"),
                shape={"coordinates": [[[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]], "type": "Polygon"},
                semantics=[
                    SemanticTag(key="osm|traffic_sign", value="yes"),
                    SemanticTag(key="detection_confidence[osm|traffic_sign=yes]", value="0.313"),
                    SemanticTag(key="detection_model[osm|traffic_sign=yes]", value="SGBlur-yolo11n/0.1.0"),
                    SemanticTag(key="osm|amenity", value="recycling"),
                    SemanticTag(key="some_qualifier[osm|amenity=recycling]", value="very import recycling property"),
                    SemanticTag(key="detection_model[osm|amenity]", value="SGBlur-yolo11n/0.1.0"),
                    SemanticTag(key="osm|traffic_sign", value="max_speed"),
                    SemanticTag(key="detection_confidence[osm|traffic_sign=max_speed]", value="0.313"),
                    SemanticTag(key="detection_model[osm|traffic_sign=max_speed]", value="AnotherService-yolo11n/0.1.0"),
                    SemanticTag(key="osm|another_tag", value="some_value"),
                    SemanticTag(key="detection_model[osm|another_tag=some_value]", value="SGBlur-yolo11n/0.1.0"),
                    SemanticTag(key="detection_model[osm|anothsomething=some_value]", value="AnotherService-yolo11n/0.1.0"),
                    SemanticTag(key="detection_model[osm|traffic_sign]", value="some_value"),
                    SemanticTag(key="a random tag", value="some random value"),
                ],
            ),
            service_name="SGBlur",
        ),
        key=lambda x: x.key,
    ) == sorted(
        [
            SemanticTag(key="osm|traffic_sign", value="yes"),
            SemanticTag(key="detection_confidence[osm|traffic_sign=yes]", value="0.313"),
            SemanticTag(key="detection_model[osm|traffic_sign=yes]", value="SGBlur-yolo11n/0.1.0"),
            SemanticTag(key="osm|amenity", value="recycling"),
            SemanticTag(key="some_qualifier[osm|amenity=recycling]", value="very import recycling property"),
            SemanticTag(key="detection_model[osm|amenity]", value="SGBlur-yolo11n/0.1.0"),
            SemanticTag(key="detection_model[osm|traffic_sign]", value="some_value"),
            SemanticTag(key="osm|another_tag", value="some_value"),
            SemanticTag(key="detection_model[osm|another_tag=some_value]", value="SGBlur-yolo11n/0.1.0"),
        ],
        key=lambda x: x.key,
    )
