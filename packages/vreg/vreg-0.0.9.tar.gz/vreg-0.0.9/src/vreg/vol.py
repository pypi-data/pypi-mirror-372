import numpy as np

from vreg import mod_affine, metrics, utils, optimize

class Volume3D:
    # TODO: for multidimensional volumes, one affine per volume
    # API ND:
    # values[:, :, :, i, j]
    # affine[:, :, i, j]
    # coords[:, i, j]
    # dims[i], dims[j]
    # API 3D:
    # values[:, :, :]
    # affine[:, :]
    # coords = None
    # dims = None
    """
    A spatially aware numpy array
    
    Args:
        values (np.ndarray): Numpy array of values (3 or more dimensions)
        affine (np.ndarray): 4x4 numpy array with the affine matrix 
            of the value array. If not provided, the identity is assumed. 
            Defaults to None.  
        coords (np.ndarray): For values with dimensions more than 3, 
            provide an additional coordinate array for the locations 
            of the replicated volumes. If not provided, index arrays 
            are used for the coordinates of the extra dimensions.
        dims (list): Names of the extra dimensions for volumes with more 
            than 3 dimensions.
        prec (int): internal precision to be used when comparing positions. 
            If not provided, the exact floating point values of locations 
            are used. Defaults to None.
    """

    def __init__(self, values:np.ndarray, affine:np.ndarray, 
                 coords:np.ndarray=None, dims:list=None, prec:int=None):
        
        # Set precision
        if prec is not None:
            if not isinstance(prec, int):
                raise ValueError("prec needs to be an integer.")
        self._prec = prec

        # Set values
        if not isinstance(values, np.ndarray):
            raise ValueError('values must be a numpy array.')
        if values.ndim < 3:
            raise ValueError("values must have at least 3 dimensions.")
        self._values = values

        # Set affine
        if not isinstance(affine, np.ndarray):
            raise ValueError('affine must be a numpy array.')
        if affine.shape != (4,4):
            raise ValueError('affine must be a 4x4 array.')
        self._affine = affine

        # Set coords & dims
        self._coords = None
        self._dims = None
        if values.ndim > 3:

            # Set dims
            if dims is None:
                dims = list(range(values.ndim-3))
            elif len(dims) != values.ndim-3:
                raise ValueError(
                    f"dims should have {values.ndim-3} values."
                )  
            self._dims = dims

            # Set coords
            if coords is None:
                coords = [np.arange(d) for d in values.shape[3:]]
                coords = np.meshgrid(*coords, indexing='ij')
                coords = np.stack(coords, axis=0)
            elif not isinstance(coords, np.ndarray):
                raise ValueError("coords must be a numpy array")
            # coords[i,j,k,n]
            elif coords.shape[0] != values.ndim-3:
                raise ValueError(
                    f"coords should have {values.ndim-3} coordinates."
                )
            elif coords.shape[1:] != values.shape[3:]:
                raise ValueError(
                    f"coords should have dimensions {values.shape[3:]}."
                )
            self._coords = coords
            
    
    @property
    def values(self):
        return self._values
    
    @property
    def affine(self):
        return self._affine
    
    @property
    def coords(self):
        return self._coords
    
    @property
    def dims(self):
        return self._dims
    
    @property
    def prec(self):
        return self._prec
    
    @property
    def ndim(self): 
        return self._values.ndim
    
    @property
    def shape(self):
        return self._values.shape
    
    @property
    def spacing(self):
        return np.linalg.norm(self.affine[:3,:3], axis=0)
    
    @property
    def row_dir(self):
        return self.affine[:3,0]/np.linalg.norm(self.affine[:3,0])
    
    @property
    def col_dir(self):
        return self.affine[:3,1]/np.linalg.norm(self.affine[:3,1])
    
    @property
    def slice_dir(self):
        return self.affine[:3,2]/np.linalg.norm(self.affine[:3,2])
    
    @property
    def is_right_handed(self):
        normal = np.cross(self.affine[:3,0], self.affine[:3,1])
        proj = np.dot(self.affine[:3,2], normal)
        return proj > 0



    def set_values(self, values:np.ndarray):
        """Set new values for the volume

        Args:
            values (np.ndarray): array with the same shape as the 
                existing array of values.
        """
        if not isinstance(values, np.ndarray):
            raise ValueError('values must be a numpy array.')
        
        if values.shape != self.values.shape:
            raise ValueError(f'values must have dimensions {self.values.shape}.')
        
        self._values = values
        return self


    def set_affine(self, affine:np.ndarray):
        """Set a new affine for the volume

        Args:
            affine (np.ndarray): 4x4 affine array
        """
        if not isinstance(affine, np.ndarray):
            raise ValueError('affine must be a numpy array.')
        
        if affine.shape != (4,4):
            raise ValueError('affine must be a 4x4 array.')
        
        self._affine = affine
        return self


    def set_coords(self, coords:np.ndarray):
        """Set new coordinates for the volume

        Args:
            coords (np.ndarray): Array of coordinates

        Raises:
            ValueError: If the new coords have the wrong shape.
        """
        if coords.shape != self._coords.shape:
            raise ValueError("New coordinate array has the wrong shape")
        self._coords = coords
        return self


    def set_dims(self, dims:list):
        """Set new names for the non-spatial dimensions

        Args:
            dims (np.ndarray): List of dimension names

        Raises:
            ValueError: If the new dims has the wrong length.
        """
        if len(dims) != self.values.ndim-3:
            raise ValueError(
                f"dims should have {self.values.ndim-3} values."
            )   
        self._dims = dims
        return self

    
    def copy(self, **kwargs):
        """Return a copy

        Args:
            kwargs: Any keyword arguments accepted by `numpy.copy`.

        Returns:
            Volume3D: copy
        """
        return Volume3D(
            self.values.copy(**kwargs), 
            self.affine.copy(**kwargs),
            self.coords.copy(**kwargs),
            list(np.asarray(self.dims).copy(**kwargs)),
            self._prec,
        )
    
    def extract_slice(self, z=0):
        """Extract a slice at index z

        Args:
            z (int, optional): slice index

        Returns:
            vreg.Volume3D: one-slice Volume3D at index z
        """
        if self.ndim > 3:
            raise ValueError("This function is not yet available for volumes "
                             "with more than 3 dimensions")
        values, affine = utils.extract_slice(self.values, self.affine, z)
        values = np.expand_dims(values.copy(), axis=-1)
        return Volume3D(values, affine.copy())


    def separate(self, axis=None):
        """Separate a volume along one or more time axes.

        Args:
            axis (int, optional): Time axis along which to separate. If this 
              is not provided, the volume is separated along all time 
              axes. Defaults to None.

        Returns:
            np.ndarray: array of 3D volumes. 
        """

        if axis in [0,1,2]:
            raise ValueError("A volume cannot be separated along a space axis. "
                             "Use split() instead.")  
        if self.ndim==3:
            raise ValueError("A 3D volume can not be separated. Perhaps "
                              "you wanted to split()?")
        if axis is not None:
            vols = []
            for i in range(self.shape[axis]):
                coords_i = _take_keepdims(self.coords, i, 1+axis-3)
                affine_i = self.affine.copy()
                values_i = _take_view_keepdims(self.values, i, axis)
                # Build the volume and add to the list.
                vol_i = Volume3D(values_i, affine_i, coords_i, self.dims) 
                vols.append(vol_i)
            return np.asarray(vols) 
        else:
            axis = self.ndim-1
            vols = self.separate(axis) # 1D
            if axis > 3:
                axis -= 1
                shape = vols.shape
                vols = [v.separate(axis) for v in vols.reshape(-1)]
                newdim = vols[0].size
                vols = np.array(vols).reshape(shape + (newdim,)) # 3D
            return vols


    def split(self, n=None, axis=2, gap=0)->list:
        """Split a volume into slices (2D volumes)

        Args:
            n (int, optional): number of slices in the result. If this is not 
              provided, n is the shape of the volume in the axis along which 
              it is split. Defaults to None.
            axis (int, optional): Axis along which to split the volume. 
              Defaults to -1 (z-axis).
            gap (float, optional): Add a gap (in mm) between the resulting 
              slices. Defaults to 0.

        Returns:
            list of Volume3D: a list of volumes with a single slice each.
        """
        if axis not in [0,1,2]:
            raise ValueError("A volume cannot be split along a time axis. Use "
                             "separate() instead.")           
        
        # Default
        if n is None:
            n = self.shape[axis]
        if n==1:
            return [self]
        # If the number of slices required is different from the current 
        # number of slices, then first resample the volume.
        if n == self.shape[axis]:
            vol = self
        else:
            spacing = self.spacing
            spacing[axis] = spacing[axis]*self.shape[axis]/n
            vol = self.resample(spacing) 

        # Split up the volume into a list of 2D volumes.
        mat = vol.affine[:3,:3]
        split_vec = mat[:, axis] 
        split_unit_vec = split_vec/self.spacing[axis]
        vols = []
        for i in range(vol.shape[axis]):
            
            # Shift the affine by i positions along the slice axis.
            affine_i = vol.affine.copy()
            affine_i[:3, 3] += i*split_vec + i*gap*split_unit_vec

            # Take the i-th slice and keep dimensions
            values_i = _take_view_keepdims(vol.values, i, axis)

            # Build the volume and add to the list.
            vol_i = Volume3D(values_i, affine_i, self.coords, self.dims)
            vols.append(vol_i)
        return vols

    
    def add(self, v, *args, **kwargs):
        """Add another volume

        Args:
            v (Volume3D): volume to add. If this is in a different geometry, it 
                will be resliced first
            args, kwargs: arguments and keyword arguments of `numpy.add`.

        Returns:
            Volume3D: sum of the two volumes
        """
        if self.ndim > 3:
            raise ValueError("This function is not yet available for volumes "
                             "with more than 3 dimensions")
        v = v.slice_like(self)
        values = np.add(self.values, v.values, *args, **kwargs)
        return Volume3D(values, self.affine)
    
    def subtract(self, v, *args, **kwargs):
        """Subtract another volume

        Args:
            v (Volume3D): volume to subtract. If this is in a different 
                geometry, it will be resliced first
            args, kwargs: arguments and keyword arguments of `numpy.subtract`.

        Returns:
            Volume3D: sum of the two volumes
        """
        if self.ndim > 3:
            raise ValueError("This function is not yet available for volumes "
                             "with more than 3 dimensions")
        v = v.slice_like(self)
        values = np.subtract(self.values, v.values, *args, **kwargs)
        return Volume3D(values, self.affine)

    def crop(self, mask=None, margin=0.0): # better term than bounding_box
        """Crop to a box

        Args:
            mask (Volume3D, optional): If mask is None, the volume 
                is cropped to the non-zero values of the Volume3D. If mask is 
                provided, it is cropped to the non-zero values of mask 
                instead. Defaults to None.
            margin (float, optional): How big a margin (in physical units) 
                around the object. Defaults to 0.

        Returns:
            Volume3D: the bounding box
        """
        return self.bounding_box(mask, margin)
    

    def bounding_box(self, mask=None, margin=0.0): # replace by crop
        """Return the bounding box

        Args:
            mask (Volume3D, optional): If mask is None, the bounding box is 
                drawn around the non-zero values of the Volume3D. If mask is 
                provided, it is drawn around the non-zero values of mask 
                instead. Defaults to None.
            margin (float, optional): How big a margin (in mm) around the 
                object. Defaults to 0.

        Returns:
            Volume3D: the bounding box
        """
        if self.ndim > 3:
            raise ValueError("This function is not yet available for volumes "
                             "with more than 3 dimensions")
        if mask is None:
            values, affine = mod_affine.mask_volume(
                self.values, self.affine, self.values, self.affine, margin)
        else:
            values, affine = mod_affine.mask_volume(
                self.values, self.affine, mask.values, mask.affine, margin)
        return Volume3D(values, affine)


    def resample(self, spacing=None, stretch=None):
        """Resample volume to new pixel spacing

        Args:
            spacing (array-like, optional): New pixel spacing in mm. Generally 
                this is a 3-element array but for isotropic resampling this can 
                be a scalar value. If this is not provided, the volume is 
                resampled according to the specified stretch. Defaults to None.
            stretch (float, optional): Rescale pixel size with this value. 
                Generally this is a 3-element array, one for each dimension. If 
                a scalar value is provided, all dimensions are resampled with 
                the same stretch factor. This argument is ignored if a spacing is 
                provided explicitly. Defaults to None (no resampling).

        Raises:
            ValueError: if spacing or stretch have the wrong size.

        Returns:
            vreg.Volume3D: resampled volume
        """
        # Set defaults
        if stretch is None:
            stretch = 1.0

        # Affine components
        #rot, trans, ps = utils.affine_components(self.affine)
        ps = self.spacing

        # Get new pixel spacing
        if spacing is None:
            if np.isscalar(stretch):
                spacing = ps*stretch
            elif np.size(stretch)==3:
                spacing = ps*stretch
            else:
                raise ValueError(
                    'stretch must be a scalar or a 3-element array')
        elif np.isscalar(spacing):
            spacing = np.full(3, spacing)
        elif np.size(spacing) != 3:
            raise ValueError(
                'spacing must be a scalar or a 3-element array')
        
        # Resample
        affine = self.affine.copy()
        for d in [0,1,2]:
            affine[:3, d] = spacing[d]*self.affine[:3,d]/self.spacing[d]
        # affine = utils.affine_matrix(rotation=rot, translation=trans, 
        #                              pixel_spacing=spacing)
        if len(self.shape)==3:
            values_reslice, _ = mod_affine.affine_reslice(self.values, self.affine, affine)
        else:
            # Get a flattened view
            values = self.values.reshape(self.shape[:3] + (-1,))
            # Loop over volumes
            for i in range(values.shape[-1]):
                values_reslice_i, _ = mod_affine.affine_reslice(values[...,i], self.affine, affine)
                if i==0:
                    values_reslice = np.empty(values_reslice_i.shape + (values.shape[-1],))
                values_reslice[...,i] = values_reslice_i

        # Return volume
        return Volume3D(values_reslice, affine, self.coords, self.dims)
    

    def find_transform_to(
            self, target, transform, params=None, metric=None, 
            optimizer=None, resolutions=None, 
            mask=None, target_mask=None, **kwargs):
        """Coregister a volume to a static target volume.

        Args:
            target (vreg.Volume3D): Fixed target volume for the coregistration.
            transform (str, optional): Coordinate transformation. 
              Possible values are 'translate', 'rotate', 'stretch', 
              'transform_rigid', 'transform_affine'.
            params (array-like, optional): Initial parameters of the 
              transformation. Defaults to None.
            metric (func, optional): Metric to quantify goodness of alignment. 
              Options are 'mi' (mutual information), 'sos' (sum of squares), 
              and 'migrad' (mutual information of the image gradient).  
              Default is 'mi'.
            optimizer (dict, optional): Optimizer as a dictionary 
              with one key *method* specifying the method used for optimization. 
              The other items in the dictionary are any optional keywords 
              accepted by the method. Defaults to {'method':'LS'}.
            resolutions (list, optional): Resolutions to use in the 
              optimization. Defaults to [1].
            mask (Volume3D, optional): volume used for masking the moving 
              volume. Defaults to None.
            target_mask (Volume3D, optional): volume used for masking the 
              static volume. Defaults to None.
            kwargs (dict, optional): optional keyword arguments for the 
              transform function.

        Returns:
            params: The optimal values for the transformaton parameters.
        """
        if self.ndim > 3:
            raise ValueError("This function is not yet available for volumes "
                             "with more than 3 dimensions")
        # Defaults
        if metric is None:
            metric = 'mi'
        if optimizer is None:
            optimizer = {'method':'LS'}
        if resolutions is None:
            resolutions = [1]

        # Perform multi-resolution loop
        mask_resampled = None
        target_ind = None

        for res in resolutions:

            if res == 1:
                moving = self
                target_resampled = target
            else:
                # Downsample
                moving = self.resample(stretch=res)
                target_resampled = target.resample(stretch=res)

            # resample the masks
            if mask is not None:
                mask_resampled = mask.slice_like(moving)
            if target_mask is not None:
                target_mask_resampled = target_mask.slice_like(target_resampled)
                target_ind = np.where(target_mask_resampled.values >= 0.5)

            args = (
                target_resampled, transform, metric, mask_resampled, 
                target_ind, kwargs,
            )
            params = optimize.minimize(
                moving._dist, params, args=args, **optimizer)
            
        return params

    def _dist(self, params, target, transform, metric, mask, target_ind, 
              kwargs):
        return self.distance(target, transform, params, metric, mask, 
                                   target_ind, **kwargs)

    def distance(self, target, transform, params, metric='mi', mask=None, 
                       target_ind=None, **kwargs):
        """Distance to a target volume after a transform

        Args:
            target (vreg.Volume3D): Target volume
            transform (str, optional): Coordinate transformation. 
              Possible values are 'translate', 'rotate', 'stretch', 
              'transform_rigid', 'transform_affine'.
            params (array-like, optional): Initial parameters of the 
              transformation. Defaults to None.
            metric (func, optional): Metric to quantify distance. 
              Options are 'mi' (mutual information), 'sos' (sum of squares), 
              and 'migrad' (mutual information of the image gradient).  
              Default is 'mi'.
            mask (Volume3D, optional): volume used for masking the moving 
              volume. Defaults to None.
            target_ind (numpy.ndarray, optional): Indices in the target 
              volume that count towards the distance. Defaults to None.

        Returns:
            float: distance after transform
        """
        if self.ndim > 3:
            raise ValueError("This function is not yet available for volumes "
                             "with more than 3 dimensions")
        if metric == 'mi':
            metric = metrics.mutual_information
        elif metric == 'sos':
            metric = metrics.sum_of_squares
        elif metric == 'migrad':
            metric = metrics.mi_grad

        # Transform the moving image to the target
        moving = self.transform_to(target, transform, params, **kwargs)
        
        # Transform the moving mask
        mask_ind = None
        if mask is not None:
            mask = mask.transform_to(target, transform, params, **kwargs)
            mask_ind = np.where(mask >= 0.5)

        # Calculate metric in indices exposed by the mask(s)
        if target_ind is None and mask_ind is None:
            return metric(target.values, moving.values)
        
        if target_ind is None and mask_ind is not None:
            ind = mask_ind
        elif target_ind is not None and mask_ind is None:
            ind = target_ind
        elif target_ind is not None and mask_ind is not None:
            ind = target_ind or mask_ind
        return metric(target.values[ind], moving.values[ind])
    
        
    def transform_to(self, target, transform, params, **kwargs):
        """Transform a volume to a target volume

        Args:
            target (vreg.Volume3D): Target volume
            transform (str, optional): Coordinate transformation. 
              Possible values are 'translate', 'rotate', 'stretch', 
              'transform_rigid', 'transform_affine'.
            params (array-like, optional): Initial parameters of the 
              transformation. Defaults to None.

        Returns:
            vreg.Volume3D: transformed volume
        """
        if self.ndim > 3:
            raise ValueError("This function is not yet available for volumes "
                             "with more than 3 dimensions")
        return getattr(self, transform + '_to')(target, params, **kwargs)
    
    def transform(self, transform, params, **kwargs):
        """Transform a volume

        Args:
            transform (str, optional): Coordinate transformation. 
              Possible values are 'translate', 'rotate', 'stretch', 
              'transform_rigid', 'transform_affine'.
            params (array-like, optional): Initial parameters of the 
              transformation. Defaults to None.

        Returns:
            vreg.Volume3D: transformed volume
        """
        if self.ndim > 3:
            raise ValueError("This function is not yet available for volumes "
                             "with more than 3 dimensions")
        return getattr(self, transform)(params, **kwargs)


    def find_transform_rigid_to(
            self, target, params=None, metric=None, 
            optimizer=None, resolutions=None, 
            mask=None, target_mask=None, center=None, coords='fixed'):
        """Find the rigid transform to a static target volume.

        Args:
            target (vreg.Volume3D): Fixed target volume for the coregistration.
            params (array-like): 6-element vector with translation and  
              rotation vectors, in that order. 
            metric (func, optional): Metric to quantify goodness of alignment. 
              Options are 'mi' (mutual information), 'sos' (sum of squares), 
              and 'migrad' (mutual information of the image gradient).  
              Default is 'mi'.
            optimizer (dict, optional): Optimizer as a dictionary 
              with one key *method* specifying the method used for optimization. 
              The other items in the dictionary are any optional keywords 
              accepted by the method. Defaults to {'method':'LS'}.
            resolutions (list, optional): Resolutions to use in the 
              optimization. Defaults to [1].
            mask (Volume3D, optional): volume used for masking the moving 
              volume. Defaults to None.
            target_mask (Volume3D, optional): volume used for masking the 
              static volume. Defaults to None.
            center (str or array-like): center of rotation. If this has value 
              'com', the rotation is performed around the center of mass. 
              Alternatively this can be a 3-element vector. Defaults to None 
              (center = origin).
            coords (str or array, optional): Reference frame for the 
              coordinates of the translation, rotation and center vector, as 
              a 4x4 affine 
              array. String options are shorthand notations: 'fixed' (patient 
              reference frame), and 'volume' (volume reference frame). Defaults 
              to 'fixed'.

        Returns:
            params: The optimal values for the transformaton parameters.
        """
        if self.ndim > 3:
            raise ValueError("This function is not yet available for volumes "
                             "with more than 3 dimensions")
        return self.find_transform_to(
            target, 'transform_rigid', params=params, metric=metric, 
            optimizer=optimizer, resolutions=resolutions, 
            mask=mask, target_mask=target_mask, center=center, coords=coords)

    def find_rotate_to(
            self, target, rotation=None, metric=None, 
            optimizer=None, resolutions=None, 
            mask=None, target_mask=None, center=None, coords='fixed'):
        """Find the rigid transform to a static target volume.

        Args:
            target (vreg.Volume3D): Fixed target volume for the coregistration.
            rotation (array-like): 3-element rotation vector. 
            metric (func, optional): Metric to quantify goodness of alignment. 
              Options are 'mi' (mutual information), 'sos' (sum of squares), 
              and 'migrad' (mutual information of the image gradient).  
              Default is 'mi'.
            optimizer (dict, optional): Optimizer as a dictionary 
              with one key *method* specifying the method used for optimization. 
              The other items in the dictionary are any optional keywords 
              accepted by the method. Defaults to {'method':'LS'}.
            resolutions (list, optional): Resolutions to use in the 
              optimization. Defaults to [1].
            mask (Volume3D, optional): volume used for masking the moving 
              volume. Defaults to None.
            target_mask (Volume3D, optional): volume used for masking the 
              static volume. Defaults to None.
            center (str or array-like): center of rotation. If this has value 
              'com', the rotation is performed around the center of mass. 
              Alternatively this can be a 3-element vector. Defaults to None 
              (center = origin).
            coords (str or array, optional): Reference frame for the 
              coordinates of the translation, rotation and center vector, as 
              a 4x4 affine 
              array. String options are shorthand notations: 'fixed' (patient 
              reference frame), and 'volume' (volume reference frame). Defaults 
              to 'fixed'.

        Returns:
            params: The optimal values for the transformaton parameters.
        """
        if self.ndim > 3:
            raise ValueError("This function is not yet available for volumes "
                             "with more than 3 dimensions")
        return self.find_transform_to(
            target, 'rotate', params=rotation, metric=metric, 
            optimizer=optimizer, resolutions=resolutions, 
            mask=mask, target_mask=target_mask, center=center, coords=coords)
    
    
    def find_translate_to(
            self, target, translation=None, metric=None, 
            optimizer=None, resolutions=None, 
            mask=None, target_mask=None, coords='fixed'):
        """Find the translation to a static target volume.

        Args:
            target (vreg.Volume3D): Fixed target volume for the coregistration.
            translation (array-like, optional): Initial values for the 
              translation vector. Defaults to None.
            metric (func, optional): Metric to quantify goodness of alignment. 
              Options are 'mi' (mutual information), 'sos' (sum of squares), 
              and 'migrad' (mutual information of the image gradient).  
              Default is 'mi'.
            optimizer (dict, optional): Optimizer as a dictionary 
              with one key *method* specifying the method used for optimization. 
              The other items in the dictionary are any optional keywords 
              accepted by the method. Defaults to {'method':'LS'}.
            resolutions (list, optional): Resolutions to use in the 
              optimization. Defaults to [1].
            mask (Volume3D, optional): volume used for masking the moving 
              volume. Defaults to None.
            target_mask (Volume3D, optional): volume used for masking the 
              static volume. Defaults to None.
            coords (str or array, optional): Reference frame for the 
              coordinates of the translation vector, as a 4x4 affine 
              array. String options are shorthand notations: 'fixed' (patient 
              reference frame), and 'volume' (volume reference frame). Defaults 
              to 'fixed'.

        Returns:
            params: The optimal values for the transformaton parameters.
        """
        if self.ndim > 3:
            raise ValueError("This function is not yet available for volumes "
                             "with more than 3 dimensions")
        return self.find_transform_to(
            target, 'translate', params=translation, metric=metric, 
            optimizer=optimizer, resolutions=resolutions, 
            mask=mask, target_mask=target_mask, coords=coords)


    def _affine_matrix(self, translation, rotation, center, stretch, coords):
        # Helper function

        # Initialize
        if translation is None:
            translation = np.zeros(3)
        if rotation is None:
            rotation = np.zeros(3)
        if stretch is None:
            stretch = np.ones(3)
        if center is None:
            center = np.zeros(3)

        # Check inputs
        if 0 != np.count_nonzero(stretch <= 0):
            raise ValueError(
                "All elements of stretch must be strictly positive")
        if isinstance(coords, str):
            if coords not in ['fixed','volume']:
                raise ValueError(
                    coords + " is not a valid reference frame. The options "
                    "are 'volume' and 'fixed'.")
        elif np.shape(coords) != (4,4):
            raise ValueError(
                "coords must either be a string or an affine array")
        if isinstance(center, str):
            if center not in ['com']:
                raise ValueError(
                    "center must be a vector or the string 'com'.")
        elif np.size(center) != 3:
            raise ValueError(
                "center must either be a string or a 3-element vector.")

        # Convert to fixed reference frame
        if isinstance(coords, str):
            if coords=='fixed':
                if isinstance(center, str):
                    center = self.center_of_mass(coords='fixed')
            elif coords=='volume':
                translation = utils.volume_vector(translation, self.affine)
                rotation = utils.volume_vector(rotation, self.affine)
                if isinstance(center, str):
                    center = self.center_of_mass(coords='fixed')
                else:
                    center = utils.vol2fix(center, self.affine)
        else:
            translation = utils.volume_vector(translation, coords)
            rotation = utils.volume_vector(rotation, coords)
            if isinstance(center, str):
                center = self.center_of_mass(coords='fixed')
            else:
                center = utils.vol2fix(center, coords)
                
        # Get affine transformation
        return utils.affine_matrix(rotation, translation, stretch, center)


    def center_of_mass(self, coords='fixed'):
        """
        Center of mass.

        Args:
            coords (str or array, optional): Reference frame for the 
              coordinates of the returned vector, as a 4x4 affine array. 
              String options are shorthand notations: 'fixed' (patient 
              reference), and 'volume' (volume reference frame). Defaults 
              to 'fixed'.

        Returns:
            numpy.ndarray: 3-element vector pointing to the volume's center of 
            mass.
        """ 
        return utils.center_of_mass(self.values[:,:,:], self.affine, coords=coords)


    def reslice(self, affine=None, orient=None, rotation=None, center=None, 
                spacing=1.0, coords='fixed'):
        """Reslice the volume.

        Args:
            affine (array, optional): 4x4 affine array providing the affine 
              of the result. If this is not provided, the affine array is 
              constructed from the other arguments. Defaults to None.
            orient (str, optional): Orientation of the volume. The options are 
              'axial', 'sagittal', or 'coronal'. Alternatively the same options 
              can be provided referring to the orientation of the image planes: 
              'xy', 'yz' or 'zx'. If None is provided, the current 
              orientation of the volume is used. **Note** while 'xy' and 'yz' 
              mean exactly the same as 'axial' and 'sagittal', respectively, 
              'zx' differs from coronal in the orientation of the z-axis. While 
              'zx' forms a right-handed reference frame, 'coronal' is 
              left-handed following the common convention in medical imaging.
              Defaults to None.
            rotation (array, optional): 3-element array specifying the rotation 
              relative to *orient*, or relative to the current orientation 
              of the volume (if *orient* is None). Defaults to None.
            center (array, optional): 3-element array specifying the rotation 
              center of the new reference frame, in case a rotation is provided. 
              Defaults to None.
            spacing (float, optional): Pixel spacing in mm. Can be a 3D array or 
              a single scalar for isotropic spacing. Defaults to 1.0.
            coords (str or array, optional): Reference frame for the 
              coordinates of the rotation and center vector, as a 4x4 affine 
              array. String options are shorthand notations: 'fixed' (patient 
              reference frame), and 'volume' (volume reference frame). Defaults 
              to 'fixed'.

        Returns:
            Volume3D: resliced volume
        """
        if self.ndim > 3:
            raise ValueError("This function is not yet available for volumes "
                             "with more than 3 dimensions")
        if affine is None:
            
            # Convert to fixed coordinates
            if isinstance(coords, str):
                if coords=='volume':
                    if rotation is not None:
                        rotation = utils.volume_vector(rotation, self.affine)
                    if center is not None:
                        center = utils.vol2fix(center, self.affine)
            else:
                if rotation is not None:
                    rotation = utils.volume_vector(rotation, coords)
                if center is not None:
                    center = utils.vol2fix(center, coords)                

            # Determine affine
            if orient is None:
                transfo = utils.affine_matrix(
                    rotation=rotation, center=center, pixel_spacing=spacing)
                affine = transfo.dot(self.affine)
            else:
                affine = utils.make_affine(orient, rotation, center, spacing) 

        # Perform an active transform with the inverse
        transfo_inv = self.affine.dot(np.linalg.inv(affine))
        values, affine = mod_affine.affine_transform(
            self.values, self.affine, transfo_inv, reshape=True)
        
        # Transform the affine with the forward
        transfo = np.linalg.inv(transfo_inv)
        affine = transfo.dot(affine)

        return Volume3D(values, affine)

    
    def slice_like(self, v):
        """Slice the volume to the geometry of another volume

        Args:
            v (Volume3D): reference volume with desired orientation and shape.

        Returns:
            Volume3D: resliced volume
        """
        if self.ndim > 3:
            raise ValueError("This function is not yet available for volumes "
                             "with more than 3 dimensions")
        values, affine = mod_affine.affine_reslice(
            self.values, self.affine, 
            v.affine, output_shape=v.shape)
        return Volume3D(values, affine)

    
    def transform_affine_to(self, target, params, center=None, coords='fixed'):
        """Apply an affine transformation and reslice the result to the 
        geometry of a target volume.

        Args:
            target (vreg.Volume3D): target volume
            params (array-like): 9-element vector with translation vector,  
              rotation vector and stretch factors, in that order. 
            center (str or array-like, optional): center of rotation. If this 
              has value 'com' the rotation is performed 
              around the center of mass. Alternatively this can be a 
              3-element vector. Defaults to None (center = origin).
            coords (str or array, optional): Reference frame for the 
              coordinates of the translation, rotation and center vector, as 
              a 4x4 affine 
              array. String options are shorthand notations: 'fixed' (patient 
              reference frame), and 'volume' (volume reference frame). Defaults 
              to 'fixed'.

        Returns:
            vreg.Volume3D: transformed volume.
        """
        if self.ndim > 3:
            raise ValueError("This function is not yet available for volumes "
                             "with more than 3 dimensions")
        translation = params[:3]
        rotation = params[3:6]
        stretch = params[6:9]

        # Get affine transformation
        transform = self._affine_matrix(translation, rotation, center, 
                                        stretch, coords)

        # Apply affine transformation
        values = mod_affine.affine_transform_and_reslice(
            self.values, self.affine, target.shape, target.affine, transform,
        )
        affine = target.affine.copy()
    
        # Return volume
        return Volume3D(values, affine)
    

    def transform_rigid_to(self, target, params, center=None, coords='fixed'):
        """Apply a rigid transformation and reslice the result to the 
        geometry of a target volume.

        Args:
            target (vreg.Volume3D): target volume
            params (array-like): 6-element vector with translation and 
              rotation vectors, in that order. 
            center (str or array-like): center of rotation. If this has value 
              'com' the rotation is performed around the 
              center of mass. Alternatively this can be a 3-element vector. 
              Defaults to None (center = origin).
            coords (str or array, optional): Reference frame for the 
              coordinates of the translation, rotation and center vector, as 
              a 4x4 affine 
              array. String options are shorthand notations: 'fixed' (patient 
              reference frame), and 'volume' (volume reference frame). Defaults 
              to 'fixed'.

        Returns:
            vreg.Volume3D: transformed volume.
        """
        if self.ndim > 3:
            raise ValueError("This function is not yet available for volumes "
                             "with more than 3 dimensions")
        stretch = np.ones(3)
        params = np.concatenate((params, stretch))
        return self.transform_affine_to(target, params, coords=coords, 
                                        center=center)
    

    def rotate_to(self, target, rotation, center=None, coords='fixed'):
        """Apply a rotation and reslice the result to the 
        geometry of a target volume.

        Args:
            target (vreg.Volume3D): target volume
            rotation (array-like): 3-element rotation vector in radians. 
              Defaults to None (no rotation).
            center (str or array-like): center of rotation. If this has value 
              'com' the rotation is performed around the 
              center of mass. Alternatively this can be a 3-element vector. 
              Defaults to None (center = origin).
            coords (str or array, optional): Reference frame for the 
              coordinates of the rotation and center vector, as a 4x4 affine 
              array. String options are shorthand notations: 'fixed' (patient 
              reference frame), and 'volume' (volume reference frame). Defaults 
              to 'fixed'.

        Returns:
            vreg.Volume3D: transformed volume.
        """
        if self.ndim > 3:
            raise ValueError("This function is not yet available for volumes "
                             "with more than 3 dimensions")
        translation = np.zeros(3)
        stretch = np.ones(3)
        params = np.concatenate((translation, rotation, stretch))
        return self.transform_affine_to(target, params, center=center, 
                                        coords=coords)


    def translate_to(self, target, translation, coords='fixed', dir='xyz'):
        """Apply a translation and reslice the result to the 
        geometry of a target volume.

        Args:
            target (vreg.Volume3D): target volume
            translation (array-like): translation vector (mm) with 1, 2 or 3 
              elements depending on the value of *dir*. 
            coords (str or array, optional): Reference frame for the 
              coordinates of the translation vector, as a 4x4 affine 
              array. String options are shorthand notations: 'fixed' (patient 
              reference frame), and 'volume' (volume reference frame). Defaults 
              to 'fixed'.
            dir (str, optional): Allowed directions of the translation. The 
              options are 'xyz' (3D translation), 'xy' (2D in-slice 
              translation) and 'z' (through-slice translation). Defaults to 
              'xyz'.

        Returns:
            vreg.Volume3D: transformed volume.
        """
        if self.ndim > 3:
            raise ValueError("This function is not yet available for volumes "
                             "with more than 3 dimensions")
        if dir=='xy':
            translation = np.concatenate((translation, [0]))
        elif dir=='z':
            translation = np.concatenate(([0,0], translation))
        rotation = np.zeros(3)
        stretch = np.ones(3)
        params = np.concatenate((translation, rotation, stretch))
        return self.transform_affine_to(target, params, coords=coords)
    

    def stretch_to(self, target, stretch):
        """Stretch and reslice to the geometry of a 
        target volume.

        Args:
            target (vreg.Volume3D): target volume
            stretch (array-like): 3-element stretch vector with strictly 
              positive dimensionless values (1 = no stretch).

        Returns:
            vreg.Volume3D: transformed volume.
        """
        if self.ndim > 3:
            raise ValueError("This function is not yet available for volumes "
                             "with more than 3 dimensions")
        translation = np.zeros(3)
        rotation = np.zeros(3)
        params = np.concatenate((translation, rotation, stretch))
        return self.transform_affine_to(target, params)
    

    def transform_affine(self, params, center=None, values=False, 
                         reshape=False, coords='fixed'):
        """Apply an affine transformation.

        Args:
            params (array-like): 9-element vector with translation vector,  
              rotation vector and stretch factors, in that order.
            center (str or array-like): center of rotation. If this has value 
              'com', the rotation is performed around the center of mass. 
              Alternatively this can be a 3-element vector. Defaults to None (
              center = origin).
            values (bool, optional): If set to True, the values are 
              transformed. Otherwise the affine is transformed. Defaults to 
              False.
            reshape (bool, optional): When values=True, reshape=False will 
              retain the shape and location of the volume. With reshape=True, 
              the volume will be reshaped to fit the transformed values. This 
              keyword is ignored when values=False. Defaults to False.
            coords (str or array, optional): Reference frame for the 
              coordinates of the translation, rotation and center vector, as 
              a 4x4 affine 
              array. String options are shorthand notations: 'fixed' (patient 
              reference frame), and 'volume' (volume reference frame). Defaults 
              to 'fixed'.

        Returns:
            vreg.Volume3D: transformed volume.
        """
        if self.ndim > 3:
            if values:
                raise ValueError(
                    "This function is not yet available for volumes "
                    "with more than 3 dimensions"
                )
        translation = params[:3]
        rotation = params[3:6]
        stretch = params[6:9]

        # Get affine transformation
        transform = self._affine_matrix(translation, rotation, center, 
                                        stretch, coords)

        # Apply affine transformation
        if values:
            values, affine = mod_affine.affine_transform(
                self.values, self.affine, transform, reshape)
        else:
            values = self.values.copy()
            affine = transform.dot(self.affine)
        return Volume3D(values, affine, self.coords, self.dims, self.prec)
            

    def transform_rigid(self, params, values=False, reshape=False, 
                        center=None, coords='fixed'):
        """Apply a rigid transformation.

        Args:
            params (array-like): 6-element vector with translation and  
              rotation vectors, in that order. 
            values (bool, optional): If set to True, the values are 
              transformed. Otherwise the affine is transformed. Defaults to 
              False.
            reshape (bool, optional): When values=True, reshape=False will 
              retain the shape and location of the volume. With reshape=True, 
              the volume will be reshaped to fit the transformed values. This 
              keyword is ignored when values=False. Defaults to False.
            center (str or array-like): center of rotation. If this has value 
              'com', the rotation is performed around the center of mass. 
              Alternatively this can be a 3-element vector. Defaults to None (
              center = origin).
            coords (str or array, optional): Reference frame for the 
              coordinates of the translation, rotation and center vector, as 
              a 4x4 affine 
              array. String options are shorthand notations: 'fixed' (patient 
              reference frame), and 'volume' (volume reference frame). Defaults 
              to 'fixed'.

        Returns:
            vreg.Volume3D: transformed volume.
        """
        if self.ndim > 3:
            raise ValueError("This function is not yet available for volumes "
                             "with more than 3 dimensions")
        stretch = np.ones(3)
        params = np.concatenate((params, stretch))
        return self.transform_affine(params, center=center, values=values, 
                                     reshape=reshape, coords=coords)
        

    def rotate(self, rotation, center=None, values=False, reshape=False, 
               coords='fixed'):
        """Rotate the volume.

        Args:
            rotation (array-like): 3-element rotation vector in radians. 
            center (str or array-like): center of rotation. If this has value 
              'com', the rotation is performed around the center of mass. 
              Alternatively this can be a 3-element vector. Defaults to None (
              center = origin).
            values (bool, optional): If set to True, the values are 
              transformed. Otherwise the affine is transformed. Defaults to 
              False.
            reshape (bool, optional): When values=True, reshape=False will 
              retain the shape and location of the volume. With reshape=True, 
              the volume will be reshaped to fit the transformed values. This 
              keyword is ignored when values=False. Defaults to False.
            coords (str or array, optional): Reference frame for the 
              coordinates of the rotation and center vector, as a 4x4 affine 
              array. String options are shorthand notations: 'fixed' (patient 
              reference frame), and 'volume' (volume reference frame). Defaults 
              to 'fixed'.

        Returns:
            vreg.Volume3D: transformed volume.
        """
        if self.ndim > 3:
            raise ValueError("This function is not yet available for volumes "
                             "with more than 3 dimensions")
        translation = np.zeros(3)
        stretch = np.ones(3)
        params = np.concatenate((translation, rotation, stretch))
        return self.transform_affine(params, values=values, reshape=reshape, 
                                     center=center, coords=coords)


    def translate(self, translation, values=False, reshape=False, 
                  coords='fixed', dir='xyz'):
        """Translate the volume.

        Args:
            translation (array-like): translation vector (mm) with 1, 2 or 3 
              elements depending on the value of *dir*. 
            values (bool, optional): If set to True, the values are 
              transformed. Otherwise the affine is transformed. Defaults to 
              False.
            reshape (bool, optional): When values=True, reshape=False will 
              retain the shape and location of the volume. With reshape=True, 
              the volume will be reshaped to fit the transformed values. This 
              keyword is ignored when values=False. Defaults to False.
            coords (str or array, optional): Reference frame for the 
              coordinates of the translation vector, as a 4x4 affine array. 
              String options are shorthand notations: 'fixed' (patient 
              reference), and 'volume' (volume reference frame). Defaults 
              to 'fixed'.
            dir (str, optional): Allowed directions of the translation. The 
              options are 'xyz' (3D translation), 'xy' (2D in-slice 
              translation) and 'z' (through-slice translation). Defaults to 
              'xyz'.

        Returns:
            vreg.Volume3D: transformed volume.
        """
        if self.ndim > 3:
            if values:
                raise ValueError(
                    "Translating values is not yet available for volumes "
                    "with more than 3 dimensions."
                )
        if dir=='xy':
            translation = np.concatenate((translation, [0]))
        elif dir=='z':
            translation = np.concatenate(([0,0], translation))
        rotation = np.zeros(3)
        stretch = np.ones(3)
        params = np.concatenate((translation, rotation, stretch))
        return self.transform_affine(params, values=values, reshape=reshape, 
                                     coords=coords)


    def stretch(self, stretch, values=False, reshape=False):
        """Stretch the volume.

        Args:
            stretch (array-like): 3-element stretch vector with strictly 
              positive dimensionless values (1 = no stretch). 
            values (bool, optional): If set to True, the values are 
              transformed. Otherwise the affine is transformed. Defaults to 
              False.
            reshape (bool, optional): When values=True, reshape=False will 
              retain the shape and location of the volume. With reshape=True, 
              the volume will be reshaped to fit the transformed values. This 
              keyword is ignored when values=False. Defaults to False.

        Returns:
            vreg.Volume3D: transformed volume.
        """
        if self.ndim > 3:
            raise ValueError("This function is not yet available for volumes "
                             "with more than 3 dimensions")
        translation = np.zeros(3)
        rotation = np.zeros(3)
        params = np.concatenate((translation, rotation, stretch))
        return self.transform_affine(params, values=values, reshape=reshape)


    def truncate(self, shape):
        """Truncate the volume to a smaller shape.

        Args:
            shape (array-like): 3-element array with the new shape. Each 
              dimension must be equal or smaller than the current shape.

        Returns:
            vreg.Volume3D: truncated volume.
        """
        if self.ndim > 3:
            return Volume3D(
                self.values[:shape[0], :shape[1], :shape[2], :],
                self.affine)
        return Volume3D(
            self.values[:shape[0], :shape[1], :shape[2]],
            self.affine)


        
