import numpy as np
from skimage.draw import ellipsoid

import vreg.utils
import vreg.mod_affine

#############################
# Generate test data
#############################


def generate(structure='ellipsoid', shape=None, affine=None, markers=True):
    
    # Default shape
    if shape is None:
        shape = (256, 256, 40) 

    # Default affine
    if affine is None:
        pixel_spacing = np.array([1.5, 1.5, 5]) # mm
        translation = np.array([0, 0, 0]) # mm
        rotation_angle = -0.2 * (np.pi/2) # radians
        rotation_axis = [1,0,0]
        rotation = rotation_angle * np.array(rotation_axis)/np.linalg.norm(rotation_axis)
        affine = vreg.utils.affine_matrix(rotation=rotation, translation=translation, pixel_spacing=pixel_spacing)

    _, _ , pixel_spacing = vreg.utils.affine_components(affine) 
    data = np.zeros(shape, dtype=np.float32)  

    if markers:
        # Insert cube markers at corners
        marker_width = 20 # marker width in mm
        w = np.around(np.divide(np.array([marker_width]*3), pixel_spacing))
        w = w.astype(np.int16) 
        data[0:w[0],0:w[1],0:w[2]] = 1
        data[-w[0]:,0:w[1],0:w[2]] = 1
        data[0:w[0],-w[1]:,0:w[2]] = 1
        data[-w[0]:,-w[1]:,0:w[2]] = 1
        data[0:w[0],0:w[1],-w[2]:] = 1
        data[-w[0]:,0:w[1],-w[2]:] = 1
        data[0:w[0],-w[1]:,-w[2]:] = 1
        data[-w[0]:,-w[1]:,-w[2]:] = 1

    if structure == 'ellipsoid':
        half_length = (20, 30, 40) # mm
        ellip = ellipsoid(half_length[0], half_length[1], half_length[2], spacing=pixel_spacing, levelset=False)
        d = ellip.shape
        p = [30, 30, 10]
        data[p[0]:p[0]+d[0], p[1]:p[1]+d[1], p[2]:p[2]+d[2]] = ellip
        return data, affine
    
    elif structure == 'double ellipsoid':
        half_length1 = np.array([10, 20, 30]) # mm
        half_length2 = np.array([5, 10, 15]) # mm
        pos = np.array([150, 50, 0]) # mm
        ellip1 = ellipsoid(half_length1[0], half_length1[1], half_length1[2], spacing=pixel_spacing, levelset=False)
        ellip2 = ellipsoid(half_length2[0], half_length2[1], half_length2[2], spacing=pixel_spacing, levelset=False)
        ellip1 = ellip1.astype(np.int16)
        ellip2 = ellip2.astype(np.int16)

        p = np.around(np.divide(pos, pixel_spacing)).astype(np.int16)
        d = ellip1.shape
        data[p[0]:p[0]+d[0], p[1]:p[1]+d[1], p[2]:p[2]+d[2]] = ellip1

        p += np.around([d[0], d[1]/4, d[2]/2]).astype(np.int16)
        d = ellip2.shape
        data[p[0]:p[0]+d[0], p[1]:p[1]+d[1], p[2]:p[2]+d[2]] = ellip2

        return data, affine

    elif structure == 'triple ellipsoid':
        half_length1 = np.array([10, 20, 30]) # mm
        half_length2 = np.array([5, 10, 15]) # mm
        p1 = np.array([150, 50, 10]) # mm
        p2 = np.array([170, 70, 20]) # mm
        p3 = np.array([150, 150, 10]) # mm

        ellip1 = ellipsoid(half_length1[0], half_length1[1], half_length1[2], spacing=pixel_spacing, levelset=False)
        ellip2 = ellipsoid(half_length2[0], half_length2[1], half_length2[2], spacing=pixel_spacing, levelset=False)
        ellip1 = ellip1.astype(np.int16)
        ellip2 = ellip2.astype(np.int16)

        p = np.around(np.divide(p1, pixel_spacing)).astype(np.int16)
        d = ellip1.shape
        data[p[0]:p[0]+d[0], p[1]:p[1]+d[1], p[2]:p[2]+d[2]] = ellip1
        
        p = np.around(np.divide(p2, pixel_spacing)).astype(np.int16)
        d = ellip2.shape
        data[p[0]:p[0]+d[0], p[1]:p[1]+d[1], p[2]:p[2]+d[2]] = ellip2

        p = np.around(np.divide(p3, pixel_spacing)).astype(np.int16)
        d = ellip1.shape
        data[p[0]:p[0]+d[0], p[1]:p[1]+d[1], p[2]:p[2]+d[2]] = ellip1

        return data, affine 


