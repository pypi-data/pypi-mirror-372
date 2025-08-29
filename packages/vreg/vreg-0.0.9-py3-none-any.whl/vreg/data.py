import os
import sys
import pickle
import requests

from vreg import vol, rw

# filepaths need to be identified with importlib_resources
# rather than __file__ as the latter does not work at runtime
# when the package is installed via pip install

if sys.version_info < (3, 9):
    # importlib.resources either doesn't exist or lacks the files()
    # function, so use the PyPI version:
    import importlib_resources
else:
    # importlib.resources has files(), so use that:
    import importlib.resources as importlib_resources



DATASETS = [
    'Dixon_fat',
    'Dixon_water',
    'Dixon_in_phase',
    'Dixon_out_phase',
    'kidneys',
    'left_kidney',
    'right_kidney',
    'MTR',
    'T1_00',
    'T1_01',
    'T1_02',
    'T1_03',
    'T1_04',
    'T2star_00',
    'T2star_01',
    'T2star_02',
    'T2star_03',
    'T2star_04',
]


def fetch(dataset=None, clear_cache=False, download_all=False) -> vol.Volume3D:
    """Fetch a dataset included in vreg.

    The source data are on `Zenodo <https://doi.org/10.5281/zenodo.14630318>`_

    Args:
        dataset (str, optional): name of the dataset. See below for options.
        clear_cache (bool, optional): When a dataset is fetched, it is 
          downloaded and then stored in a local cache memory for faster access 
          next time it is fetched. Set clear_cache=True to delete all data 
          in the cache memory. Default is False.
        download_all (bool, optional): By default only the dataset that is 
          fetched is downloaded. Set download_all=True to download all 
          datasets at once. This will cost some time but then offers fast and 
          offline access to all datasets afterwards. This will take up around 
          300 MB of space on your hard drive. Default is False.

    Returns:
        Volume3D or list: Data as a vreg.Volume3D (for 3D scans) or a list of 
        Volume3D objects (for 2D multislice scans).

    Example:
        Fetch the kidneys mask and the T1-map, and display as overlay:

    .. pyvista-plot::
        :include-source:
        :context: 
        :force_static:

        >>> import vreg
        >>> import vreg.plot as plt

        Get the data:

        >>> kidneys = vreg.fetch('kidneys')
        >>> T1 = vreg.fetch('T1')

        Plot as overlays:

        >>> plt.overlay_2d(T1, kidneys)

    """

    if dataset is None:
        v = None
    elif dataset in ['T1', 'T2star']:
        v = [_fetch_dataset(f'{dataset}_{str(i).zfill(2)}') for i in range(5)]
    else:
        v = _fetch_dataset(dataset)

    if clear_cache:
        _clear_cache()

    if download_all:
        for d in DATASETS:
            _download(d)

    return v



def _clear_cache():
    """
    Clear the folder where the data downloaded via fetch are saved.

    Note if you clear the cache the data will need to be downloaded again 
    if you need them.
    """
    # TODO: This also deletes __init__.py
    f = importlib_resources.files('vreg.datafiles')
    for item in f.iterdir(): 
        if item.is_file(): 
            if str(item)[-11:] != '__init__.py':
                item.unlink() # Delete the file


def _fetch_dataset(dataset):

    f = importlib_resources.files('vreg.datafiles')
    datafile = str(f.joinpath(dataset + '.nii'))

    # If this is the first time the data are accessed, download them.
    if not os.path.exists(datafile):
        _download(dataset)

    return rw.read_nifti(datafile)


def _download(dataset):
        
    f = importlib_resources.files('vreg.datafiles')
    datafile = str(f.joinpath(dataset + '.nii'))

    if os.path.exists(datafile):
        return

    # Dataset location
    version_doi = "15535700" # This will change if a new version is created on zenodo
    file_url = "https://zenodo.org/records/" + version_doi + "/files/" + dataset + ".nii"

    # Make the request and check for connection error
    try:
        file_response = requests.get(file_url) 
    except requests.exceptions.ConnectionError as err:
        raise requests.exceptions.ConnectionError(
            "\n\n"
            "A connection error occurred trying to download the test data \n"
            "from Zenodo. This usually happens if you are offline. The \n"
            "first time a dataset is fetched via vreg.fetch you need to \n"
            "be online so the data can be downloaded. After the first \n"
            "time they are saved locally so afterwards you can fetch \n"
            "them even if you are offline. \n\n"
            "The detailed error message is here: " + str(err)) 
    
    # Check for other errors
    file_response.raise_for_status()

    # Save the file locally 
    with open(datafile, 'wb') as f:
        f.write(file_response.content)