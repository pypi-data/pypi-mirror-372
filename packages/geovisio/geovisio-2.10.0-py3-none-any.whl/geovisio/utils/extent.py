from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class Temporal(BaseModel):
    """Temporal extent"""

    interval: List[List[datetime]]
    """Interval"""


class Spatial(BaseModel):
    """Spatial extent"""

    bbox: List[List[float]]
    """Bounding box"""


class Extent(BaseModel):
    """Spatio-temporal extents"""

    temporal: Optional[Temporal]
    spatial: Optional[Spatial]


class TemporalExtent(BaseModel):
    """Temporal extents (without spatial extent)"""

    temporal: Optional[Temporal]