def generate_plot_data_1():

    # Define geometry of input data
    pixel_spacing = np.array([2.0, 2.0, 10.0]) # mm
    input_shape = np.array([100, 100, 10], dtype=np.int16)
    translation = np.array([0, 0, 0]) # mm
    rotation_angle = 0.0 * (np.pi/2) # radians
    rotation_axis = [1,0,0]
    rotation = rotation_angle * np.array(rotation_axis)/np.linalg.norm(rotation_axis)
    input_affine = vreg.utils.affine_matrix(rotation=rotation, translation=translation, pixel_spacing=pixel_spacing)
    
    # Generate ground truth data
    input_data, input_affine = generate('triple ellipsoid', shape=input_shape, affine=input_affine, markers=True)

    return input_data, input_affine


def generate_reslice_data_1():

    # Downsample
    # Reslice high-res volume to lower resolution.
    # Values are chosen so that the field of view stays the same.

    # Define geometry of input data
    matrix = np.array([400, 300, 120])  
    pixel_spacing = np.array([1.0, 1.0, 1.0]) # mm
    translation = np.array([0, 0, 0]) # mm
    rotation_angle = -0.0 * (np.pi/2) # radians
    rotation_axis = [1,0,0]
    rotation = rotation_angle * np.array(rotation_axis)/np.linalg.norm(rotation_axis)

    # Define geometry of output data
    output_pixel_spacing = np.array([1.25, 5.0, 10.0]) # mm
    output_shape = None # retain field of view

    # Generate data
    input_affine = vreg.utils.affine_matrix(rotation=rotation, translation=translation, pixel_spacing=pixel_spacing)
    output_affine = vreg.utils.affine_matrix(rotation=rotation, translation=translation, pixel_spacing=output_pixel_spacing)
    input_data, input_affine = generate('triple ellipsoid', shape=matrix, affine=input_affine, markers=True)

    return input_data, input_affine, output_affine, output_shape


def generate_reslice_data_2():

    # Upsample
    # Reslice low-res volume to higher resolution.
    # Values are chosen so that the field of view stays the same.

    # Define geometry of input data
    matrix = np.array([320, 60, 8])  
    pixel_spacing = np.array([1.25, 5.0, 15.0]) # mm
    translation = np.array([0, 0, 0]) # mm
    rotation_angle = -0.0 * (np.pi/2) # radians
    rotation_axis = [1,0,0]
    rotation = rotation_angle * np.array(rotation_axis)/np.linalg.norm(rotation_axis)

    # Define geometry of output data
    output_pixel_spacing = np.array([1.0, 1.0, 1.0]) # mm
    output_shape = None # retain field of view

    # Generate data
    input_affine = vreg.utils.affine_matrix(rotation=rotation, translation=translation, pixel_spacing=pixel_spacing)
    output_affine = vreg.utils.affine_matrix(rotation=rotation, translation=translation, pixel_spacing=output_pixel_spacing)
    input_data, input_affine = generate('triple ellipsoid', shape=matrix, affine=input_affine, markers=False)

    return input_data, input_affine, output_affine, output_shape


def generate_reslice_data_3():

    # resample to lower resolution with a
    # 90 degree rotation around x + translation along y

    # Define source data
    matrix = np.array([400, 300, 120]) 
    pixel_spacing = np.array([1.0, 1.0, 1.0]) # mm
    translation = np.array([0, 0, 0]) # mm
    rotation_angle = 0 * (np.pi/2) # radians
    rotation_axis = [1,0,0]

    # Generate source data
    rotation = rotation_angle * np.array(rotation_axis)/np.linalg.norm(rotation_axis)
    input_affine = vreg.utils.affine_matrix(rotation=rotation, translation=translation, pixel_spacing=pixel_spacing)
    input_data, input_affine = generate('triple ellipsoid', shape=matrix, affine=input_affine)

    # Define geometry of new slab
    pixel_spacing = np.array([1.25, 1.25, 10.0]) # mm
    translation = np.array([0, 120, 0]) # mm
    rotation_angle = 1.0 * (np.pi/2) # radians
    rotation_axis = [1,0,0]
    
    # Reslice current slab to geometry of new slab
    rotation = rotation_angle * np.array(rotation_axis)/np.linalg.norm(rotation_axis)
    output_affine = vreg.utils.affine_matrix(rotation=rotation, translation=translation, pixel_spacing=pixel_spacing)
    output_shape = None
    return input_data, input_affine, output_affine, output_shape


