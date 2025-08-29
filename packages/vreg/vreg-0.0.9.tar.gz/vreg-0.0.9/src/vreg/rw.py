import numpy as np

try:
    import nibabel as nib
except ImportError:
    nib_installed = False
else:
    nib_installed = True

try:
    import zarr
except ImportError:
    zarr_installed = False
else:
    zarr_installed = True

from vreg.vol import Volume3D


NIFTI_IMPORT_ERROR = (
    "Saving in NIfTI format requires the nibabel python package. You can "
    "install it with 'pip install nibabel', or else install vreg with the "
    "rw option as 'pip install vreg[rw]'."
)
ZARR_IMPORT_ERROR = (
    "Saving in zarray format requires the zarr python package. You can "
    "install it with 'pip install zarr', or else install vreg with the "
    "rw option as 'pip install vreg[rw]'."
)


def write_npz(vol:Volume3D, filepath:str):
    """Write a volume to a single file in numpy's uncompressed .npz file format

    Args:
        vol (Volume3D): the volume to write.
        filepath (str): filepath to the .npz file.
    """
    np.savez(filepath, values=vol.values, affine=vol.affine)


def read_npz(filepath:str):
    """Load a volume created by write_npz()

    Args:
        filepath (str): filepath to the .npz file.

    Returns:
        Volume3D: the volume read from file.
    """
    npz = np.load(filepath)
    if 'values' not in npz.files:
        raise ValueError("The .npz file has not been created by write_npz.")
    if 'affine' not in npz.files:
        raise ValueError("The .npz file has not been created by write_npz.")
    return Volume3D(npz['values'], npz['affine'])


def _affine_to_from_RAH(affine):
    # convert to/from nifti coordinate system
    rot_180 = np.identity(4, dtype=np.float32)
    rot_180[:2,:2] = [[-1,0],[0,-1]]
    return np.matmul(rot_180, affine)


# TODO: Build a LazyVolume3D()??
# vol = vreg.from_zarr(path)
# vol.values is a zarray
# read Volume3D with vol01 = vol[i0:i1]
# write Colume3D with vol[i0:i1] = vol01


def create_zarr(vol:Volume3D, **kwargs):
    """Write volume to disk in zarray format.

    Args:
        vol (Volume3D): the volume to write.
        kwargs (dict): Any keyword arguments accepted by zarr.create()

    Raises:
        ImportError: Error raised if zarr is not installed.

    Note:
        This requires a separate installation of the optional zarr package, 
        either via 'pip install zarr' or by installing vreg with the rw 
        option 'pip install vreg[rw]'.
    """
    if not zarr_installed:
        raise ImportError(ZARR_IMPORT_ERROR)
    zarray = zarr.create(**kwargs)
    zarray[:] = vol.values
    zarray.attrs['affine'] = vol.affine.tolist()
    if vol.coords is not None:
        zarray.attrs['coords'] = vol.coords.tolist()
        zarray.attrs['dims'] = vol.dims
    return zarray


def write_nifti(vol:Volume3D, filepath:str):
    """Write volume to disk in NIfTI format.

    Args:
        vol (Volume3D): the volume to write.
        filepath (str): filepath to the NIfTI file.

    Raises:
        ImportError: Error raised if nibabel is not installed.

    Note:
        This requires a separate installation of the optional nibabel package, 
        either via 'pip install nibabel' or by installing vreg with the rw 
        option 'pip install vreg[rw]'.

    Warning:
        For volumes with more than 3 dimensions, saving to nifti will 
        result in loss of information on the extra dimensions - 
        specifically their name and coordinates of the images. 
    """
    if not nib_installed:
        raise ImportError(NIFTI_IMPORT_ERROR)
    affine = _affine_to_from_RAH(vol.affine)
    nifti = nib.Nifti1Image(vol.values, affine)
    nib.save(nifti, filepath)


def read_nifti(filepath:str, coords:np.ndarray=None, 
               dims:list=None, prec:int=None):
    """Read volume from a NIfTI file on disk.

    Args:
        filepath (str): filepath to the NIfTI file.
        coords (np.ndarray): For values with dimensions more than 3, 
            provide an additional coordinate array for the locations 
            of the replicated volumes. If not provided, index arrays 
            are used for the coordinates of the extra dimensions.
        dims (list): Names of the extra dimensions for volumes with more 
            than 3 dimensions.
        prec (int): internal precision to be used when comparing positions. 
            If not provided, the exact floating point values of locations 
            are used. Defaults to None.

    Raises:
        ImportError: Error raised if nibabel is not installed.

    Returns:
        Volume3D: the volume read from file.

    Note:
        This requires a separate installation of the optional nibabel package, 
        either via 'pip install nibabel' or by installing vreg with the rw 
        option 'pip install vreg[rw]'.

    Warning:
        For volumes with more than 3 dimensions, coordinates and 
        dimensions need to be provided separately as nifti does not 
        store those.
    """
    if not nib_installed:
        raise ImportError(NIFTI_IMPORT_ERROR)
    img = nib.load(filepath)
    values = img.get_fdata()
    affine = _affine_to_from_RAH(img.affine)
    return Volume3D(values, affine, coords, dims, prec)
