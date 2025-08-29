import numpy as np
import scipy.ndimage as ndi

import vreg.utils



# def mask_volume(array, affine, array_mask, affine_mask, margin:float=0):

#     # Overlay the mask on the array.
#     array_mask, _ = affine_reslice(array_mask, affine_mask, affine, array.shape)

#     # Mask out array pixels outside of region.
#     array *= array_mask

#     # Extract bounding box around non-zero pixels in masked array.
#     array, affine = vreg.utils.bounding_box(array, affine, margin)
    
#     return array, affine

def mask_volume(array, affine, array_mask, affine_mask, margin:float=0):

    # Overlay the mask on the array.
    array_mask, _ = affine_reslice(array_mask, affine_mask, affine, array.shape)

    # Extract bounding box around non-zero pixels in masked array.
    geom = vreg.utils.bounding_box_geom(array_mask, affine, margin)
    array, affine = vreg.utils.bounding_box_apply(array, affine, *geom)
    
    return array, affine



def apply_affine(affine, coord):
    """Apply affine transformation to an array of coordinates"""

    nd = affine.shape[0]-1
    matrix = affine[:nd,:nd]
    offset = affine[:nd, nd]
    return np.dot(coord, matrix.T) + offset
    #return np.dot(matrix, co.T).T + offset


def apply_inverse_affine(
        input_data, inverse_affine, 
        output_shape, output_coordinates=None, 
        order=1, **kwargs):

    # Create an array of all coordinates in the output volume
    if output_coordinates is None:
        output_coordinates = vreg.utils.volume_coordinates(output_shape)

    # Apply affine transformation to all coordinates in the output volume
    # nd = inverse_affine.shape[0]-1
    # matrix = inverse_affine[:nd,:nd]
    # offset = inverse_affine[:nd, nd]
    # input_coordinates = np.dot(output_coordinates, matrix.T) + offset
    # #co = np.dot(matrix, co.T).T + offset
    input_coordinates = apply_affine(inverse_affine, output_coordinates)

    # Extend with constant value for half a voxel outside of the boundary
    input_coordinates = vreg.utils.extend_border(
        input_coordinates, input_data.shape)

    # Interpolate the volume in the transformed coordinates
    #output_data = ndi.map_coordinates(input_data, input_coordinates.T, **kwargs)
    output_data = ndi.map_coordinates(
        input_data, input_coordinates.T, order=order, **kwargs)
    output_data = np.reshape(output_data, output_shape)

    return output_data


def affine_reslice(
        input_data, input_affine:np.ndarray, 
        output_affine:np.ndarray, output_shape=None, 
        **kwargs):

    # If the output shape is 2d, add a 3d dimension of size 1 for the calculation
    output_2d = False
    if output_shape is not None:
        output_2d = np.size(output_shape)==2
        if output_2d:
            output_shape = output_shape + (1,)

    # If 2d array, add a 3d dimension of size 1
    if input_data.ndim == 2: 
        input_data = np.expand_dims(input_data, axis=-1)

    # If no output shape is provided, retain the physical volume of the input datas
    if output_shape is None:

        # Get field of view from input data
        input_pixel_spacing = np.linalg.norm(input_affine[:3,:3], axis=0)
        field_of_view = np.multiply(np.array(input_data.shape), input_pixel_spacing)

        # Find output shape for the same field of view
        #output_rotation, output_translation, output_pixel_spacing = vreg.utils.affine_components(output_affine)
        output_pixel_spacing = np.linalg.norm(output_affine[:3,:3], axis=0)
        output_shape = np.around(np.divide(field_of_view, output_pixel_spacing)).astype(np.int16)
        output_shape[np.where(output_shape==0)] = 1

        # Adjust output pixel spacing to fit the field of view
        output_pixel_spacing = np.divide(field_of_view, output_shape)
        new_output_affine = output_affine.copy()
        for d in [0,1,2]:
            new_output_affine[:3,d] = output_pixel_spacing[d] * output_affine[:3,d]/np.linalg.norm(output_affine[:3,d])
        output_affine = new_output_affine
        # output_affine = vreg.utils.affine_matrix(
        #     rotation=output_rotation, translation=output_translation, 
        #     pixel_spacing=output_pixel_spacing)

    # Reslice input data to output geometry
    transform = np.linalg.inv(input_affine).dot(output_affine) # Ai B
    output_data = apply_inverse_affine(input_data, transform, output_shape, **kwargs)

    # If a 2d output shape was requested, return a 2d array
    if output_2d:
        output_data = output_data[:,:,0]

    return output_data, output_affine


def affine_transform(input_data, input_affine, transformation, reshape=False, **kwargs):

    # If 2d array, add a 3d dimension of size 1
    if input_data.ndim == 2: 
        input_data = np.expand_dims(input_data, axis=-1)

    if reshape:
        output_shape, output_affine = vreg.utils.affine_output_geometry(input_data.shape, input_affine, transformation)
    else:
        output_shape, output_affine = input_data.shape, input_affine.copy()

    # Perform the inverse transformation
    affine_transformed = transformation.dot(input_affine)
    inverse = np.linalg.inv(affine_transformed).dot(output_affine) # Ainv Tinv B 
    output_data = apply_inverse_affine(input_data, inverse, output_shape, **kwargs)

    return output_data, output_affine

# This needs a
def affine_transform_and_reslice(input_data, input_affine, output_shape, output_affine, transformation, **kwargs):

    input_data = vreg.utils.to_3d(input_data)
    affine_transformed = transformation.dot(input_affine)
    inverse = np.linalg.inv(affine_transformed).dot(output_affine) # Ai Ti B
    output_data = apply_inverse_affine(input_data, inverse, output_shape, **kwargs)

    return output_data