def generate_reslice_data_4():

    # Rotation at low resolution

    # Define geometry of input data
    input_shape = np.array([40, 40, 20], dtype=np.int16)
    pixel_spacing = np.array([6, 6, 6.0])       # mm
    translation = np.array([0, 0, 0]) # mm
    rotation_angle = 0.0 * (np.pi/2) # radians
    rotation_axis = [1,0,0]
    rotation = rotation_angle * np.array(rotation_axis)/np.linalg.norm(rotation_axis)
    input_affine = vreg.utils.affine_matrix(rotation=rotation, translation=translation, pixel_spacing=pixel_spacing)

    # Define output affine
    #pixel_spacing = np.array([0.5, 0.5, 0.5])       # mm
    translation = np.array([0, 0, 0])     # mm
    rotation_angle = 0.15 * (np.pi/2)    # radians
    #translation = np.array([0, 0, 30]) # mm
    rotation_axis = [1,0,0]
    rotation = rotation_angle * np.array(rotation_axis)/np.linalg.norm(rotation_axis)
    output_affine = vreg.utils.affine_matrix(rotation=rotation, translation=translation, pixel_spacing=pixel_spacing)
    
    # Generate input data data
    input_data, input_affine = generate('triple ellipsoid', shape=input_shape, affine=input_affine, markers=True)

    return input_data, input_affine, output_affine, None


def generate_reslice_data_5():

    # Reslice an object with its own affine

    # Define geometry of input data
    input_size = np.array([400, 300, 120])   # mm
    input_shape = np.array([400, 300, 120], dtype=np.int16)
    translation = np.array([0, 0, 0]) # mm
    rotation_angle = 0.0 * (np.pi/2) # radians
    rotation_axis = [1,0,0]
    rotation = rotation_angle * np.array(rotation_axis)/np.linalg.norm(rotation_axis)
    pixel_spacing = np.divide(input_size, input_shape)
    input_affine = vreg.utils.affine_matrix(rotation=rotation, translation=translation, pixel_spacing=pixel_spacing)

    # Define output affine
    pixel_spacing = np.array([1.6, 2.6, 7.5])       # mm
    translation = np.array([100, 0, 0])     # mm
    rotation_angle = 0.1 * (np.pi/2)    # radians
    rotation_axis = [1,0,0]
    rotation = rotation_angle * np.array(rotation_axis)/np.linalg.norm(rotation_axis)
    output_affine = vreg.utils.affine_matrix(rotation=rotation, translation=translation, pixel_spacing=pixel_spacing)
    
    # Generate input data data
    input_data, input_affine = generate('triple ellipsoid', shape=input_shape, affine=input_affine, markers=False)

    # Reslice to output affine keeping the same field of view
    output_data, output_affine = vreg.mod_affine.affine_reslice(input_data, input_affine, output_affine)

    return output_data, output_affine, output_affine, None


def generate_reslice_data_6():

    # 1-pixel thick - does not work yet!!

    # Define geometry of input data
    pixel_spacing = np.array([1.25, 1.25, 5.0]) # mm
    input_shape = np.array([300, 200, 20], dtype=np.int16)
    translation = np.array([0, 0, 0]) # mm
    rotation_angle = 0.0 * (np.pi/2) # radians
    rotation_axis = [1,0,0]
    rotation = rotation_angle * np.array(rotation_axis)/np.linalg.norm(rotation_axis)
    input_affine = vreg.utils.affine_matrix(rotation=rotation, translation=translation, pixel_spacing=pixel_spacing)

    # Define geometry of output data
    pixel_spacing = np.array([1.25, 1.25, 10.0]) # mm
    output_shape = np.array([300, 250, 1], dtype=np.int16)
    translation = np.array([0, 0, 5]) # mm
    rotation_angle = 0.2 * (np.pi/2) # radians
    rotation_axis = [1,0,0]
    rotation = rotation_angle * np.array(rotation_axis)/np.linalg.norm(rotation_axis)
    output_affine = vreg.utils.affine_matrix(rotation=rotation, translation=translation, pixel_spacing=pixel_spacing)
    
    # Generate ground truth data
    input_data, input_affine = generate('triple ellipsoid', shape=input_shape, affine=input_affine, markers=True)

    return input_data, input_affine, output_affine, output_shape


