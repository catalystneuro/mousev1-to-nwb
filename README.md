# mousev1-to-nwb
NWB conversion scripts for MouseV1 lab data to the [Neurodata Without Borders](https://nwb-overview.readthedocs.io/) data format.

## Installation from Github
We recommend that you install the package directly from Github. This option has the advantage that the source code can be modifed if you need to amend some of the code we originally provided to adapt to future experimental differences. To install the conversion from GitHub you will need to use `git` ([installation instructions](https://github.com/git-guides/install-git)). We also recommend the installation of `conda` ([installation instructions](https://docs.conda.io/en/latest/miniconda.html)) as it contains all the required machinery in a single and simple install

From a terminal (note that conda should install one in your system) you can do the following:

```
git clone https://github.com/catalystneuro/mousev1-to-nwb
cd mousev1-to-nwb
conda env create --file make_env.yml
conda activate mousev1_to_nwb_env
```

This creates a [conda environment](https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/environments.html) which isolates the conversion code from your system libraries.  We recommend that you run all your conversion related tasks and analysis from the created environment in order to minimize issues related to package dependencies.

Alternatively, if you want to avoid conda altogether (for example if you use another virtual environment tool) you can install the repository with the following commands using only pip:

```
git clone https://github.com/catalystneuro/mousev1-to-nwb
cd mousev1-to-nwb
pip install -e .
```

Note:
both of the methods above install the repository in [editable mode](https://pip.pypa.io/en/stable/cli/pip_install/#editable-installs).

## Running a specific conversion
To run a specific conversion, you might need to install first some conversion specific dependencies that are located in each conversion directory:
```
pip install -r src/mousev1_to_nwb/hendricks_2024/hendricks_2024_requirements.txt
```
Before running the conversion for a specific session you migth need to modify the metadata in the `hendricks_2024_metadata.yml` file .

You will also need to modify `hendricks_2024_conversion_script.py`: 

* Specify the data directory and the output directory for the nwb files
```python
root_path = Path("/media/amtra/Samsung_T5/CN_data")
data_dir_path = root_path / "MouseV1-to-nwb"
output_dir_path = root_path / "MouseV1-conversion_nwb/"

imaging_folder_path = data_dir_path / "raw-tiffs"
segmentation_folder_path = data_dir_path / "processed-suite2p-data/suite2p"
holographic_stimulation_file_path = data_dir_path / "example_data_rev20242501.hdf5"
visual_stimulus_file_path = data_dir_path / "example_data_rev20242501.hdf5"

```
* Specify the subject_id

```python
subject_id = "w57_1"
```

* Specify the epoch_names and add the experiment decription for each epoch

```python
epoch_names = ["2ret", "3ori", "4ori", "5stim", "6stim", "7expt"]
epoch_name_description_mapping = {  
    "2ret": "Retinotopy",
    "3ori": "Simple visual stimulation",
    "4ori": "Visual orientation tuning",
    "5stim": "Holographic stimulation of single cells and ensembles of co-tuned cells in primary visual cortex.",
    "6stim": "",
    "7expt": "Holographic stimulation of single cells and ensembles of co-tuned cells in primary visual cortex.",
}
```

* Map the field name of the visual stimulus data (as reported in the .hdf5 file) on the respective epoch name

```python
epoch_name_visual_stimulus_mapping = {
    "2ret": "vis_retinotopy_example",
    "3ori": "vis_simple_example",
    "4ori": "vis_orientation_tuning_example",
}
```

Eventually run the specific conversion with the following command:
```
python src/mousev1_to_nwb/hendricks_2024/hendricks_2024_conversion_script.py
```

## Repository structure
Each conversion is organized in a directory of its own in the `src` directory:

    mousev1-to-nwb/
    ├── LICENSE
    ├── make_env.yml
    ├── pyproject.toml
    ├── README.md
    ├── requirements.txt
    ├── setup.py
    └── src
        ├── mousev1_to_nwb
        │   ├── conversion_directory_1
        │   └── hendricks_2024
        │       ├── hendricks_2024_imagingextractor.py
        │       ├── hendricks_2024_imaginginterface.py
        │       ├── hendricks_2024_segmentationinterface.py
        │       ├── hendricks_2024_holostiminterface.py
        │       ├── hendricks_2024_visualstimulusinterface.py
        │       ├── hendricks_2024_nwbconverter.py
        │       ├── hendricks_2024_convert_session.py
        │       ├── hendricks_2024_metadata.yml
        │       ├── hendricks_2024_holostim_metadata.yml
        │       ├── hendricks_2024_requirements.txt
        │       ├── hendricks_2024_notes.md
        │       ├── hendricks_2024_conversion_script.py
        │       └── __init__.py

        └── __init__.py

 For example, for the conversion `hendricks_2024` you can find a directory located in `src/mousev1-to-nwb/hendricks_2024`. Inside each conversion directory you can find the following files:

* `hendricks_2024_conversion_script.py`: this script run the conversion of one full session (all epochs). Data directories, output directory, subject id and other information to run the conversion should be defined here.
* `hendricks_2024_convert_sesion.py`: this script defines the function to convert one full session of the conversion.
* `hendricks_2024_requirements.txt`: dependencies specific to this conversion.
* `hendricks_2024_metadata.yml`: metadata in yaml format for this specific conversion.
* `hendricks_2024_imagingextractor.py`: the extractor for the imaging data.
* `hendricks_2024_imaginginterface.py`: the interface for the imaging data.
* `hendricks_2024_segmentationinterface.py`: the interface for the segmentation data.
* `hendricks_2024_holostim_metadata.yml`: metadata in yaml format for holographic stimulus specs.
* `hendricks_2024_holostiminterface.py`: the interface for the holographic stimulus data.
* `hendricks_2024_visualstimulusinterface.py`: the interface for the visual stimulus data.
* `hendricks_2024_nwbconverter.py`: the place where the `NWBConverter` class is defined.
* `hendricks_2024_notes.md`: notes and comments concerning this specific conversion.

