from typing import Optional, Tuple, List, Iterable
from pathlib import Path
import glob
from roiextractors.extractors.tiffimagingextractors.scanimagetiffimagingextractor import (
    ScanImageTiffMultiPlaneImagingExtractor,
    ScanImageTiffSinglePlaneImagingExtractor,
)

from roiextractors.imagingextractor import ImagingExtractor
from roiextractors.multiimagingextractor import MultiImagingExtractor
from neuroconv.utils import FolderPathType
from roiextractors.extraction_tools import PathType, FloatType, ArrayType, DtypeType, get_package
import numpy as np


class Abdeladim2023MultiPlaneImagingExtractor(ImagingExtractor):
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
        tif_file_paths = sorted(glob.glob(f"{self.folder_path}/*.tif"))
        assert tif_file_paths, f"The TIF image files are missing from '{folder_path}'."

        imaging_extractors = [
            ScanImageTiffMultiPlaneImagingExtractor(file_path=file_path, channel_name=channel_name)
            for file_path in tif_file_paths
        ]

        self.imaging_extractor = MultiImagingExtractor(imaging_extractors)
        times = self.imaging_extractor._get_times()
        self.set_times(times=times)

    def get_frames(self, frame_idxs: ArrayType) -> np.ndarray:
        """Get specific video frames from indices (not necessarily continuous).

        Parameters
        ----------
        frame_idxs: array-like
            Indices of frames to return.

        Returns
        -------
        frames: numpy.ndarray
            The video frames.
        """
        return self.imaging_extractor.get_frames(frame_idxs=frame_idxs)

    def get_num_frames(self) -> int:
        return self.imaging_extractor.get_num_frames()

    def get_video(self, start_frame: Optional[int] = None, end_frame: Optional[int] = None) -> np.ndarray:
        """Get the video frames.

        Parameters
        ----------
        start_frame: int, optional
            Start frame index (inclusive).
        end_frame: int, optional
            End frame index (exclusive).

        Returns
        -------
        video: numpy.ndarray
            The video frames.
        """
        return self.imaging_extractor.get_video(start_frame=start_frame, end_frame=end_frame)

    def get_channel_names(self):
        return self.imaging_extractor.get_channel_names()

    def get_image_size(self):
        return self.imaging_extractor.get_image_size()

    def get_num_channels(self):
        return self.imaging_extractor.get_num_channels()

    def get_sampling_frequency(self):
        return self.imaging_extractor.get_sampling_frequency()


class Abdeladim2023SinglePlaneImagingExtractor(ImagingExtractor):
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
        tif_file_paths = sorted(glob.glob(f"{self.folder_path}/*.tif"))
        assert tif_file_paths, f"The TIF image files are missing from '{folder_path}'."

        imaging_extractors = [
            ScanImageTiffSinglePlaneImagingExtractor(
                file_path=file_path, channel_name=channel_name, plane_name=plane_name
            )
            for file_path in tif_file_paths
        ]

        self.imaging_extractor = MultiImagingExtractor(imaging_extractors)
        times = self.imaging_extractor._get_times()
        self.set_times(times=times)

    def get_frames(self, frame_idxs: ArrayType,channel: Optional[int] = 0) -> np.ndarray:
        """Get specific video frames from indices (not necessarily continuous).

        Parameters
        ----------
        frame_idxs: array-like
            Indices of frames to return.

        Returns
        -------
        frames: numpy.ndarray
            The video frames.
        """
        return self.imaging_extractor.get_frames(frame_idxs=frame_idxs)

    def get_num_frames(self) -> int:
        return self.imaging_extractor.get_num_frames()

    def get_video(self, start_frame: Optional[int] = None, end_frame: Optional[int] = None,channel: Optional[int] = 0) -> np.ndarray:
        """Get the video frames.

        Parameters
        ----------
        start_frame: int, optional
            Start frame index (inclusive).
        end_frame: int, optional
            End frame index (exclusive).

        Returns
        -------
        video: numpy.ndarray
            The video frames.
        """
        return self.imaging_extractor.get_video(start_frame=start_frame, end_frame=end_frame)

    def get_channel_names(self):
        return self.imaging_extractor.get_channel_names()

    def get_image_size(self):
        return self.imaging_extractor.get_image_size()

    def get_num_channels(self):
        return self.imaging_extractor.get_num_channels()

    def get_sampling_frequency(self):
        return self.imaging_extractor.get_sampling_frequency()
