from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class Type(Enum):
    Point = "Point"


class Geometry1(BaseModel):
    type: Type
    coordinates: List[float] = Field(..., min_length=2)
    bbox: Optional[List[float]] = Field(None, min_length=4)


class Type1(Enum):
    LineString = "LineString"


class Geometry2(BaseModel):
    type: Type1
    coordinates: List[List[float]] = Field(..., min_length=2)
    bbox: Optional[List[float]] = Field(None, min_length=4)


class Type2(Enum):
    Polygon = "Polygon"


class Geometry3(BaseModel):
    type: Type2
    coordinates: List[List[List[float]]]
    bbox: Optional[List[float]] = Field(None, min_length=4)


class Type3(Enum):
    MultiPoint = "MultiPoint"


class Geometry4(BaseModel):
    type: Type3
    coordinates: List[List[float]]
    bbox: Optional[List[float]] = Field(None, min_length=4)


class Type4(Enum):
    MultiLineString = "MultiLineString"


class Geometry5(BaseModel):
    type: Type4
    coordinates: List[List[List[float]]]
    bbox: Optional[List[float]] = Field(None, min_length=4)


class Type5(Enum):
    MultiPolygon = "MultiPolygon"


class Geometry6(BaseModel):
    type: Type5
    coordinates: List[List[List[List[float]]]]
    bbox: Optional[List[float]] = Field(None, min_length=4)
