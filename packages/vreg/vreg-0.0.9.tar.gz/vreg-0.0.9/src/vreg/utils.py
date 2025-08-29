import numpy as np
import scipy.ndimage as ndi

from scipy.spatial.transform import Rotation
from scipy.interpolate import griddata 

def affine_resolution(shape, spacing):
    """Smallest detectable rotation, translation and stretching of a volume with given shape and resolution."""

    translation_res = spacing
    # Geometry-based rotation resolution needs some more thinking - this produces too small values
    # rot_res_x = min([spacing[1],spacing[2]])/max([shape[1],shape[2]])
    # rot_res_y = min([spacing[2],spacing[0]])/max([shape[2],shape[0]])
    # rot_res_z = min([spacing[0],spacing[1]])/max([shape[0],shape[1]])
    # rot_res = np.array([rot_res_x, rot_res_y, rot_res_z])
    rot_res = np.array([np.pi/180, np.pi/180, np.pi/180])
    scaling_res = np.array([0.01, 0.01, 0.01])
    return rot_res, translation_res, scaling_res


def volume_coordinates(shape, position=[0,0,0]):

    # data are defined at the middle of the voxels - use p+0.5 offset.
    xo, yo, zo = np.meshgrid(
        np.arange(position[0]+0.5, position[0]+0.5+shape[0]),
        np.arange(position[1]+0.5, position[1]+0.5+shape[1]),
        np.arange(position[2]+0.5, position[2]+0.5+shape[2]),
        indexing = 'ij')
    return np.column_stack((xo.ravel(), yo.ravel(), zo.ravel()))


def fill_gaps(data, loc, mask=None):
    # Fill gaps in data by interpolation
    # data is an array with values
    # loc is a mask array defining where to interpolate (0=interpolate, 1=value)
    # mask is a mask array to restrict the interpolation to certain regions.

    x, y, z = np.indices(data.shape)

    # Get locations and values of non-zero pixels
    i = loc>0.5
    if mask is not None:
        i = i & (mask==1)
    points = np.column_stack([x[i], y[i], z[i]])
    values = data[i]

    # Interpolate using griddata
    k = loc<0.5
    if mask is not None:
        k = k & (mask==1)
    filled = data.copy()
    filled[k] = griddata(points, values, (x[k], y[k], z[k]), method='linear', fill_value=0)

    if mask is not None:
        filled *= mask

    return filled


def rotation_displacement(rotation, center):

    rot = Rotation.from_rotvec(rotation)
    center_rot = rot.apply(center)
    return center_rot-center


def envelope(d, affine, decimals=None):

    corners, _ = parallellepid(np.array(d), affine)

    x0 = np.amin(corners[:,0])
    x1 = np.amax(corners[:,0])
    y0 = np.amin(corners[:,1])
    y1 = np.amax(corners[:,1])
    z0 = np.amin(corners[:,2])
    z1 = np.amax(corners[:,2])

    dx = x1-x0
    dy = y1-y0
    dz = z1-z0
    if decimals is not None:
        dx = np.round(dx, decimals)
        dy = np.round(dy, decimals)
        dz = np.round(dz, decimals)
    nx = np.ceil(dx).astype(np.int16)
    ny = np.ceil(dy).astype(np.int16)
    nz = np.ceil(dz).astype(np.int16)

    output_shape = (nx, ny, nz)
    output_pos = [x0, y0, z0]

    return output_shape, output_pos

def bounding_box_geom(array:np.ndarray, affine:np.ndarray, margin:float=0)->tuple:

    pixel_spacing = np.linalg.norm(affine[:3, :3], axis=0)
    xmargin = np.around(margin/pixel_spacing[0]).astype(np.int16)
    ymargin = np.around(margin/pixel_spacing[1]).astype(np.int16)
    zmargin = np.around(margin/pixel_spacing[2]).astype(np.int16)

    # Find shape and location of the box in array coordinates and get array.
    x, y, z = np.where(array != 0)
    x0, x1 = np.amin(x)-xmargin, np.amax(x)+xmargin
    y0, y1 = np.amin(y)-ymargin, np.amax(y)+ymargin
    z0, z1 = np.amin(z)-zmargin, np.amax(z)+zmargin
    x0, x1 = np.amax([0, x0]), np.amin([x1, array.shape[0]-1])
    y0, y1 = np.amax([0, y0]), np.amin([y1, array.shape[1]-1])
    z0, z1 = np.amax([0, z0]), np.amin([z1, array.shape[2]-1])
    nx = 1 + np.ceil(x1-x0).astype(np.int16)
    ny = 1 + np.ceil(y1-y0).astype(np.int16)
    nz = 1 + np.ceil(z1-z0).astype(np.int16)
    return x0, y0, z0, nx, ny, nz

