from pathlib import Path
import numpy as np
from hendricks_2024_convert_session import session_to_nwb

# Specify the data directory and the output directory for the nwb files
root_path = Path("/media/amtra/Samsung_T5/CN_data")
data_dir_path = root_path / "MouseV1-to-nwb"
output_dir_path = root_path / "MouseV1-conversion_nwb/"

imaging_folder_path = data_dir_path / "raw-tiffs"
segmentation_folder_path = data_dir_path / "processed-suite2p-data/suite2p"
holographic_stimulation_file_path = data_dir_path / "example_data_rev20242501.hdf5"
visual_stimulus_file_path = None #data_dir_path / "example_data_rev20242501.hdf5"

# To test the conversion pipeline on a smaller portion of the dataset: stub_test = True
stub_test = False

# Specify the subject_id
subject_id = "w57_1"

# Specify the epoch_names and add the experiment decription for each epoch
epoch_names = ["2ret", "3ori", "4ori", "5stim", "6stim", "7expt"]
epoch_name_description_mapping = {  
    "2ret": "Retinotopy",
    "3ori": "Simple visual stimulation",
    "4ori": "Visual orientation tuning",
    "5stim": "Holographic stimulation of single cells and ensembles of co-tuned cells in primary visual cortex.",
    "6stim": "",
    "7expt": "Holographic stimulation of single cells and ensembles of co-tuned cells in primary visual cortex.",
}

# Map the field name of the visual stimulus data on the respective epoch name
epoch_name_visual_stimulus_mapping = {
    "2ret": "vis_retinotopy_example",
    "3ori": "vis_simple_example",
    "4ori": "vis_orientation_tuning_example",
}

for epoch_name in epoch_names:
    epoch_imaging_folder_path = imaging_folder_path / epoch_name

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
        imaging_folder_path=epoch_imaging_folder_path,
        segmentation_folder_path=segmentation_folder_path,
        visual_stimulus_file_path=visual_stimulus_file_path,
        epoch_name_visual_stimulus_mapping=epoch_name_visual_stimulus_mapping,
        holographic_stimulation_file_path=holographic_stimulation_file_path,
        segmentation_start_frame=segmentation_start_frame,
        segmentation_end_frame=segmentation_end_frame,
        epoch_name_description_mapping=epoch_name_description_mapping,
        stub_test=stub_test,
    )
