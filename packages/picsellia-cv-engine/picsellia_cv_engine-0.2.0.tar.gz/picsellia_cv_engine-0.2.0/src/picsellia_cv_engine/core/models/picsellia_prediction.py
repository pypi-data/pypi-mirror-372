from dataclasses import dataclass

from picsellia import Asset, Label


@dataclass
class PicselliaLabel:
    """Label associated with a prediction."""

    value: Label

    @property
    def name(self) -> str:
        return self.value.name

    @property
    def id(self) -> int:
        return self.value.id


@dataclass
class PicselliaConfidence:
    """Confidence score for a prediction (typically between 0 and 1)."""

    value: float


@dataclass
class PicselliaRectangle:
    """Bounding box in [x, y, width, height] format."""

    value: list[int]

    def __init__(self, x: int, y: int, w: int, h: int):
        """Initialize rectangle coordinates."""
        self.value = [int(x), int(y), int(w), int(h)]

    @property
    def x(self) -> int:
        return self.value[0]

    @property
    def y(self) -> int:
        return self.value[1]

    @property
    def width(self) -> int:
        return self.value[2]

    @property
    def height(self) -> int:
        return self.value[3]


@dataclass
class PicselliaText:
    """Recognized text from OCR predictions."""

    value: str


@dataclass
class PicselliaPolygon:
    """Polygon represented by a list of points."""

    value: list[list[int]]

    def __init__(self, points: list[list[int]]):
        """Initialize polygon with a list of [x, y] points."""
        self.value = points

    @property
    def points(self) -> list[list[int]]:
        return self.value

    def compute_area(self) -> float:
        # Optional: simple polygon area (Shoelace formula)
        from shapely.geometry import Polygon

        return Polygon(self.points).area if self.points else 0.0


@dataclass
class PicselliaClassificationPrediction:
    """Prediction result for classification tasks."""

    asset: Asset
    label: PicselliaLabel
    confidence: PicselliaConfidence


@dataclass
class PicselliaRectanglePrediction:
    """Prediction result for object detection (rectangles)."""

    asset: Asset
    boxes: list[PicselliaRectangle]
    labels: list[PicselliaLabel]
    confidences: list[PicselliaConfidence]


@dataclass
class PicselliaOCRPrediction:
    """Prediction result for OCR tasks."""

    asset: Asset
    boxes: list[PicselliaRectangle]
    labels: list[PicselliaLabel]
    texts: list[PicselliaText]
    confidences: list[PicselliaConfidence]


@dataclass
class PicselliaPolygonPrediction:
    """Prediction result for segmentation tasks."""

    asset: Asset
    polygons: list[PicselliaPolygon]
    labels: list[PicselliaLabel]
    confidences: list[PicselliaConfidence]