def bounding_box_apply(array, affine, x0, y0, z0, nx, ny, nz):

    box_array = array[x0:x0+nx, y0:y0+ny, z0:z0+nz]

    # Get the corner in absolute coordinates and offset the affine.
    nd = 3
    matrix = affine[:nd,:nd]
    offset = affine[:nd, nd]
    r0 = np.array([x0,y0,z0])
    r0 = np.dot(r0, matrix.T) + offset
    box_affine = affine.copy()
    box_affine[:nd, nd] = r0

    return box_array, box_affine


def bounding_box(array:np.ndarray, affine:np.ndarray, margin:float=0)->tuple:

    # pixel_spacing = np.linalg.norm(affine[:3, :3], axis=0)
    # xmargin = np.around(margin/pixel_spacing[0]).astype(np.int16)
    # ymargin = np.around(margin/pixel_spacing[1]).astype(np.int16)
    # zmargin = np.around(margin/pixel_spacing[2]).astype(np.int16)

    # # Find shape and location of the box in array coordinates and get array.
    # x, y, z = np.where(array != 0)
    # x0, x1 = np.amin(x)-xmargin, np.amax(x)+xmargin
    # y0, y1 = np.amin(y)-ymargin, np.amax(y)+ymargin
    # z0, z1 = np.amin(z)-zmargin, np.amax(z)+zmargin
    # x0, x1 = np.amax([0, x0]), np.amin([x1, array.shape[0]-1])
    # y0, y1 = np.amax([0, y0]), np.amin([y1, array.shape[1]-1])
    # z0, z1 = np.amax([0, z0]), np.amin([z1, array.shape[2]-1])
    # nx = 1 + np.ceil(x1-x0).astype(np.int16)
    # ny = 1 + np.ceil(y1-y0).astype(np.int16)
    # nz = 1 + np.ceil(z1-z0).astype(np.int16)

    x0, y0, z0, nx, ny, nz = bounding_box_geom(array, affine, margin)
    return bounding_box_apply(array, affine, x0, y0, z0, nx, ny, nz)
    # box_array = array[x0:x0+nx, y0:y0+ny, z0:z0+nz]

    # # Get the corner in absolute coordinates and offset the affine.
    # nd = 3
    # matrix = affine[:nd,:nd]
    # offset = affine[:nd, nd]
    # r0 = np.array([x0,y0,z0])
    # r0 = np.dot(r0, matrix.T) + offset
    # box_affine = affine.copy()
    # box_affine[:nd, nd] = r0

    # return box_array, box_affine


def affine_output_geometry(input_shape, input_affine, transformation):
        
    # Determine output shape and position
    affine_transformed = transformation.dot(input_affine)
    forward = np.linalg.inv(input_affine).dot(affine_transformed) # Ai T A
    output_shape, output_pos = envelope(input_shape, forward, decimals=6)

    # Determine output affine by shifting affine to the output position
    nd = input_affine.shape[0]-1
    matrix = input_affine[:nd,:nd]
    offset = input_affine[:nd, nd]
    output_affine = input_affine.copy()
    output_affine[:nd, nd] = np.dot(matrix, output_pos) + offset

    return output_shape, output_affine


def multislice_to_singleslice_affine(affine_ms, slice_thickness):
    # In a multi-slice affine, the z-spacing is the slice spacing (distance between slice centers)
    # In a single-slice affine, the z-spacing is the slice thickness
    affine_ss = affine_ms.copy()
    affine_ss[:3,2] *= slice_thickness/np.linalg.norm(affine_ss[:3,2])
    return affine_ss

def affine_slice(affine, z, slice_thickness=None):
    # Get the slice and its affine
    affine_z = affine.copy()
    affine_z[:3,3] += z*affine[:3,2]
    # Set the slice spacing to equal the slice thickness.
    # Note: both are equal for 3D array but different for 2D multislice
    # This caters for the convention in dbdicom and should become obsolete
    if slice_thickness is not None:
        slice_spacing = np.linalg.norm(affine[:3,2])
        if np.isscalar(slice_thickness):
            affine_z[:3,2] *= slice_thickness/slice_spacing
        else:
            affine_z[:3,2] *= slice_thickness[z]/slice_spacing
    return affine_z


