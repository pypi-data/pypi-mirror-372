import os
import numpy as np

import vreg

from vreg.data import DATASETS


def test_fetch():
    mask = vreg.fetch('left_kidney')
    assert 1504 == np.sum(mask.values[:,:,2])
    vreg.fetch(clear_cache=True)
    vreg.fetch(download_all=True)
    vreg.fetch(download_all=True)

# def convert():
#     tmp = os.path.join(os.getcwd(), 'tmp')
#     os.makedirs(tmp, exist_ok=True)
#     for data in ['T1', 'T2star']:
#         vol = vreg.fetch(data)
#         for i, v, in enumerate(vol):
#             vreg.write_nifti(v, f"{os.path.join(tmp, data)}_{str(i).zfill(2)}")

if __name__ == '__main__':

    #test_fetch()
    vreg.fetch(clear_cache=True)
    #convert()