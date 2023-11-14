from typing import Optional, Tuple, List, Iterable
from pathlib import Path
import glob
from roiextractors.extractors.tiffimagingextractors.scanimagetiffimagingextractor import (
    ScanImageTiffMultiPlaneImagingExtractor,
)
from roiextractors.extractors.tiffimagingextractors.brukertiffimagingextractor import (
    BrukerTiffMultiPlaneImagingExtractor,
)
from roiextractors.imagingextractor import ImagingExtractor
from roiextractors.extraction_tools import PathType, FloatType, ArrayType, DtypeType, get_package
import numpy as np


class Abdeladim2023VolumetricImagingExtractor(ImagingExtractor):
    """Specialized extractor for Abdeladim2023 conversion project: reading ScanImage .tif files chunked over time"""

    extractor_name = "Abdeladim2023VolumetricImagingExtractor"
    is_writable = True
    mode = "folder"

    def __init__(
        self,
        folder_path: PathType,
        channel_name: Optional[str] = None,
    ) -> None:
        self.folder_path = Path(folder_path)
        tif_file_paths = sorted(glob.glob(f"{self.folder_path}/*.tif"))
        assert tif_file_paths, f"The TIF image files are missing from '{folder_path}'."

        self.imaging_extractors = [
            ScanImageTiffMultiPlaneImagingExtractor(file_path=file_path, channel_name=channel_name)
            for file_path in tif_file_paths
        ]

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
        if isinstance(frame_idxs, int):
            frame_idxs = [frame_idxs]

        if not all(np.diff(frame_idxs) == 1):
            return np.concatenate([self._get_single_frame(frame=idx) for idx in frame_idxs])
        else:
            return self.get_video(start_frame=frame_idxs[0], end_frame=frame_idxs[-1] + 1)

    def get_num_frames(self) -> int:
        return sum([extractor.get_num_frames() for extractor in self.imaging_extractors])

    def _get_single_frame(self, frame: int) -> np.ndarray:
        """Get a single frame of data from the TIFF file.

        Parameters
        ----------
        frame : int
            The index of the frame to retrieve.

        Returns
        -------
        frame: numpy.ndarray
            The frame of data.
        """

        return self.get_video(start_frame=frame, end_frame=frame + 1)

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
        start = start_frame if start_frame is not None else 0
        end = end_frame if end_frame is not None else self.get_num_frames()
        video = []
        for extractor in self.imaging_extractors:
            video = np.append(video, extractor.get_video())

        return video[:, :, :, start:end]

    def get_channel_names(self):
        return self.imaging_extractors[0].get_channel_names()

    def get_image_size(self):
        return self.imaging_extractors[0].get_image_size()

    def get_num_channels(self):
        return self.imaging_extractors[0].get_num_channels()

    def get_sampling_frequency(self):
        return self.imaging_extractors[0].get_sampling_frequency()
