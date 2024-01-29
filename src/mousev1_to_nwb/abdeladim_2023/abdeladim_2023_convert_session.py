"""Primary script to run to convert an entire session for of data using the NWBConverter."""
from pathlib import Path
from typing import Union
import h5py
from zoneinfo import ZoneInfo
import numpy as np

from neuroconv.utils import load_dict_from_file, dict_deep_update

from abdeladim_2023nwbconverter import Abdeladim2023NWBConverter
from abdeladim_2023nwbconverter import get_default_segmentation_to_imaging_name_mapping


def session_to_nwb(
    data_dir_path: Union[str, Path],
    output_dir_path: Union[str, Path],
    epoch_name: str,
    subject_id: str,
    segmentation_start_frame: int,
    segmentation_end_frame: int,
    stub_test: bool = False,
):
    data_dir_path = Path(data_dir_path)
    output_dir_path = Path(output_dir_path)
    if stub_test:
        output_dir_path = output_dir_path / "nwb_stub"
    output_dir_path.mkdir(parents=True, exist_ok=True)

    # Add Imaging
    imaging_folder_path = data_dir_path / "raw-tiffs" / epoch_name
    # Add Segmentation
    segmentation_folder_path = data_dir_path / "processed-suite2p-data/suite2p"
    segmentation_to_imaging_plane_map = get_default_segmentation_to_imaging_name_mapping(
        imaging_folder_path, segmentation_folder_path
    )
    # Check if session has holographic photostimulation data
    holographic_stimulation_file_path = data_dir_path / "example_data_rev20242501.hdf5"
    holographic_stimulation_data = h5py.File(holographic_stimulation_file_path, "r")
    if epoch_name not in holographic_stimulation_data.keys():
        holographic_stimulation_file_path = None

    converter = Abdeladim2023NWBConverter(
        imaging_folder_path=imaging_folder_path,
        segmentation_folder_path=segmentation_folder_path,
        segmentation_to_imaging_map=segmentation_to_imaging_plane_map,
        segmentation_start_frame=segmentation_start_frame,
        segmentation_end_frame=segmentation_end_frame,
        holographic_stimulation_file_path=holographic_stimulation_file_path,
        epoch_name=epoch_name,
        verbose=False,
        stub_test=stub_test,
    )

    conversion_options = {
        interface_name: dict(stub_test=stub_test) for interface_name in converter.data_interface_objects.keys()
    }
    photon_series_index = 0
    for interface_name in converter.data_interface_objects.keys():
        if "Imaging" in interface_name:
            conversion_options[interface_name] = {"photon_series_index": photon_series_index}
            photon_series_index += 1

    # Add datetime to conversion
    metadata = converter.get_metadata()

    # Update default metadata with the editable in the corresponding yaml file
    editable_metadata_path = Path(__file__).parent / "abdeladim_2023_metadata.yaml"
    editable_metadata = load_dict_from_file(editable_metadata_path)
    metadata = dict_deep_update(metadata, editable_metadata)

    # Update metadata with the holographic stimulation data
    if "HolographicStimulation" in converter.data_interface_objects:
        holographic_stimulation_metadata_path = Path(__file__).parent / "abdeladim_2023_holostim_metadata.yaml"
        holographic_metadata = load_dict_from_file(holographic_stimulation_metadata_path)
        metadata = dict_deep_update(metadata, holographic_metadata)

    # Add the correct metadata for the session
    timezone = ZoneInfo("America/Los_Angeles")  # Time zone for Berkeley, California
    session_start_time = metadata["NWBFile"]["session_start_time"]
    metadata["NWBFile"].update(session_start_time=session_start_time.replace(tzinfo=timezone))
    metadata["Subject"].update(subject_id=subject_id)

    # Each epoch will be saved in a different nwb file but they will have the same session_id.
    session_id = f"{session_start_time.year}{session_start_time.month}{session_start_time.day}_{subject_id}"
    metadata["NWBFile"].update(session_id=session_id)

    nwbfile_path = output_dir_path / f"{session_id}_{epoch_name}.nwb"

    # Run conversion
    converter.run_conversion(
        metadata=metadata, nwbfile_path=nwbfile_path, conversion_options=conversion_options, overwrite=True
    )


if __name__ == "__main__":
    # Parameters for conversion
    root_path = Path(f"/media/amtra/Samsung_T5/CN_data")
    data_dir_path = root_path / "MouseV1-to-nwb"
    output_dir_path = root_path / "MouseV1-conversion_nwb/"
    stub_test = True  # for some reason does not work for iamging data

    subject_id = "w57_1"  # "w51_1", "w57_1"
    epoch_name = "3ori"

    epoch_names = ["2ret", "3ori", "4ori", "5stim", "6stim", "7expt"]
    try:
        epoch_index = epoch_names.index("3ori")
    except ValueError:
        print("'3ori' not found in the list of possible epoch_names.")

    segmentation_folder_path = data_dir_path / "processed-suite2p-data/suite2p/plane0"
    file_npy_path = segmentation_folder_path / "ops.npy"
    ops = np.load(file_npy_path, allow_pickle=True).item()
    frames_per_epoch = ops["frames_per_folder"]
    segmentation_start_frame = np.sum(frames_per_epoch[:epoch_index])
    segmentation_end_frame = segmentation_start_frame + frames_per_epoch[epoch_index]

    session_to_nwb(
        data_dir_path=data_dir_path,
        output_dir_path=output_dir_path,
        epoch_name=epoch_name,
        subject_id=subject_id,
        stub_test=stub_test,
        segmentation_start_frame=segmentation_start_frame,
        segmentation_end_frame=segmentation_end_frame,
    )
