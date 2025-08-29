import numpy as np
import scipy.ndimage as ndi
from scipy.interpolate import interpn

import vreg.utils
import vreg.mod_affine


def freeform(input_data, input_affine, output_shape, output_affine, parameters, **kwargs):
    # Since parameters is a flat array, we need to find the number of nodes
    nodes = 2
    shape = deformation_field_shape(output_shape, nodes)
    while np.prod(shape) != np.size(parameters):
        nodes += 1
        shape = deformation_field_shape(output_shape, nodes)
    # Reshape parameters
    deformation_field = np.reshape(parameters, shape)
    # Get o2i transformation
    output_to_input = np.linalg.inv(input_affine).dot(output_affine)
    # Perform freeform deformation
    return freeform_deformation(input_data, deformation_field, output_shape, output_to_input, **kwargs)

def freeform_align(input_data, input_affine, output_shape, output_affine, parameters, **kwargs):
    output_to_input = np.linalg.inv(input_affine).dot(output_affine)
    return freeform_deformation_align(input_data, parameters, output_shape, output_to_input, **kwargs)



# Note: to apply to a window, adjust output_shape and output_affine (position vector)
# Deformation defined in input coordinates
def freeform_deformation(input_data, displacement, output_shape=None, output_to_input=np.eye(4), output_coordinates=None, **kwargs):
    #Freeform deformation assuming deformation field is defined in the reference frame of input data

     # Set defaults
    # If 2d array, add a 3d dimension of size 1
    if input_data.ndim == 2: 
        input_data = np.expand_dims(input_data, axis=-1)
    if output_shape is None:
        output_shape = input_data.shape
    else:
        output_shape = tuple(output_shape)

    # Create an array of all coordinates in the output volume
    # Optional argument as this can be precomputed for registration purposes
    if output_coordinates is None:
        # Creat output coordinates
        output_coordinates = vreg.utils.volume_coordinates(output_shape)
        # Express output coordinates in reference frame of the input volume
        output_coordinates = vreg.mod_affine.apply_affine(output_to_input, output_coordinates)
        
    # Apply free-from deformation to all output coordinates
    deformation = interpolate_displacement(displacement, output_shape, order=1)
    
    input_coordinates = output_coordinates + deformation

    # Extend with constant value for half a voxel outside of the boundary
    # TODO make this an option in 3D - costs time and is not necessary when a window is taken inside the FOV (better way to deal with borders)
    input_coordinates = vreg.utils.extend_border(input_coordinates, input_data.shape)

    # Interpolate the input data in the transformed coordinates
    output_data = ndi.map_coordinates(input_data, input_coordinates.T, order=1, **kwargs)
    output_data = np.reshape(output_data, output_shape)

    return output_data



# Note: to apply to a window, adjust output_shape and output_affine (position vector)
# Deformation defined in input coordinates
def freeform_deformation_align(input_data, displacement, output_shape=None, output_to_input=np.eye(4), output_coordinates=None, interpolator=None, **kwargs):
    #Freeform deformation with precomputing options optimized for use in coregistration

    # Set defaults
    # If 2d array, add a 3d dimension of size 1
    if input_data.ndim == 2: 
        input_data = np.expand_dims(input_data, axis=-1)
    if output_shape is None:
        output_shape = input_data.shape
    else:
        output_shape = tuple(output_shape)

    # Create an array of all coordinates in the output volume
    # Optional argument as this can be precomputed for registration purposes
    if output_coordinates is None:
        # Creat output coordinates
        output_coordinates = vreg.utils.volume_coordinates(output_shape)
        # Express output coordinates in reference frame of the input volume
        output_coordinates = vreg.mod_affine.apply_affine(output_to_input, output_coordinates)

    if interpolator is None:
        interpolator = freeform_interpolator(displacement.shape, output_shape, order=1)
        
    # Apply free-from deformation to all output coordinates
    deformation = interpolator_displacement(displacement, output_shape, interpolator)
    
    input_coordinates = output_coordinates + deformation

    # Extend with constant value for half a voxel outside of the boundary
    # TODO make this an option in 3D - costs time and is not necessary when a window is taken inside the FOV (better way to deal with borders)
    input_coordinates = vreg.utils.extend_border(input_coordinates, input_data.shape)

    # Interpolate the input data in the transformed coordinates
    output_data = ndi.map_coordinates(input_data, input_coordinates.T, order=1)
    
    output_data = np.reshape(output_data, output_shape)

    #print('Interpolate displacement', t1)
    #print('Map coordinates', t2)
    #print('Interp1/interp2', t1/t2)

    return output_data





