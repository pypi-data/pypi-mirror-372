import numpy as np
import scipy.optimize
from tqdm import tqdm
# import dask
# from dask.diagnostics import ProgressBar

from vreg.scipy_least_squares import least_squares

# @dask.delayed
# def _compute_cost(cost_function, x, i, *args):
#     parameters = np.array([xp.ravel()[i] for xp in x])
#     return cost_function(parameters, *args)

# @dask.delayed
# def _opt_params(x, cost):
#     i = np.argmin(cost)
#     return np.array([xp.ravel()[i] for xp in x])

# def _minimize_brute(cost_function, args=None, grid=None, 
#                    desc='Performing brute-force optimization', progress=True):
#     x = [np.linspace(p[0], p[1], p[2]) for p in grid]
#     x = np.meshgrid(*tuple(x), indexing='ij')
#     cost = []
#     for i in range(x[0].size):
#     #for i in tqdm(range(x[0].size), desc=desc, disable=not progress):
#         ci = _compute_cost(cost_function, x, i, *args)
#         cost.append(ci)
#     opt = _opt_params(x, cost)
#     #with ProgressBar():
#         #opt = opt.compute(scheduler='single-threaded')
#     opt = opt.compute(scheduler='single-threaded')
#     return opt

def minimize(goodness_of_alignment, parameters, args=(), method='LS', **kwargs):
    "General minimization function including scipy and custom methods"

    if method == 'GD':
        return minimize_gd(goodness_of_alignment, parameters, args=args, **kwargs)
    elif method=='brute':
        return minimize_brute(goodness_of_alignment, args=args, **kwargs)
    elif method=='brute-LS':
        return minimize_brute_ls(goodness_of_alignment, args=args, **kwargs)
    elif method=='ibrute':
        return minimize_iterative_brute(goodness_of_alignment, args=args, **kwargs)
    elif method=='LS':
        res = least_squares(goodness_of_alignment, parameters, args=args, **kwargs)
        return res.x
    elif method == 'min':
        res = scipy.optimize.minimize(goodness_of_alignment, parameters, args=args, **kwargs)
        return res.x
    else:
        raise ValueError(
            "Optimization method " + str(method) + " is not recognized."
            "The options are 'GD', 'brute', 'ibrute', 'LS' or 'min'.")

def minimize_brute_ls(cost_function, args=None, grid=None, **kwargs):
    params = minimize_brute(cost_function, args=args, grid=grid)
    res = least_squares(cost_function, params, args=args, **kwargs)
    return res.x

def minimize_brute(
        cost_function, args=None, grid=None, 
        desc='Performing brute-force optimization', progress=False, 
        callback=None):
    #grid = [[start, stop, num], [start, stop, num], ...]
    x = [np.linspace(p[0], p[1], p[2]) for p in grid]
    x = np.meshgrid(*tuple(x), indexing='ij')
    for i in tqdm(range(x[0].size), desc=desc, disable=not progress):
        if callback is not None:
            callback(100*(i+1)/x[0].size)
        parameters = np.array([xp.ravel()[i] for xp in x])
        cost = cost_function(parameters, *args)
        if i==0:
            minimum = cost
            par_opt = parameters
        elif cost<minimum:
            minimum = cost
            par_opt = parameters
    return par_opt


def minimize_iterative_brute(goodness_of_alignment, args=None, num=3, nit=5, bounds=None):
    #options = {'num':3, 'nit':5, 'bounds':[[start, stop], [start, stop], ...]}
    grid = [[b[0], b[1], num] for b in bounds]
    parameters = minimize_brute(goodness_of_alignment, args=args, grid=grid)
    for _ in range(nit-1):
        dist = [(g[1]-g[0])/(num-1) for g in grid]
        grid = [[p-dist[i], p+dist[i], num] for i, p in enumerate(parameters)]
        parameters = minimize_brute(goodness_of_alignment, args=args, grid=grid)
    return parameters