def generate_translated_data_1():

    # Define geometry of input data
    pixel_spacing = np.array([1.25, 1.25, 5.0]) # mm
    translation = np.array([0, 0, 0]) # mm
    rotation_angle = 0.5 * (np.pi/2) # radians
    rotation_axis = [1,0,0]
    rotation = rotation_angle * np.array(rotation_axis)/np.linalg.norm(rotation_axis)
    input_affine = vreg.utils.affine_matrix(rotation=rotation, translation=translation, pixel_spacing=pixel_spacing)
    input_shape = np.array([300, 200, 25])  

    # Define affine transformation
    translation = np.array([10, -10, 10]) # mm
    
    # Define geometry of output data (exactly equal to translated volume)
    transformation = vreg.utils.affine_matrix(translation=translation)
    output_shape, output_affine = vreg.utils.affine_output_geometry(input_shape, input_affine, transformation)

    # Generate ground truth data
    input_data, input_affine = generate('triple ellipsoid', shape=input_shape, affine=input_affine, markers=False)
    output_data = vreg.mod_affine.translate(input_data, input_affine, output_shape, output_affine, translation)

    return input_data, input_affine, output_data, output_affine, translation


def generate_translated_data_2():

    # Model for 3D to 2D registration

    # Define geometry of input data
    pixel_spacing = np.array([1.0, 1.0, 1.0]) # mm
    translation = np.array([0, 0, 0]) # mm
    rotation_angle = 0.0 * (np.pi/2) # radians
    rotation_axis = [1,0,0]
    rotation = rotation_angle * np.array(rotation_axis)/np.linalg.norm(rotation_axis)
    input_affine = vreg.utils.affine_matrix(rotation=rotation, translation=translation, pixel_spacing=pixel_spacing)
    input_shape = np.array([300, 200, 100]) 

    # Define affine transformation
    active_translation = np.array([10, -10, 10]) # mm

    # Define geometry of output data
    output_shape = np.array([150, 200, 1])  
    pixel_spacing = np.array([1.25, 1.25, 7.5]) # mm
    #translation = np.array([100, 0, 50]) # mm
    translation = np.array([100, 0, 25]) # mm
    rotation_angle = 0.1 * (np.pi/2) # radians
    rotation_axis = [1,0,0]
    rotation = rotation_angle * np.array(rotation_axis)/np.linalg.norm(rotation_axis)
    output_affine = vreg.utils.affine_matrix(rotation=rotation, translation=translation, pixel_spacing=pixel_spacing)

    # Generate ground truth data
    input_data, input_affine = generate('triple ellipsoid', shape=input_shape, affine=input_affine, markers=False)
    output_data = vreg.mod_affine.translate(input_data, input_affine, output_shape, output_affine, active_translation)

    return input_data, input_affine, output_data, output_affine, active_translation


def generate_translated_data_3():

    # Model for 2D to 3D registration
    # Same as 2 but input and output reversed

    # Define geometry of input data
    pixel_spacing = np.array([1.0, 1.0, 1.0]) # mm
    translation = np.array([0, 0, 0]) # mm
    rotation_angle = 0.0 * (np.pi/2) # radians
    rotation_axis = [1,0,0]
    rotation = rotation_angle * np.array(rotation_axis)/np.linalg.norm(rotation_axis)
    input_affine = vreg.utils.affine_matrix(rotation=rotation, translation=translation, pixel_spacing=pixel_spacing)
    input_shape = np.array([300, 200, 100]) 

    # Define affine transformation
    active_translation = np.array([10, -10, 10]) # mm

    # Define geometry of output data
    output_shape = np.array([150, 200, 1])   # mm
    pixel_spacing = np.array([1.25, 1.25, 7.5]) # mm
    # translation = np.array([100, 0, 50]) # mm
    translation = np.array([100, 0, 25]) # mm
    rotation_angle = 0.1 * (np.pi/2) # radians
    rotation_axis = [1,0,0]
    rotation = rotation_angle * np.array(rotation_axis)/np.linalg.norm(rotation_axis)
    output_affine = vreg.utils.affine_matrix(rotation=rotation, translation=translation, pixel_spacing=pixel_spacing)

    # Generate ground truth data
    input_data, input_affine = generate('triple ellipsoid', shape=input_shape, affine=input_affine, markers=False)
    output_data = vreg.mod_affine.translate(input_data, input_affine, output_shape, output_affine, active_translation)

    return output_data, output_affine, input_data, input_affine, -active_translation