def volume(values:np.ndarray, affine:np.ndarray=None, 
           coords:np.ndarray=None, dims:list=None, prec:int=None, 
           orient='axial', rotation=None, center=None, spacing=1.0, 
           pos=[0,0,0]):
    """Create a new volume from an array of values

    Args:
        values (array): 2D or 3D array of values.
        affine (array, optional): 4x4 affine array. If this is not provided, 
          the affine array is constructed from the other arguments. Defaults 
          to None.
        coords (array, optional): Array with coordinates for volumes that 
          have more than 3 dimensions (non-spatial dimensions). If values 
          has N non-spatial dimensions, coords can be an N-dimensionsal 
          coordinate array or a tuple of N 1D arrays. Values of the 
          coords array can have any type including strings or tuples.
        orient (str, optional): Orientation of the volume. The options are 
          'axial', 'sagittal', or 'coronal'. Alternatively the same options 
          can be provided referring to the orientation of the image planes: 
          'xy', 'yz' or 'zx'. **Note** while 'xy' and 'yz' mean exactly the 
          same as 'axial' and 'sagittal', respectively, 'zx' differs from 
          coronal in the orientation of the z-axis. While 'zx' forms a 
          right-handed reference frame, 'coronal' is left-handed following 
          the common convention in medical imaging.Defaults to 'axial.
        rotation (array, optional): 3-element array specifying a rotation 
          relative to *orient*. Defaults to None.
        center (array, optional): 3-element array specifying the rotation 
          center, in case a rotation is provided. Defaults to None.
        spacing (float, optional): Pixel spacing in mm. Can be a 3D array or 
          a single scalar for isotropic spacing. Defaults to 1.0.
        pos (list, optional): Position of the upper left-hand corner in mm. 
          Defaults to [0,0,0].

    Returns:
        vreg.Volume3D: volume with required orientation and position.
    """

    if affine is None:
        # Define orient=None and check that the user has defined an orientation
        affine = utils.make_affine(orient, rotation, center, spacing, pos) 
    if values.ndim==1:
        # This can only be done meaningfully if orient is specified
        values = np.expand_dims(values, -1)
    if values.ndim==2:
        # This can only be done meaningfully if orient is specified
        values = np.expand_dims(values, -1)
    if values.ndim>3:
        if coords is None:
            coords = [np.arange(d) for d in values.shape[3:]]
            coords = np.meshgrid(*coords, indexing='ij')
            coords = np.stack(coords, axis=0, dtype=object) # coordinates for volume i, j are coords[:,i,j]
        elif isinstance(coords, tuple):
            coords = np.meshgrid(*coords, indexing='ij')
            coords = np.stack(coords, axis=0, dtype=object)   
        else:         
            coords = np.asarray(coords, dtype=object)

    return Volume3D(values, affine, coords, dims, prec)



