from typing import Optional
from pathlib import Path
from natsort import natsorted
import numpy as np
import h5py

from neuroconv import BaseDataInterface
from neuroconv.utils import FilePathType, FolderPathType

from pynwb import NWBFile
from pynwb.epoch import TimeIntervals

from roiextractors.extractors.tiffimagingextractors.scanimagetiff_utils import extract_timestamps_from_file


def h5py_to_dict(item):
    if isinstance(item, h5py.Group):
        group_dict = {}
        for key, subitem in item.items():
            group_dict[key] = h5py_to_dict(subitem)
        return group_dict
    elif isinstance(item, h5py.Dataset):
        return item[()]
    else:
        return None


class Hendricks2024VisualStimuliInterface(BaseDataInterface):
    """
    Data Interface for writing visual stimuli data for the MouseV1 to NWB conversion
    using Hendricks2024VisualStimuliInterface.
    """

    def __init__(
        self,
        folder_path: FolderPathType,
        visual_stimulus_file_path: FilePathType,
        visual_stimulus_type: str = None,
        verbose: bool = True,
    ):
        """
        Data interface for adding the visual stimuli to the NWB file.

        Parameters
        ----------
        folder_path : FolderPathType
            The folder path that contains the imaging data.
        visual_stimulus_file_path: FilePathType
            The file path for the .hdf5 file that contains the  visual stimuli data
        visual_stimulus_type: str, default: None
            The name of the visual stimulus applied in the current epoch as reported in the .hdf5 header
        verbose : bool, default: True
        """

        folder_path = Path(folder_path)
        tif_file_paths = natsorted(folder_path.glob("*.tif"))
        assert tif_file_paths, f"The TIF image files are missing from '{folder_path}'."
        self._total_number_of_trials = len(tif_file_paths)

        self.trial_start_times = []
        for tif_file_path in tif_file_paths:
            timestamps = extract_timestamps_from_file(file_path=tif_file_path)
            self.trial_start_times.append(timestamps[0])

        data = h5py.File(visual_stimulus_file_path, "r")
        if visual_stimulus_type not in data.keys() or visual_stimulus_type is None:
            raise ValueError(
                f"'{visual_stimulus_type}' is not a valid visual_stimulus_type"
                f" it must be one of the following {list(data.keys())} as defined in {visual_stimulus_file_path}"
            )
        else:
            self.visual_stimulus_type = visual_stimulus_type

        data = data[self.visual_stimulus_type]
        self.visual_stim_dict = dict()
        for key, item in data.items():
            self.visual_stim_dict[key] = h5py_to_dict(item)

            self._variables_description = {
                "orientation": "orientation of drifting grating in degrees (0-360)",
                "size_vdeg": "size of stimulus in visual degrees, 1d of length n trials",
                "contrast": "contrast of gratings, values between 0-1",
                "location": "(X,Y) location on screen in visual degrees",
            }

        super().__init__()
        self.verbose = verbose

    def add_to_nwbfile(
        self,
        nwbfile: NWBFile,
        metadata: Optional[dict] = None,
        stub_test: bool = False,
    ) -> None:
        stimulus_table = TimeIntervals(
            name="VisualStimuli",
            description=self.visual_stimulus_type.replace("_", " "),
        )
        start_times = self.trial_start_times + self.visual_stim_dict["vis_times"][0]
        stop_times = self.trial_start_times + self.visual_stim_dict["vis_times"][1]
        for t in range(self._total_number_of_trials):
            stimulus_table.add_interval(start_time=start_times[t], stop_time=stop_times[t])

        extra_columns = [key for key in self.visual_stim_dict.keys() if key not in ["vis_ids", "vis_times"]]

        for column_name in extra_columns:
            if isinstance(self.visual_stim_dict[column_name], (int, float, np.generic)):
                # if it is define as scalar, copy the value for each trial
                self.visual_stim_dict[column_name] = (
                    np.ones((len(self.visual_stim_dict["vis_times"][0]))) * self.visual_stim_dict[column_name]
                )
            description = self._variables_description.get(column_name)
            stimulus_table.add_column(
                name=column_name,
                description=description or column_name.replace("_", " "),
                data=self.visual_stim_dict[column_name],
            )

        nwbfile.add_time_intervals(stimulus_table)