# # Deformation define in absolute coordinates
# def absolute_freeform(input_data, input_affine, output_shape, output_affine, displacement, output_coordinates=None, **kwargs):

#     # Create an array of all coordinates in the output volume
#     if output_coordinates is None:
#         output_coordinates = volume_coordinates(output_shape) 

#     # Express output coordinates in the scanner reference frame
#     reference_output_coordinates = apply_affine(output_affine, output_coordinates)

#     # Apply free-from deformation to all output coordinates
#     deformation = interpolate_displacement(displacement, output_shape)
#     reference_input_coordinates = reference_output_coordinates + deformation

#     # Express new coordinates in reference frame of the input volume
#     input_affine_inv = np.linalg.inv(input_affine)
#     input_coordinates = apply_affine(input_affine_inv, reference_input_coordinates)

#     # Extend with constant value for half a voxel outside of the boundary
#     # TODO make this an option - costs time and is not necessary when a window is taken inside the FOV (better way to deal with borders)
#     input_coordinates = extend_border(input_coordinates, input_data.shape)

#     # Interpolate the input data in the transformed coordinates
#     output_data = ndi.map_coordinates(input_data, input_coordinates.T, **kwargs)
#     output_data = np.reshape(output_data, output_shape)

#     return output_data

def interpolate_displacement_coords(dshape, shape):
    """Get the coordinates of the interpolated displacement field."""

    w = np.array(dshape[:-1])-1
    d = np.divide(w, shape)
    xo, yo, zo = np.meshgrid(
        np.linspace(0.5*d[0], w[0]-0.5*d[0], shape[0]),
        np.linspace(0.5*d[1], w[1]-0.5*d[1], shape[1]),
        np.linspace(0.5*d[2], w[2]-0.5*d[2], shape[2]),
        indexing = 'ij')
    return np.column_stack((xo.ravel(), yo.ravel(), zo.ravel())).T


def interpolate_displacement(displacement_field, shape, coord=None, order=1, **kwargs):

    if coord is None:
        coord = interpolate_displacement_coords(displacement_field.shape, shape)

    # Interpolate displacement field in volume coordinates.
    dx = ndi.map_coordinates(displacement_field[...,0], coord, order=order, **kwargs)
    dy = ndi.map_coordinates(displacement_field[...,1], coord, order=order, **kwargs)
    dz = ndi.map_coordinates(displacement_field[...,2], coord, order=order, **kwargs)
    deformation = np.column_stack((dx,dy,dz))
    #deformation = np.reshape(deformation, (np.prod(shape), 3))

    return deformation


def freeform_interpolator(dshape, shape, **kwargs):
    iind = []
    ival = []
    coord = interpolate_displacement_coords(dshape, shape)
    displacement = np.zeros(dshape, dtype=np.float32)
    for i in range(displacement.size):
        c = np.unravel_index(i, displacement.shape)
        displacement[c] = 1
        v = interpolate_displacement(displacement, shape, coord, **kwargs)
        v = np.ravel(v)
        displacement[c] = 0
        ind = np.where(v != 0)
        val = v[ind]
        iind.append(ind)
        ival.append(val)
    return {'ind':iind, 'val':ival}


def interpolator_displacement(displacement, shape, interpolator):

    displacement_interp = np.zeros((np.prod(shape)*3,), np.float32)
    for i in range(displacement.size):
        c = np.unravel_index(i, displacement.shape)
        displacement_interp[interpolator['ind'][i]] += displacement[c]*interpolator['val'][i]
    displacement_interp = np.reshape(displacement_interp, (np.prod(shape), 3))
    return displacement_interp




def upsample_deformation_field(field, ni):

    new_field = np.empty(ni + (3,))
    L = np.array(field.shape[:3])-1

    # Get x, y, z coordinates for current field
    x = np.linspace(0, L[0], field.shape[0])
    y = np.linspace(0, L[1], field.shape[0])
    z = np.linspace(0, L[0], field.shape[0])

    # Get x, y, z coordinates for new field
    xi = np.linspace(0, L[0], new_field.shape[0])
    yi = np.linspace(0, L[1], new_field.shape[1])
    zi = np.linspace(0, L[2], new_field.shape[2])

    # Interpolate to new resolution
    ri = np.meshgrid(xi, yi, zi, indexing='ij')
    ri = np.stack(ri, axis=-1)
    for d in range(3):
        new_field[...,d] = interpn((x,y,z), field[...,d], ri)
    return new_field