def zeros(shape, affine=None, orient='axial', spacing=1.0, pos=[0,0,0], 
          **kwargs):
    """Return a new volume of given shape and affine, filled with zeros.

    Args:
        shape (int or tuple of ints): Shape of the new array, e.g., (2, 3) or 2.
        affine (array, optional): 4x4 affine array. If this is not provided, 
          the affine array is constructed from the other arguments. Defaults 
          to None.
        orient (str, optional): Orientation of the volume. The options are 
          'axial', 'sagittal', or 'coronal'. Alternatively the same options 
          can be provided referring to the orientation of the image planes: 
          'xy', 'yz' or 'zx'. **Note** while 'xy' and 'yz' mean exactly the 
          same as 'axial' and 'sagittal', respectively, 'zx' differs from 
          coronal in the orientation of the z-axis. While 'zx' forms a 
          right-handed reference frame, 'coronal' is left-handed following 
          the common convention in medical imaging. Defaults to 'axial'.
        spacing (float, optional): Pixel spacing in mm. Can be a 3D array or 
          a single scalar for isotropic spacing. Defaults to 1.0.
        pos (list, optional): Position of the upper left-hand corner in mm. 
          Defaults to [0,0,0].
        kwargs: Any keyword arguments accepted by `numpy.zeros`.

    Returns:
        Volume3D: vreg.Volume3D with zero values.
    """
    values = np.zeros(shape, **kwargs)
    return volume(values, affine, orient, spacing, pos)


