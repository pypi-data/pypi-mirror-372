from xml.dom import ValidationErr
from flask import json
from pydantic import BaseModel, ValidationError
import pytest

from geovisio.utils.pic_shape import InputAnnotationShape


class AnnotationShape(BaseModel):
    shape: InputAnnotationShape


@pytest.mark.parametrize(
    ("input"),
    [
        ([1, 1, 10, 10]),
        (
            {
                "type": "Polygon",
                "coordinates": [
                    [
                        [1, 10],
                        [10, 100],
                        [5, 300],
                        [240, 632],
                        [1000, 1000],
                        [1, 10],
                    ]
                ],
            }
        ),
    ],
)
def test_shape_input(input):

    a = AnnotationShape(shape=input)
    assert a.model_dump_json().replace(" ", "") == json.dumps({"shape": input}).replace(" ", "")


@pytest.mark.parametrize(
    ("input", "error"),
    [
        (
            [1, 1],
            """1 validation error for AnnotationShape
shape.bbox
    List should have at least 4 items after validation, not 2 [type=too_short, input_value=[1, 1], input_type=list]
    For further information visit https://errors.pydantic.dev/2.11/v/too_short""",
        ),
        (
            {
                "type": "Point",
                "coordinates": [
                    [
                        [1, 10],
                    ]
                ],
            },
            """2 validation errors for AnnotationShape
shape.geometry.type
    Input should be 'Polygon' [type=literal_error, input_value='Point', input_type=str]
        For further information visit https://errors.pydantic.dev/2.11/v/literal_error
shape.geometry.coordinates.0
    List should have at least 4 items after validation, not 1 [type=too_short, input_value=[[1, 10]], input_type=list]
        For further information visit https://errors.pydantic.dev/2.11/v/too_short""",
        ),
        (
            {
                "type": "Polygon",
                "coordinates": [
                    [
                        [1, 10],
                        [10, 100],
                        [5, 300],
                        [240, 632],
                        [1000, 1000],
                    ]
                ],
            },
            """1 validation error for AnnotationShape
shape.geometry.coordinates
  Value error, All linear rings have the same start and end coordinates [type=value_error, input_value=[[[1, 10], [10, 100], [5,...40, 632], [1000, 1000]]], input_type=list]
    For further information visit https://errors.pydantic.dev/2.11/v/value_error""",
        ),
        (
            "pouet",
            """1 validation error for AnnotationShape
shape.geometry
    Input should be a valid dictionary or instance of Polygon [type=model_type, input_value='pouet', input_type=str]
        For further information visit https://errors.pydantic.dev/2.11/v/model_type""",
        ),
    ],
)
def test_wrong_shape(input, error):

    with pytest.raises(ValidationError) as e:

        AnnotationShape(shape=input)

    assert str(e.value).replace(" ", "").replace("\n", "").replace("\t", "") == error.replace(" ", "").replace("\n", "").replace(
        "\t", ""
    ), str(e.value)