def deformation_field_shape(data_shape, nodes):
    # Work out the exact number of nodes for each dimensions
    # Assuming the given number of nodes is exact for the largest dimension
    # And the distance between nodes is approximately the same in other directions

    distance_between_nodes = np.amax(data_shape)/(nodes-1)
    shape = 1 + np.ceil(data_shape/distance_between_nodes)
    return tuple(shape.astype(np.int16)) + (3,)



def affine_freeform(
        input_data, input_affine, 
        output_shape, output_affine, 
        parameters, nodes=4):
    
    inverse_deformation_field = affine_deformation_field(
        input_affine, 
        output_shape, output_affine, 
        parameters, nodes=nodes)

    output_data = freeform(
        input_data, input_affine, 
        output_shape, output_affine, 
        inverse_deformation_field)

    return output_data


def affine_deformation_field(
        input_affine, 
        output_shape, output_affine, 
        parameters, nodes=4):
    
    # Perform an affine transformation using a freeform model
    
    affine_transformation_abs = vreg.utils.affine_matrix(
        rotation=parameters[:3], 
        translation=parameters[3:6], 
        pixel_spacing=parameters[6:])

    # Express affine transformation in input coordinates
    affine_transformation = np.linalg.inv(input_affine).dot(affine_transformation_abs).dot(input_affine)

    # Invert affine transformation
    affine_transformation_inv = np.linalg.inv(affine_transformation)

    # Get corresponding inverse deformation field
    o2i = np.linalg.inv(input_affine).dot(output_affine)
    inverse_deformation_field = _affine_deformation_field(affine_transformation_inv, output_shape, nodes, output_to_input=o2i)

    return inverse_deformation_field


def _affine_deformation_field(affine, output_shape, nodes, output_to_input=np.eye(4)):

    # Initialise the inverse deformation field
    shape = deformation_field_shape(output_shape, nodes)

    # Get coordinates in output reference frame
    xo, yo, zo = np.meshgrid(
        np.linspace(0, output_shape[0], shape[0]),
        np.linspace(0, output_shape[1], shape[1]),
        np.linspace(0, output_shape[2], shape[2]),
        indexing = 'ij')
    coordinates = np.column_stack((xo.ravel(), yo.ravel(), zo.ravel()))

    # Express output coordinates in reference frame of the input volume
    coordinates = vreg.mod_affine.apply_affine(output_to_input, coordinates)

    # Apply affine in reference frame of input
    new_coordinates = vreg.mod_affine.apply_affine(affine, coordinates)

    # Get the deformation field in shape (x,y,z,dim)
    deformation_field = new_coordinates - coordinates
    deformation_field = np.reshape(deformation_field, shape)

    return deformation_field


# def _interpolate_displacement(displacement_field, shape, **kwargs):

#     # Get x, y, z coordinates for deformation field
#     w = np.array(displacement_field.shape[:-1])-1
#     x = np.linspace(0, w[0], displacement_field.shape[0])
#     y = np.linspace(0, w[1], displacement_field.shape[1])
#     z = np.linspace(0, w[2], displacement_field.shape[2])

#     # Get x, y, z coordinates for voxel centers
#     di = np.divide(w, shape)
#     xi = np.linspace(0.5*di[0], w[0]-0.5*di[0], shape[0])
#     yi = np.linspace(0.5*di[1], w[1]-0.5*di[1], shape[1])
#     zi = np.linspace(0.5*di[2], w[2]-0.5*di[2], shape[2])

#     # Create coordinate array
#     dim = np.arange(3)
#     #ri = np.meshgrid(xi, yi, zi, indexing='ij')
#     ri = np.meshgrid(xi, yi, zi, dim, indexing='ij')
#     ri = np.stack(ri, axis=-1)

#     # Interpolate the displacement field in the voxel centers
#     #dx = interpn((x,y,z), displacement_field[...,0], ri, method='linear')
#     #dy = interpn((x,y,z), displacement_field[...,1], ri, method='linear')
#     #dz = interpn((x,y,z), displacement_field[...,2], ri, method='linear')
#     #displacement_field = np.column_stack((dx,dy,dz))
#     displacement_field = interpn((x,y,z,dim), displacement_field, ri, method='linear')
#     displacement_field = np.reshape(displacement_field, (np.prod(shape), 3))

#     # Return results
#     return displacement_field