def full(shape, fill_value, affine=None, orient='axial', spacing=1.0, 
         pos=[0,0,0], **kwargs):
    """Return a new volume of given shape and affine, filled with *fill_value*.

    Args:
        shape (int or tuple of ints): Shape of the new array, e.g., (2, 3) or 2.
        fill_value (float): value to fill the array.
        affine (array, optional): 4x4 affine array. If this is not provided, 
          the affine array is constructed from the other arguments. Defaults 
          to None.
        orient (str, optional): Orientation of the volume. The options are 
          'axial', 'sagittal', or 'coronal'. Alternatively the same options 
          can be provided referring to the orientation of the image planes: 
          'xy', 'yz' or 'zx'. **Note** while 'xy' and 'yz' mean exactly the 
          same as 'axial' and 'sagittal', respectively, 'zx' differs from 
          coronal in the orientation of the z-axis. While 'zx' forms a 
          right-handed reference frame, 'coronal' is left-handed following 
          the common convention in medical imaging. Defaults to 'axial'.
        spacing (float, optional): Pixel spacing in mm. Can be a 3D array or 
          a single scalar for isotropic spacing. Defaults to 1.0.
        pos (list, optional): Position of the upper left-hand corner in mm. 
          Defaults to [0,0,0].
        kwargs: Any keyword arguments accepted by `numpy.full`.

    Returns:
        Volume3D: vreg.Volume3D with *fill_value* values.
    """
    values = np.full(shape, fill_value, **kwargs)
    return volume(values, affine, orient, spacing, pos)


