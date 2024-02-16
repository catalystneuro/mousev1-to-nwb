# Notes concerning the hendricks_2024 conversion


# Reference papers
* [Probing inter-areal computations with a cellular resolution two-photon holographic mesoscope](https://www.biorxiv.org/content/10.1101/2023.03.02.530875v2.full)
* [The logic of recurrent circuits in the primary visual cortex](https://www.biorxiv.org/content/10.1101/2022.09.20.508739v1.full)
* [All-optical recreation of naturalistic neural activity with a multifunctional transgenic reporter mouse](https://www.sciencedirect.com/science/article/pii/S2211124723009208)

## Experimental protocol:

The microscope is calibrated to aim holograms/optogenetic stimulation to pixel coordinates in ScanImage. 
After motion correcting and processing the data with suite2p, they extract cell masks and traces. 
Then (x,y) pixel targeted locations are matched to (x,y) suite2p locations using a simple distance matching algorithm (with a maximum distance threshold). 
For various reasons, suite2p will not always detect a cell in the location where hologram shoul be. 
To preserve indexing, those are marked as NaN.

## Data streams:

- imaging data (ScanImage),
- segmentation (Suite2P), 
- holographic stimulation (Custom Matlab code, HDF5 file)
- event annotations: visual stimuli (Custom Matlab code, HDF5 file)

### Data exploraton:
The example data shared is structured as follow:
- imaging data --> "raw_tiffs" folder containing a folder for each session: "2ret","3ori","4ori","5stim","6stim","7expt"
- suite2p data --> "processed-suite2p-data"
- holographic stimulation -->  processed "example_data_rev20242501.hdf5" file
- visual stimulus -->  processed "example_data_rev20242501.hdf5" file

#### Imaging data (ScanImage):
- each session has multiple .tif files to be concatenated in time --> use MultiImageExtractor
- image dimension: 
    - n_xpixels: 512 `'SI.hRoiManager.pixelsPerLine'`
    - n_ypixels: 512 `'SI.hRoiManager.linesPerFrame'`
- number of planes: 3   `'SI.hStackManager.numSlices'`
- two channel: "Channel 1"--> Green, "Channel 2" --> Red 
    - `SI.hChannels.channelMergeColor : {'green';'red';'red';'red'}`
    - `SI.hChannels.channelName : {'Channel 1' 'Channel 2' 'Channel 3' 'Channel 4'}`
    - `SI.hChannels.channelSave : [1;2]`
- round-robin acquisition at: 19.0686 `SI.hRoiManager.scanFrameRate`
- plane acquisition rate at: 6.35621 `SI.hRoiManager.scanVolumeRate`
- line acquisition rate at:  1/6.31833e-05 `SI.hRoiManager.linePeriod`
- grid_spacing: [13.5, 13.5] (`"sizeXY"`)/ [512, 512] (`"pixelResolutionXY"`)   
- origin_coords: [-1.776356839e-16, 0.1] `"centerXY"`
---------------------------
#### Segmentation data (Suite2P),
- Suit2p data has 41305 frames for each Plane (`'frames_per_folder'`: [ 9604,  6203,  6394,  1708,  3527, 13869])
The Suit2p processing is done by concatenating the different epochs, we separate them using `'frames_per_folder'` indication. 
---------------------------
#### Holographic stimulation data (custom):
Only "5stim" and "7expt" epochs contains holographic stimulation.
Each trial correspond to a multipage .tif file.
from the README provided in the data folder:
**Variables and nomenclature**
`scanimage_hologram_list` = list of unique stimulations/holograms that is indexed by `stim_id`
`targeted_cells` = overally list of all suite2p cells targeted and matched to holographic stimuli
`stim_times` = stimulation time (in seconds) within a trial for each roi, NaN means the cell was not stimulated
`stim_id` = trialwise index into `hologram_list`, note this is idx-1, as the first "stim" condition is a control trial
`roi_powers_mW` = power per cell/stimulation site in mW
`spikes_per_cell` = stim frequency per cell/stimulation site 
`hz_per_cell` = stimulation frequency per cell/stimulation site
`scanimage_targets` = (X,Y,Z) locations of holograms in pixels, taken from scan image ROIs
`suite2p_targets` = (X,Y,Z) locations of holograms in pixels, taken from suite2p median locations for each ROI

---------------------------
#### Visual stimulus data (custom):
Only "2ret" "3ori"  and "4ori" epochs contains visual stimulus events.

**Variables and nomenclature**
* **`vis_simple_example`** 
    `vis_ids`: unique indexes for each unique visual stimulus presented (1d array of length n trials)
    `vis_times`: a 2xn array of length n trials, representing (vis_on, vis_off) in seconds from the beginning of each trial
* **`vis_orientation_example`**
    `vis_ids`: unique indexes for each unique visual stimulus presented (1d array of length n trials)
    `vis_times`: a 2xn array of length n trials, representing (vis_on, vis_off) in seconds from the beginning of each trial
    `orientation`: orientation of drifting grating in degrees (0-360), 1d of length n trials
    `size_vdeg`: size of stimulus in visual degrees, 1d of length n trials
    `contrast`: contrast of gratings, float between 0-1, 1d of length n trials
    *not included in this example* `location`: (X,Y) location on screen in visual degrees, you can just use (0,0) (represents the center of the screen)
* **`vis_retinotopy_example`**
    `vis_times`: a 2xn array of length n trials, representing (vis_on, vis_off) in seconds from the beginning of each trial
    `locations`: trial wise (X,Y) locations of stimulus on screen in visual degrees
    `size_vdeg`: size of stimulus in visual degrees, 1d of length n trials
    `contrast`: contrast of gratings, float between 0-1, 1d of length n trials
    
## Lab code:
[willyh101/analysis](https://github.com/willyh101/analysis/tree/5bd562ca531a6cc9ce9a57ed76229d89a8fcb82d)
[adesnik-lab/holography](https://github.com/adesnik-lab/holography/tree/main)

