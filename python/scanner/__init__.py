"""Scanner — автоматизированная система 3D-сканирования."""

__version__ = "0.1.0"

from ._scanner_cpp import (
    BoundingBox,
    PointCloud,
    TriangleMesh,
    RepairReport,
    MeshRepair,
    PrintabilityReport,
    PrintPreparation,
)

__all__ = [
    "BoundingBox",
    "PointCloud",
    "TriangleMesh",
    "RepairReport",
    "MeshRepair",
    "PrintabilityReport",
    "PrintPreparation",
]