def zeros_like(v:Volume3D):
    """Return a new volume with same shape and affine as v, filled with zeros.

    Args:
        v (int or tuple of ints): Shape of the new array, e.g., (2, 3) or 2.

    Returns:
        Volume3D: vreg.Volume3D with zero values.
    """
    values = np.zeros(v.shape, dtype=v.values.dtype)
    return volume(values, v.affine.copy())


def full_like(v:Volume3D, fill_value):
    """Return a new volume with same shape and affine as v, filled with 
    *fill_value*.

    Args:
        v (int or tuple of ints): Shape of the new array, e.g., (2, 3) or 2.
        fill_value (float): value to fill the array.

    Returns:
        Volume3D: vreg.Volume3D with *fill_value* values.
    """
    values = np.full_like(v.values, fill_value)
    return volume(values, v.affine.copy())


def concatenate(vols, prec=None):
    #TODO remove move keyword
    #TODO remove axis keyword. Isntead try each axis until one is found that fits.
    """Join a sequence of volumes along x-, y-, or z-axis.

    Volumes can only be joined up if they have the same shape 
    (except along the axis of concatenation), the same orientation and 
    the same voxel size.

    Args:
        vols (sequence of volumes): Volumes to concatenate.
        prec (int, optional): precision to consider when comparing positions 
          and orientations of volumes. All differences are rounded off to this 
          digit before comparing them to zero. If this is not specified, 
          floating-point precision is used. Defaults to None.

    Returns:
        Volume3D: The concatenated volume.
    """
    if isinstance(vols, Volume3D):
        return vols
    
    # Check arguments
    if not np.iterable(vols):
        raise ValueError(
            "vreg.stack() requires an iterable as argument.")

    # Check that all volumes have the same shape and orientation
    if prec is None:
        mat = [v.affine[:3,:3].tolist() for v in vols]  
    else:
        mat = [np.around(v.affine[:3,:3], prec).tolist() for v in vols]
    mat = [x for i, x in enumerate(mat) if i==mat.index(x)]
    if len(mat) > 1:
        raise ValueError(
            "Volumes with different orientations or voxel sizes cannot be "
            "concatenated."
        )

    # TODO: Generalize: they do not have to be in the correct order
    for axis in [0,1,2]:
        if _aligned_along_axis(vols, axis, prec):
            affine = vols[0].affine
            values = np.concatenate([v.values for v in vols], axis=axis)
            return Volume3D(values, affine)  
    raise ValueError(
        "Volumes cannot be concatenated. They are not aligned in "
        "any direction."
    )


