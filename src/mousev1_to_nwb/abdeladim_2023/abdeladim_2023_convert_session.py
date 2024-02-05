"""Primary script to run to convert an entire session for of data using the NWBConverter."""

from pathlib import Path
from typing import Union, Optional
import h5py
from zoneinfo import ZoneInfo
import numpy as np

from neuroconv.utils import load_dict_from_file, dict_deep_update

from abdeladim_2023nwbconverter import Abdeladim2023NWBConverter
from abdeladim_2023nwbconverter import get_default_segmentation_to_imaging_name_mapping


def session_to_nwb(
    epoch_name: str,
    subject_id: str,
    output_dir_path: Union[str, Path],
    imaging_folder_path: Union[str, Path],
    segmentation_folder_path: Optional[Union[str, Path]] = None,
    visual_stimulus_file_path: Optional[Union[str, Path]] = None,
    epoch_name_visual_stimulus_mapping: Optional[dict] = None,
    holographic_stimulation_file_path: Optional[Union[str, Path]] = None,
    segmentation_start_frame: Optional[int] = 0,
    segmentation_end_frame: Optional[int] = 100,
    epoch_name_description_mapping: Optional[dict] = None,
    stub_test: bool = False,
):
    conversion_options = dict()

    # Add Imaging
    imaging_folder_path = Path(imaging_folder_path)

    # Add Segmentation
    if segmentation_folder_path:
        segmentation_folder_path = Path(segmentation_folder_path)
        segmentation_to_imaging_plane_map = get_default_segmentation_to_imaging_name_mapping(
            imaging_folder_path, segmentation_folder_path
        )

    if holographic_stimulation_file_path:
        # Check if session has holographic photostimulation data
        holographic_stimulation_data = h5py.File(holographic_stimulation_file_path, "r")
        if epoch_name not in holographic_stimulation_data.keys():
            holographic_stimulation_file_path = None

    if visual_stimulus_file_path:
        if epoch_name_visual_stimulus_mapping is None:
            epoch_name_visual_stimulus_mapping = {
                "2ret": "vis_retinotopy_example",
                "3ori": "vis_simple_example",
                "4ori": "vis_orientation_tuning_example",
            }
        if epoch_name in epoch_name_visual_stimulus_mapping.keys():
            visual_stimulus_type = epoch_name_visual_stimulus_mapping[epoch_name]
        else:
            visual_stimulus_type = None

    converter = Abdeladim2023NWBConverter(
        imaging_folder_path=imaging_folder_path,
        segmentation_folder_path=segmentation_folder_path,
        segmentation_to_imaging_map=segmentation_to_imaging_plane_map,
        segmentation_start_frame=segmentation_start_frame,
        segmentation_end_frame=segmentation_end_frame,
        visual_stimulus_file_path=visual_stimulus_file_path,
        visual_stimulus_type=visual_stimulus_type,
        holographic_stimulation_file_path=holographic_stimulation_file_path,
        epoch_name=epoch_name,
        verbose=False,
    )

    photon_series_index = 0
    for interface_name in converter.data_interface_objects.keys():
        if "Imaging" in interface_name:
            conversion_options[interface_name] = {"stub_test": stub_test, "photon_series_index": photon_series_index}
            photon_series_index += 1
        if "Segmentation" in interface_name:
            conversion_options[interface_name] = {"stub_test": stub_test}

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
    metadata["NWBFile"].update(experiment_description=epoch_name_description_mapping.get(epoch_name))
    metadata["Subject"].update(subject_id=subject_id)

    # Each epoch will be saved in a different nwb file but they will have the same session_id.
    session_id = f"{session_start_time.year}{session_start_time.month}{session_start_time.day}_{subject_id}"
    metadata["NWBFile"].update(session_id=session_id)

    output_dir_path = Path(output_dir_path)
    if stub_test:
        output_dir_path = output_dir_path / f"nwb_stub/{session_id}"
    else:
        output_dir_path = output_dir_path / f"{session_id}"
    output_dir_path.mkdir(parents=True, exist_ok=True)
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
    stub_test = True

    subject_id = "w57_1"
    epoch_names = ["2ret", "3ori", "4ori", "5stim", "6stim", "7expt"]
    epoch_name_description_mapping = {  # TODO add more extensive experiment description
        "2ret": "Retinotopy",
        "3ori": "Simple visual stimulation",
        "4ori": "Visual orientation tuning",
        "5stim": "Holographic stimulation of single cells and ensembles of co-tuned cells in primary visual cortex.",
        "6stim": "",
        "7expt": "Holographic stimulation of single cells and ensembles of co-tuned cells in primary visual cortex.",
    }

    segmentation_folder_path = data_dir_path / "processed-suite2p-data/suite2p"

    holographic_stimulation_file_path = data_dir_path / "example_data_rev20242501.hdf5"

    visual_stimulus_file_path = data_dir_path / "example_data_rev20242501.hdf5"
    epoch_name_visual_stimulus_mapping = {
        "2ret": "vis_retinotopy_example",
        "3ori": "vis_simple_example",
        "4ori": "vis_orientation_tuning_example",
    }

    for epoch_name in epoch_names:
        imaging_folder_path = data_dir_path / "raw-tiffs" / epoch_name

        file_npy_path = segmentation_folder_path / "plane0/ops.npy"
        ops = np.load(file_npy_path, allow_pickle=True).item()
        frames_per_epoch = ops["frames_per_folder"]
        epoch_index = epoch_names.index(epoch_name)

        segmentation_start_frame = np.sum(frames_per_epoch[:epoch_index])
        segmentation_end_frame = segmentation_start_frame + frames_per_epoch[epoch_index]

        session_to_nwb(
            epoch_name=epoch_name,
            subject_id=subject_id,
            output_dir_path=output_dir_path,
            imaging_folder_path=imaging_folder_path,
            segmentation_folder_path=segmentation_folder_path,
            visual_stimulus_file_path=visual_stimulus_file_path,
            epoch_name_visual_stimulus_mapping=epoch_name_visual_stimulus_mapping,
            holographic_stimulation_file_path=holographic_stimulation_file_path,
            segmentation_start_frame=segmentation_start_frame,
            segmentation_end_frame=segmentation_end_frame,
            epoch_name_description_mapping=epoch_name_description_mapping,
            stub_test=stub_test,
        )
