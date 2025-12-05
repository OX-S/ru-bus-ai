from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SemanticIndexDocument(BaseModel):
    """Single item to be embedded into a vector index"""

    id: str
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class StopSemanticInfo(BaseModel):
    """Canonical semantic model for a transit stop"""

    stop_id: str
    official_name: str

    nicknames: List[str] = Field(default_factory=list)
    campus: Optional[str] = None

    landmarks_nearby: List[str] = Field(default_factory=list)

    routes_serving: List[str] = Field(default_factory=list)

    lat: Optional[float] = None
    lon: Optional[float] = None

    def to_index_document(self) -> SemanticIndexDocument:
        """Renders given stop into a single semantic document plus metadata"""
        parts: List[str] = [
            f"Stop: {self.official_name} (stop_id={self.stop_id}).",
        ]

        if self.campus:
            parts.append(f"Campus: {self.campus}.")

        if self.nicknames:
            nick_str = ", ".join(f'"{name}"' for name in self.nicknames)
            parts.append(f"Nicknames: {nick_str}.")

        if self.landmarks_nearby:
            landmarks_str = ", ".join(f'"{name}"' for name in self.landmarks_nearby)
            parts.append(f"Nearby landmarks: {landmarks_str}.")

        if self.routes_serving:
            routes_str = ", ".join(self.routes_serving)
            parts.append(f"Routes serving this stop: {routes_str}.")

        text = " ".join(parts)

        metadata: Dict[str, Any] = {
            "type": "stop",
            "stop_id": self.stop_id,
            "official_name": self.official_name,
        }

        if self.campus:
            metadata["campus"] = self.campus

        if self.landmarks_nearby:
            metadata["landmarks_nearby"] = self.landmarks_nearby

        if self.routes_serving:
            metadata["routes_serving"] = self.routes_serving

        if self.lat is not None and self.lon is not None:
            metadata["lat"] = self.lat
            metadata["lon"] = self.lon

        return SemanticIndexDocument(id=self.stop_id, text=text, metadata=metadata)


class LandmarkSemanticInfo(BaseModel):
    """Canonical semantic model for a landmark or place"""

    landmark_id: str
    name: str

    # Other ways students might refer to this place.
    aliases: List[str] = Field(default_factory=list)

    # Closest stop identifiers for reaching this place.
    near_stop_ids: List[str] = Field(default_factory=list)

    campus: Optional[str] = None
    description: Optional[str] = None

    def to_index_document(self) -> SemanticIndexDocument:
        parts: List[str] = [
            f"Landmark: {self.name}.",
        ]

        if self.campus:
            parts.append(f"Campus: {self.campus}.")

        if self.aliases:
            alias_str = ", ".join(f'"{alias}"' for alias in self.aliases)
            parts.append(f"Also known as: {alias_str}.")

        if self.near_stop_ids:
            stops_str = ", ".join(self.near_stop_ids)
            parts.append(f"Closest stops: {stops_str}.")

        if self.description:
            parts.append(f"Description: {self.description}.")

        text = " ".join(parts)

        metadata: Dict[str, Any] = {
            "type": "landmark",
            "landmark_id": self.landmark_id,
            "name": self.name,
        }

        if self.campus:
            metadata["campus"] = self.campus

        if self.near_stop_ids:
            metadata["near_stop_ids"] = self.near_stop_ids

        return SemanticIndexDocument(id=self.landmark_id, text=text, metadata=metadata)


def build_stop_documents(stops: List[StopSemanticInfo]) -> List[SemanticIndexDocument]:
    return [stop.to_index_document() for stop in stops]


def build_landmark_documents(
    landmarks: List[LandmarkSemanticInfo],
) -> List[SemanticIndexDocument]:
    return [landmark.to_index_document() for landmark in landmarks]