def _aligned_along_axis(vols, axis, prec):
    mat = vols[0].affine[:3,:3]
    pos = [v.affine[:3,3] for v in vols]
    concat_vec = mat[:,axis]
    for i, v in enumerate(vols[:-1]):
        pos_next = pos[i] + concat_vec*v.shape[axis]
        dist = np.linalg.norm(pos[i+1]-pos_next)
        if prec is not None:
            dist = np.around(dist, prec)
        if dist > 0:
            return False
    return True


def stack(vols, axis=3, prec=None):
    """Stack a sequence volumes at the same location along a new time axis.

    Args:
        vols (sequence of volumes): Volumes to concatenate.
        axis (int, optional): The axis along which the volumes will be 
          stacked. This must be larger than 2.
        prec (int, optional): precision to consider when comparing positions 
          and orientations of volumes. All differences are rounded off to this 
          digit before comparing them to zero. If this is not specified, 
          floating-point precision is used. Defaults to None.

    Returns:
        Volume3D: The concatenated volume.
    """
    if isinstance(vols, Volume3D):
        return vols
    
    # Check arguments
    if not np.iterable(vols):
        raise ValueError(
            "vreg.stack() requires an iterable as argument.")
    if axis in [0,1,2]:
        raise ValueError(
            "Volumes cannot be stacked along a new space dimension. "
            "Consider using concatenate instead.")

    # Check that all volumes have the same shape and orientation
    if prec is None:
        mat = [v.affine[:3,:3].tolist() for v in vols]  
    else:
        mat = [np.around(v.affine[:3,:3], prec).tolist() for v in vols]
    mat = [x for i, x in enumerate(mat) if i==mat.index(x)]
    if len(mat) > 1:
        raise ValueError(
            "Volumes with different orientations or voxel sizes cannot be "
            "stacked."
        )
    
    # Check that all volumes are at the same position  
    for v in vols[1:]:
        dist = v.affine[:3,3] - vols[0].affine[:3,3]
        dist = np.linalg.norm(dist)
        if prec is not None:
            dist = np.around(dist, prec)
        if dist > 0:
            raise ValueError(
                "Volumes cannot be concatenated in a time direction. "
                "They are not all at the same position. Set move=True "
                "if you want to allow them to move to the correct "
                "position.")

    # Determine concatenation and return new volume
    affine = vols[0].affine
    values = np.stack([v.values for v in vols], axis=axis)
    return Volume3D(values, affine)  


