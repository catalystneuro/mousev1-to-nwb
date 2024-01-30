from typing import Optional
import h5py
from neuroconv import BaseDataInterface
from neuroconv.utils import FilePathType, FolderPathType
from pynwb import NWBFile
from pynwb.epoch import TimeIntervals
from pathlib import Path
from natsort import natsorted
from roiextractors.extractors.tiffimagingextractors.scanimagetiff_utils import extract_timestamps_from_file
import numpy as np


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


class Abdeladim2023VisualStimuliInterface(BaseDataInterface):
    """
    Data Interface for writing visual stimuli data for the MouseV1 to NWB conversion
    using Abdeladim2023VisualStimuliInterface.
    """

    def __init__(
        self,
        folder_path: FolderPathType,
        visual_stimulus_file_path: FilePathType,
        visual_stimulus_type: str = None,
        field_description_mapping: Optional[dict] = None,
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
        field_description_mapping: dict, optional, default: None
            A dictonary that map the name of the visual stimulus and its properties (as reported in the .hdf5) 
            and associate a descritpion, e.g.:
            field_description_mapping= {"vis_orientation_tuning": "Visual Orientation Tuning",
                                        "orientation": "orientation of drifting grating in degrees (0-360)",
                                        ...
                                        }
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

        if field_description_mapping is None:
            self._field_description_mapping = {
                "orientation": "orientation of drifting grating in degrees (0-360)",
                "size_vdeg": "size of stimulus in visual degrees, 1d of length n trials",
                "contrast": "contrast of gratings, values between 0-1",
                "location": "(X,Y) location on screen in visual degrees",
                "vis_orientation_tuning_example": "Visual Orientation Tuning",
                "vis_orientation_tuning": "Visual Orientation Tuning",  # TODO add a more descriptive text
                "vis_retinotopy_example": "Retinotopy",
                "vis_retinotopy": "Retinotopy",  # TODO add a more descriptive text
                "vis_simple_example": "Simple Visual Stimuls",
                "vis_simple": "Simple Visual Stimuls",  # TODO add a more descriptive text
            }
        else:
            self._field_description_mapping = field_description_mapping

        super().__init__()
        self.verbose = verbose

    def add_to_nwbfile(
        self,
        nwbfile: NWBFile,
        metadata: Optional[dict] = None,
        stub_test: bool = False,
    ) -> None:
        description = self._field_description_mapping.get(self.visual_stimulus_type)
        stimulus_table = TimeIntervals(
            name="VisualStimuli",
            description=description or self.visual_stimulus_type.replace("_", " "),
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
            description = self._field_description_mapping.get(column_name)
            stimulus_table.add_column(
                name=column_name,
                description=description or column_name.replace("_", " "),
                data=self.visual_stim_dict[column_name],
            )

        nwbfile.add_time_intervals(stimulus_table)
