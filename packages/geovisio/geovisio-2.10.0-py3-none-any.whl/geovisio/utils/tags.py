from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class TagAction(str, Enum):
    """Actions to perform on a tag list"""

    add = "add"
    delete = "delete"


class SemanticTagUpdate(BaseModel):
    """Parameters used to update a tag list"""

    action: TagAction = Field(default=TagAction.add)
    """Action to perform on the tag list. The default action is `add` which will add the given tag to the list.
    The action can also be to `delete` the key/value"""
    key: str = Field(max_length=256)
    """Key of the tag to update limited to 256 characters"""
    value: str = Field(max_length=2048)
    """Value of the tag to update limited ot 2048 characters"""

    model_config = ConfigDict(use_attribute_docstrings=True)


class SemanticTag(BaseModel):
    key: str
    """Key of the tag"""
    value: str
    """Value of the tag"""