def join(vols:np.ndarray): #concat->stack, join as a generalized stack, stack-> concat
    """Join multiple volumes into a single volume.

    This is the opposite operation to split

    Args:
        vols (array of volumes): Volumes to join. 

    Returns:
        Volume3D: A single volume.
    """

    # Concatenate in space
    shape = vols.shape
    vols = vols.reshape((shape[0],-1))
    vols_stack = []
    for k in range(vols.shape[1]):
        vstack = concatenate(vols[:,k], prec=2) # TODO use internal precision 
        vols_stack.append(vstack)
    if len(shape) == 1:
        return vols_stack[0]
    else:
        vols = np.asarray(vols_stack).reshape(shape[1:])
        
    # Stack along the other dimensions
    axis = 3
    while True:
        shape = vols.shape
        vols = vols.reshape((shape[0],-1))
        vols_stack = []
        for k in range(vols.shape[1]):
            vstack = stack(vols[:,k], axis=axis, prec=3) 
            vols_stack.append(vstack)
        if len(shape) == 1:
            return vols_stack[0]
        else:
            vols = np.asarray(vols_stack).reshape(shape[1:])
            axis += 1


def mean(vol:Volume3D, axis=None):
    vals = np.mean(vol.values, axis=axis)
    if axis is None:
        vals = np.full(vol.shape, vals)
        return Volume3D(vals, vol.affine.copy())
    elif axis < 3:
        vals = np.expand_dims(vals, axis=axis)
        return Volume3D(vals, vol.affine.copy())
    if axis >= 3:
        dims = [d for i, d in enumerate(vol.dims) if i != axis-3]
        coords = np.take(vol.coords, indices=0, axis=1+axis-3)
        if dims==[]:
            dims = None
            coords = None
        else:
            # THIS NEEDS DEBUGGING
            inds = [i for i in range(coords.shape[0]) if i != axis]
            coords = np.take(coords, indices=inds, axis=0)
        mean_vol = Volume3D(vals, vol.affine.copy(), coords, dims)
    return mean_vol