def extract_slice(array, affine, z, slice_thickness=None):
    array_z = array[:,:,z]
    affine_z = affine_slice(affine, z, slice_thickness=slice_thickness)
    return array_z, affine_z

def center_of_mass(volume, affine, coords='fixed'):

    com = ndi.center_of_mass(volume)
    if isinstance(coords, str):
        if coords == 'volume':
            return com
        if coords == 'fixed':
            return vol2fix(com, affine)
    else:
        return vol2vol(com, affine, coords)

    # nd = volume.ndim
    # matrix = affine[:nd,:nd]
    # offset = affine[:nd, nd]
    # return np.dot(matrix, com) + offset

def vol2vol(vec, affine_in, affine_out):
    affine = np.linalg.inv(affine_out).dot(affine_in)
    matrix = affine[:3,:3]
    offset = affine[:3, 3]
    return np.dot(matrix, vec) + offset
    # vec = vol2fix(vec, affine_in)
    # vec = fix2vol(vec, affine_out)
    # return vec

def vol2fix(vec, affine):
    matrix = affine[:3,:3]
    offset = affine[:3, 3]
    return np.dot(matrix, vec) + offset

def fix2vol(vec, affine):
    affine = np.linalg.inv(affine)
    matrix = affine[:3,:3]
    offset = affine[:3, 3]
    return np.dot(matrix, vec) + offset

def volume_vector(vec, affine):
    row_cosine = affine[:3,0]/np.linalg.norm(affine[:3,0])
    column_cosine = affine[:3,1]/np.linalg.norm(affine[:3,1])
    slice_cosine = affine[:3,2]/np.linalg.norm(affine[:3,2])
    # Replaced as incorrect for stretched volume?
    # slice_cosine = np.cross(row_cosine, column_cosine)
    return vec[0]*row_cosine + vec[1]*column_cosine + vec[2]*slice_cosine

def inslice_vector(vec, affine):
    row_cosine = affine[:3,0]/np.linalg.norm(affine[:3,0])
    column_cosine = affine[:3,1]/np.linalg.norm(affine[:3,1])
    return vec[0]*row_cosine + vec[1]*column_cosine

def through_slice_vector(vec, affine):
    # Replaced as incorrect for stretched volume?
    # row_cosine = affine[:3,0]/np.linalg.norm(affine[:3,0])
    # column_cosine = affine[:3,1]/np.linalg.norm(affine[:3,1])
    # slice_cosine = np.cross(row_cosine, column_cosine)
    slice_cosine = affine[:3,2]/np.linalg.norm(affine[:3,2])
    if np.isscalar(vec):
        return vec*slice_cosine
    else:
        return vec[0]*slice_cosine


def to_3d(array):
    # Ensures that the data are 3D
    # Obsolete as Volume3D enforces 3D
    if array.ndim == 2: 
        return np.expand_dims(array, axis=-1)
    else:
        return array
    

def make_affine(orient='axial', rotation=None, center=None, spacing=1.0, 
                pos=[0,0,0]):

    # Check data types
    if orient not in ['axial','coronal','sagittal', 'xy', 'yz', 'zx']:
        raise ValueError(
            str(orient) + " is not a valid orientation. Possible "
            "orientations are 'axial', 'coronal' and 'sagittal', "
            "or also 'xy', 'yz' and 'zx'. ")

    if rotation is not None:
        rotation = np.array(rotation)
        if rotation.size != 3:
            raise ValueError("rotation must be a 3-element array.")
        
    if center is not None:
        center = np.array(center)
        if center.size != 3:
            raise ValueError("center must be a 3-element array.")
        
    if np.isscalar(spacing):
        spacing = 3*[spacing]
    spacing = np.array(spacing)
    if spacing.size != 3:
        raise ValueError("spacing must be a 3-element array.")
    
    # Set up default orientation
    if orient in ['axial', 'xy']:
        affine = np.array([[1, 0, 0, 0],
                           [0, 1, 0, 0],
                           [0, 0, 1, 0],
                           [0, 0, 0, 1]], dtype=np.float32)
    elif orient in ['sagittal', 'yz']:
        affine = np.array([[ 0, 0, 1, 0],
                           [-1, 0, 0, 0],
                           [ 0,-1, 0, 0],
                           [ 0, 0, 0, 1]], dtype=np.float32)
    elif orient == 'coronal':
        affine = np.array([[1, 0, 0, 0],
                           [0, 0,-1, 0],
                           [0,-1, 0, 0],
                           [0, 0, 0, 1]], dtype=np.float32)
    elif orient == 'zx':
        affine = np.array([[1, 0, 0, 0],
                           [0, 0, 1, 0],
                           [0,-1, 0, 0],
                           [0, 0, 0, 1]], dtype=np.float32)
        
    # Add spacing
    for i in [0,1,2]:
        affine[:,i] *= spacing[i]

    # Rotate default orientation
    if rotation is not None:  
        transfo = affine_matrix(rotation=rotation, center=center) 
        affine = transfo.dot(affine)
  
    # Shift
    affine[:3,3] = np.array(pos)

    return affine
    

