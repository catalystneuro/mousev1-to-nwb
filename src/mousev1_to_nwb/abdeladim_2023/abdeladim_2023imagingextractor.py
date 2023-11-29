from typing import Optional, Tuple, List, Iterable
from pathlib import Path
from natsort import natsorted
from roiextractors.extractors.tiffimagingextractors.scanimagetiffimagingextractor import (
    ScanImageTiffMultiPlaneImagingExtractor,
    ScanImageTiffSinglePlaneImagingExtractor,
)

from roiextractors.imagingextractor import ImagingExtractor
from roiextractors.multiimagingextractor import MultiImagingExtractor
from neuroconv.utils import FolderPathType
from roiextractors.extraction_tools import PathType, FloatType, ArrayType, DtypeType, get_package
import numpy as np
from natsort import natsorted


class Abdeladim2023MultiPlaneImagingExtractor(MultiImagingExtractor):
    """Specialized extractor for Abdeladim2023 conversion project: reading ScanImage .tif files chunked over time"""

    extractor_name = "Abdeladim2023MultiPlaneImagingExtractor"
    is_writable = True
    mode = "folder"

    def __init__(
        self,
        folder_path: FolderPathType,
        channel_name: Optional[str] = None,
    ) -> None:
        self.folder_path = Path(folder_path)
        tif_file_paths = natsorted(self.folder_path.glob("*.tif"))
        assert tif_file_paths, f"The TIF image files are missing from '{self.folder_path}'."

        imaging_extractors = [
            ScanImageTiffMultiPlaneImagingExtractor(file_path=file_path, channel_name=channel_name)
            for file_path in tif_file_paths
        ]

        super().__init__(imaging_extractors=imaging_extractors)


class Abdeladim2023SinglePlaneImagingExtractor(MultiImagingExtractor):
    """Specialized extractor for Abdeladim2023 conversion project: reading ScanImage .tif files chunked over time"""

    extractor_name = "Abdeladim2023SinglePlaneImagingExtractor"
    is_writable = True
    mode = "folder"

    def __init__(
        self,
        folder_path: FolderPathType,
        channel_name: str,
        plane_name: str,
    ) -> None:
        self.folder_path = Path(folder_path)
        tif_file_paths = natsorted(self.folder_path.glob("*.tif"))
        assert tif_file_paths, f"The TIF image files are missing from '{folder_path}'."

        imaging_extractors = [
            ScanImageTiffSinglePlaneImagingExtractor(
                file_path=file_path, channel_name=channel_name, plane_name=plane_name
            )
            for file_path in tif_file_paths
        ]

        super().__init__(imaging_extractors=imaging_extractors)

