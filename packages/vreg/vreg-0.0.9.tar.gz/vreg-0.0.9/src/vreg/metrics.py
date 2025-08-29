import numpy as np

# default metrics
# ---------------


def cov_mask(static, transformed, nan=None):
    # transformed is here a mask image.
    if nan is None:
        masked = static[transformed > 0.01]
    else:
        masked = static[(transformed > 0.01) & (transformed != nan)]
    return np.std(masked)/np.mean(masked)


def sum_of_squares(static, transformed, nan=None):
    if nan is not None:
        i = np.where(transformed != nan)
        st, tr = static[i], transformed[i]
    else:
        st, tr = static, transformed
    return np.sum(np.square(st-tr))
    

def mutual_information(static, transformed, nan=None):

    # Mask if needed
    if nan is not None:
        i = np.where(transformed != nan)
        st, tr = static[i], transformed[i]
    else:
        st, tr = static, transformed
    # Calculate 2d histogram
    hist_2d, _, _ = np.histogram2d(st.ravel(), tr.ravel(), bins=20)
    # Convert bins counts to probability values
    pxy = hist_2d / float(np.sum(hist_2d))
    px = np.sum(pxy, axis=1) # marginal for x over y
    py = np.sum(pxy, axis=0) # marginal for y over x
    px_py = px[:, None] * py[None, :] # Broadcast to multiply marginals
    # Now we can do the calculation using the pxy, px_py 2D arrays
    nzs = pxy > 0 # Only non-zero pxy values contribute to the sum
    return -np.sum(pxy[nzs] * np.log(pxy[nzs] / px_py[nzs]))


def mi_grad(static, transformed, nan=None):
    gstatic = np.gradient(np.squeeze(static))
    gtransf = np.gradient(np.squeeze(transformed))
    gstatic = np.linalg.norm(np.stack(gstatic), axis=0)
    gtransf = np.linalg.norm(np.stack(gtransf), axis=0)
    # support = np.squeeze(static) > 1e-2
    # gstatic = gstatic[support]
    # gtransf = gtransf[support]
    # gstatic /= np.linalg.norm(gstatic)
    # gtransf /= np.linalg.norm(gtransf)
    return mutual_information(gstatic, gtransf, nan=nan)

def sos_grad(static, transformed, nan=None):
    gstatic = np.gradient(np.squeeze(static))
    gtransf = np.gradient(np.squeeze(transformed))
    gstatic = np.linalg.norm(np.stack(gstatic), axis=0)
    gtransf = np.linalg.norm(np.stack(gtransf), axis=0)
    gstatic /= np.linalg.norm(gstatic)
    gtransf /= np.linalg.norm(gtransf)
    return sum_of_squares(gstatic, gtransf, nan=nan)