def affine_matrix(rotation=None, translation=None, pixel_spacing=None, center=None):

    if np.isscalar(pixel_spacing):
        pixel_spacing = 3*[pixel_spacing]

    nd = 3
    matrix = np.eye(1+nd)

    if rotation is not None:
        rot = Rotation.from_rotvec(rotation)
        matrix[:nd,:nd] = rot.as_matrix()

        # Shift to rotate around center
        if center is not None:
            center_rot = rot.apply(center)
            offset = center_rot-center
            matrix[:nd, nd] -= offset

    if translation is not None:
        matrix[:nd, nd] += translation

    if pixel_spacing is not None:
        for c in range(nd):
            matrix[:nd, c] *= pixel_spacing[c]

    return matrix


def affine_components(matrix):
    """Extract rotation, translation and pixel spacing vector from affine matrix"""

    nd = matrix.shape[0]-1
    translation = matrix[:nd, nd].copy()
    rotation_matrix = matrix[:nd, :nd].copy()
    pixel_spacing = np.linalg.norm(matrix[:nd, :nd], axis=0)
    for c in range(nd):
        rotation_matrix[:nd, c] /= pixel_spacing[c]
    rot = Rotation.from_matrix(rotation_matrix)
    rotation = rot.as_rotvec()
    return rotation, translation, pixel_spacing


def surface_coordinates(shape):

    # data are defined at the edge of volume - extend shape with 1.
    xo, yo, zo = np.meshgrid(
        np.arange(1.0 + shape[0]),
        np.arange(1.0 + shape[1]),
        np.arange(1.0 + shape[2]),
        indexing = 'ij')
    return np.column_stack((xo.ravel(), yo.ravel(), zo.ravel()))


def extend_border(r, shape):

    # Shift with half a voxel because data are defined at voxel centers
    r -= 0.5

    # Set coordinates at 0.5 pixel from the borders equal to the borders
    x0, x1 = 0, shape[0]-1
    y0, y1 = 0, shape[1]-1
    z0, z1 = 0, shape[2]-1

    r[np.where(np.logical_and(x0-0.5 <= r[:,0], r[:,0] <= x0)), 0] = x0
    r[np.where(np.logical_and(x1+0.5 >= r[:,0], r[:,0] >= x1)), 0] = x1
    r[np.where(np.logical_and(y0-0.5 <= r[:,1], r[:,1] <= y0)), 1] = y0
    r[np.where(np.logical_and(y1+0.5 >= r[:,1], r[:,1] >= y1)), 1] = y1
    r[np.where(np.logical_and(z0-0.5 <= r[:,2], r[:,2] <= z0)), 2] = z0
    r[np.where(np.logical_and(z1+0.5 >= r[:,2], r[:,2] >= z1)), 2] = z1

    return r


def parallellepid(L, affine=None):

    c = np.array([0,0,0])
    x = np.array([1,0,0])*L[0]
    y = np.array([0,1,0])*L[1]
    z = np.array([0,0,1])*L[2]

    # mesh points
    vertices = np.array(
        [   c, 
            c+x, 
            c+x+z, 
            c+z, 
            c+y, 
            c+y+x, 
            c+y+x+z, 
            c+y+z,
        ]
    )
    
    if affine is not None:
        nd = 3
        matrix = affine[:nd,:nd]
        offset = affine[:nd, nd]
        vertices = np.dot(vertices, matrix.T) + offset

    # mesh faces
    faces = np.hstack(
        [
            [4, 0, 1, 2, 3], #right
            [4, 4, 5, 6, 7], #left
            [4, 0, 1, 5, 4], #bottom
            [4, 2, 3, 7, 6], #top
            [4, 0, 3, 7, 4], #front
            [4, 1, 2, 6, 5], #back
        ]
    )

    return vertices, faces