# def asarray(vol):
    
#     if isinstance(vol, Volume3D):
#         return vol.values
    
#     vol = np.asarray(vol)

#     # Check that all affines are the same
#     uniq = np.unique([v.affine for v in vol.reshape(-1)])
#     if uniq.size>1:
#         raise ValueError("Cannot extract an array from volumes that have "
#                          "different affines.")
    
#     # Check that all shapes are the same
#     uniq = np.unique([v.shape for v in vol.reshape(-1)])
#     if uniq.size>1:
#         raise ValueError("Cannot extract an array from volumes that have "
#                          "different shapes.")

#     # Build n-dimensional array
#     shape = vol.shape
#     arr = np.stack([v.values for v in vol.reshape(-1)], axis=-1)
#     return arr.reshape(arr.shape[:3] + shape)


# def asvolume(arr:np.ndarray, affine):
#     if arr.ndim <= 3:
#         return volume(arr, affine)
#     shape = arr.shape[3:]
#     arr = arr.reshape((arr.shape[:3], -1))
#     vol = [volume(arr[...,k], affine) for k in range(arr.shape[-1])]
#     return np.asarray(vol).reshape(shape)


def _take_view(arr, i, axis):
    # alternative to np.take() which returns a view
    # Create a tuple of slice(None) (which selects all elements) for each axis
    slc = [slice(None)] * arr.ndim
    # Replace the desired axis with the scalar index
    slc[axis] = i
    return arr[tuple(slc)]  # Returns a view

def _take_view_keepdims(arr, i, axis):
    slc = [slice(None)] * arr.ndim
    slc[axis] = slice(i, i + 1)
    return arr[tuple(slc)]

def _take_keepdims(arr, i, axis):
    slc = [slice(None)] * arr.ndim
    slc[axis] = slice(i, i + 1)
    return arr[tuple(slc)].copy()