def minimize_gd(
        cost_function, parameters, args=None, callback=None, max_iter=100, 
        bounds=None, gradient_step=None, tolerance=0.1, scale_down=5.0, 
        scale_up=1.5, stepsize_max=1000.0):

    # Set default values for global options
    if gradient_step is None:
        gradient_step = np.ones(parameters.shape)

    stepsize = 1.0 # initial stepsize
    n_iter = 0
    cost = cost_function(parameters, *args)
    while True:
        n_iter+=1
        print('iteration: ', n_iter)
        grad = gradient(cost_function, parameters, cost, gradient_step, bounds, *args)
        parameters, stepsize, cost = line_search(
            cost_function, grad, parameters, stepsize, cost, bounds, *args, 
            tolerance=tolerance, scale_down=scale_down, scale_up=scale_up, 
            stepsize_max=stepsize_max)
        if callback is not None:
            callback(parameters)
        if cost == 0:
            return parameters
        if stepsize == 0:
            return parameters
        if n_iter == max_iter:
            return parameters


def gradient(cost_function, parameters, f0, step, bounds, *args):
    grad = np.empty(parameters.shape)
    for i in range(parameters.size):
        c = np.unravel_index(i, parameters.shape)
        pc = parameters[c]
        sc = step[c]
        parameters[c] = pc+sc
        parameters = project_on(parameters, bounds, coord=c)
        fp = cost_function(parameters, *args)
        parameters[c] = pc-sc
        parameters = project_on(parameters, bounds, coord=c)
        fn = cost_function(parameters, *args)
        parameters[c] = pc
        grad[c] = (fp-fn)/2
        #grad[i] = (fp-fn)/(2*step[i])
        #grad[i] = stats.linregress([-step[i],0,step[i]], [fn,f0,fp]).slope

    # Normalize the gradient
    grad_norm = np.linalg.norm(grad)
    if grad_norm == 0:
        return grad 
    grad /= grad_norm
    grad = np.multiply(step, grad)

    return grad


def project_on(par, bounds, coord=None):
    if bounds is None:
        return par
    if len(bounds) != len(par):
        msg = 'Parameter and bounds must have the same length'
        raise ValueError(msg)
    if coord is not None:   # project only that index
        pc = par[coord]
        bc = bounds[coord]
        if pc <= bc[0]:
            pc = bc[0]
        if pc >= bc[1]:
            pc = bc[1]
    else:   # project all indices
        for i in range(par.size):
            c = np.unravel_index(i, par.shape)
            pc = par[c]
            bc = bounds[c]
            if pc <= bc[0]:
                par[c] = bc[0]
            if pc >= bc[1]:
                par[c] = bc[1]
    return par


def line_search(
        cost_function, grad, p0, stepsize0, f0, bounds, *args, 
        tolerance=0.1, scale_down=5.0, scale_up=1.5, stepsize_max=1000.0):

    # Initialize stepsize to current optimal stepsize
    stepsize_try = stepsize0 / scale_down
    p_init = p0.copy()

    # backtrack in big steps until reduction in cost
    while True:

        # Take a step and evaluate the cost
        p_try = p_init - stepsize_try*grad 
        p_try = project_on(p_try, bounds)
        f_try = cost_function(p_try, *args)

        print('cost: ', f_try, ' stepsize: ', stepsize_try, ' par: ', p_try)

        # If a reduction in cost is found, move on to the next part
        if f_try < f0:
            break

        # Otherwise reduce the stepsize and try again
        else:
            stepsize_try /= scale_down

        # If the stepsize has been reduced below the resolution without reducing the cost,
        # then the initial values were at the minimum (stepsize=0).
        if stepsize_try < tolerance: 
            return p0, 0, f0 # converged
        
    if stepsize_try < tolerance: 
        return p_try, 0, f_try # converged

    # If a reduction in cost has been found, then refine it 
    # by moving forward in babysteps until the cost increases again.
    while True:
        
        # Update the current optimum
        stepsize0 = stepsize_try
        f0 = f_try
        p0 = p_try

        # Take a baby step and evaluate the cost
        stepsize_try *= scale_up
        p_try = p_init - stepsize_try*grad
        p_try = project_on(p_try, bounds)
        f_try = cost_function(p_try, *args)

        print('cost: ', f_try, ' stepsize: ', stepsize_try, ' par: ', p_try)

        # If the cost has increased then a minimum was found
        if f_try >= f0:
            return p0, stepsize0, f0

        # emergency stop
        if stepsize_try > stepsize_max:
            msg = 'Line search failed to find a minimum'
            raise ValueError(msg) 