from typing import Optional
from pathlib import Path
from natsort import natsorted

from neuroconv.utils import FolderPathType

from roiextractors.extractors.tiffimagingextractors.scanimagetiffimagingextractor import (
    ScanImageTiffMultiPlaneImagingExtractor,
    ScanImageTiffSinglePlaneImagingExtractor,
)
from roiextractors.multiimagingextractor import MultiImagingExtractor


class Hendricks2024MultiPlaneImagingExtractor(MultiImagingExtractor):
    """Specialized extractor for Hendricks2024 conversion project: reading ScanImage .tif files chunked over time"""

    extractor_name = "Hendricks2024MultiPlaneImagingExtractor"
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


class Hendricks2024SinglePlaneImagingExtractor(MultiImagingExtractor):
    """Specialized extractor for Hendricks2024 conversion project: reading ScanImage .tif files chunked over time"""

    extractor_name = "Hendricks2024SinglePlaneImagingExtractor"
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
