
"""
imlib is a file intended to host internal function for the im sub-module, not to be available outside the package and
keep it clean.
"""
import warnings
import numpy as np
from scipy import sparse


def _binned_statistic(x, values, bin_width=1., xrange=None, edges=None, funcs=None):
    # type: (np.array, np.array, float, tuple(float, float), np.array, list(callable)) -> dict
    """
    source: https://stackoverflow.com/questions/26783719/efficiently-get-indices-of-histogram-bins-in-python

    Given data, return the radial profile. For each bin, the left edge is included, the right edge excluded, apart from
    the last bin where both edges are included

    Note on speed:
        By default, all functions are processed and it can seems not optimized to do 7 functions while you're only
        interested in the mean.

        For a test image 1000x1000, the time of this function was 0.052s. Rewriting the function to do only one
        function decreased the time to 0.05s (i.e 5% improvement)

    Sampling example:
    r     0.5   1.5   2.5   3.5
    bins [0;1[ [1;2[ [2;3[ [3;4]

    Note that due to the discrete sampling of pixels, the bin_center is not necessarily at the center of each bin, but
    is rather the mean of all radius for all selected pixels.

    Parameters
    ----------
    :param x: nd.array
        metric over which we want to spread the bins evenly. array shape must
        be similar to 'values'

    :param values: nd.ma.MaskedArray
        input data

    :param bin_width: default 1. Ignored if edges is set.

    :param xrange: (float, float)
        min and max of the bin sampling (cut-off of the real bin range)
        Ignored if edges is set

    :param edges: nd.array
        list of n+1 edges for the n bins. If set, bin_width and xrange are ignored

    Output
    ------
    :return r: dict
        dictionnary with an array of results for the following input keys:
        ["mean", "std", "median", "var", "max", "sum", "r", "size"]

    """
    if funcs is None:
        funcs = [np.nanmean, np.nanstd, np.nanmedian, np.nanvar, np.nanmax, np.nansum, len]
        funcnames = ["mean", "std", "median", "variance", "max", "sum", "size"]
    else:
        funcnames = [f.__name__ for f in funcs]

    if values.ndim > 1:
        # Flatten (copy here to avoid changing the original)
        values = values.ravel()
        x = x.ravel()

    # Get rid of masked values
    selection = ~values.mask
    # If maskedArray was created from a simple np.array, mask is just a boolean equal to False, and selection is just True
    # In that case, applying a selection add an empty dimension, effectively turning a (625,) array into a (1, 625) array
    # Hence this test to only apply the selection if there's something to select
    # (can't just test the type because it's not bool)
    if np.any(selection == False):
        values = values[selection]
        x = x[selection]

    if edges is None:
        if xrange is None:
            xmax = np.max(x)
            xmin = 0
        else:
            xmin, xmax = xrange
        nbins = int(np.ceil((xmax - xmin) / bin_width))
        edges = np.arange(xmin, xmin + (nbins + 1) * bin_width, bin_width)
    else:
        nbins = edges.size - 1

    # 0 correspond to values to the left of the leftmost edge. We have to shift the indexes
    digitized = np.digitize(x, edges, right=False) - 1

    # All bins are with left edge included, right edge excluded.
    # For the last bin, we need a special treatment to make sure
    # the outer edge is also included, or we will have a
    # fantom nbins+1 bin with only the values at exactly the maximum
    digitized[x == edges[-1]] = nbins - 1

    # We get rid of pixels outside of the range
    mask = (digitized < nbins) * (digitized >= 0)
    n = np.count_nonzero(mask)

    tmp_sparse_matrix = sparse.csr_matrix((values[mask], [digitized[mask], np.arange(n)]), shape=(nbins, n))

    # bins values
    groups = np.split(tmp_sparse_matrix.data, tmp_sparse_matrix.indptr[1:-1])

    # We get the exact mean radius for each bin
    indices = np.split(tmp_sparse_matrix.indices, tmp_sparse_matrix.indptr[1:-1])
    bin_centers = np.array([np.mean(x[mask][i]) if i.size else np.nan for i in indices])

    # Add one np.nan in empty sequences
    groups = [g if g.size else np.array([np.nan]) for g in groups]

    results = {}
    # I expect to see RuntimeWarnings in this block
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        for (func, name) in zip(funcs, funcnames):
            tmp = [func(group) for group in groups]

            results[name] = np.array(tmp)

    results["r"] = bin_centers

    return results


def _2d_binned_statistic(x, y, values, xbins, ybins):
    """
    source: https://stackoverflow.com/questions/26783719/efficiently-get-indices-of-histogram-bins-in-python

    Get a 2d study of a given dataset of values. We'll split the data into subgroups of values depending on the value of
    x and y for each corresponding item (x,y and values have the same size, each value then have an associated x and y)
    We will return a 2d image for each of the functions to apply to the subsets.

    :param x: metric over which we want to spread the bins evenly. array shape must be similar to 'values'
    :type x: np.array(nvalues)

    :param y: metric over which we want to spread the bins evenly. array shape must be similar to 'values'
    :type y: np.array(nvalues)

    :param values: input data as a simple array or masked array. values masked will get filtered before data is
                   processed
    :type values: nd.ma.MaskedArray(nvalues) or np.array(nvalues)

    :param int xbins: Number of bins (linear) for x (first dimension)
    :param int ybins: Number of bins (linear) for y (second dimension)

    :return: dictionnary with a 2d array of results for the following input keys:
        ["mean", "std", "median", "var", "max", "sum", "x", "y", "size"]
        For each keys, value is a np.array(xbins, ybins). x and y are specials, they correspond to the x and y labels
        for each index in the 2d image for each key (they are then only 1d)
    :rtype: dict
    """

    # Count only non NaN values per bin. Because I add a NaN in empty bins, this wouldn't have much sense otherwise
    nanlen = lambda x: x.size - np.count_nonzero(np.isnan(x))

    funcs = [np.nanmean, np.nanstd, np.nanmedian, np.nanvar, np.nanmax, np.nansum, nanlen]
    funcnames = ["mean", "std", "median", "variance", "max", "sum", "size"]

    # Get rid of masked values
    if isinstance(values, np.ma.MaskedArray):
        selection = ~values.mask
        # If maskedArray was created from a simple np.array, mask is just a boolean equal to False, and selection
        # is just True. In that case, applying a selection add an empty dimension, effectively turning a (625,)
        # array into a (1, 625) array. Hence this test to only apply the selection if there's something to select
        # (can't just test the type because it's not bool)
        if np.any(selection is False):
            values = values[selection]
            x = x[selection]
            y = y[selection]

    xmax = np.max(x)
    xmin = np.min(x)
    x_edges = np.linspace(xmin, xmax, xbins+1)

    ymax = np.max(y)
    ymin = np.min(y)
    y_edges = np.linspace(ymin, ymax, ybins+1)

    # 0 correspond to values to the left of the leftmost edge. We have to shift the indexes
    x_digitized = np.digitize(x, x_edges, right=False) - 1
    y_digitized = np.digitize(y, y_edges, right=False) - 1

    # All bins are with left edge included, right edge excluded.
    # For the last bin, we need a special treatment to make sure
    # the outer edge is also included, or we will have a
    # fantom nbins+1 bin with only the values at exactly the maximum
    x_digitized[x == x_edges[-1]] = xbins - 1
    y_digitized[y == y_edges[-1]] = ybins - 1

    # We get rid of pixels outside of the range
    mask = (x_digitized < xbins) * (x_digitized >= 0) * (y_digitized < ybins) * (y_digitized >= 0)
    n = np.count_nonzero(mask)

    digitized = np.zeros_like(x_digitized)
    digitized[mask] = np.ravel_multi_index((y_digitized[mask], x_digitized[mask]), (ybins, xbins))

    tmp_sparse_matrix = sparse.csr_matrix((values[mask], [digitized[mask], np.arange(n)]), shape=(xbins * ybins, n))

    # bins values
    groups = np.split(tmp_sparse_matrix.data, tmp_sparse_matrix.indptr[1:-1])

    # We get the exact mean radius for each bin
    # indices = np.split(tmp_sparse_matrix.indices, tmp_sparse_matrix.indptr[1:-1])

    # Add one np.nan in empty sequences
    groups = [g if g.size else np.array([np.nan]) for g in groups]

    results = {}
    # I expect to see RuntimeWarnings in this block
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        for (func, name) in zip(funcs, funcnames):
            tmp = [func(group) for group in groups]

            results[name] = np.array(tmp).reshape((ybins, xbins))

    results["x"] = x_edges[:-1] + np.diff(x_edges)/2
    results["y"] = y_edges[:-1] + np.diff(y_edges)/2

    return results


def comb_indices(indices):
    """
    For a given list of indices, return the combinations possibles between them

    We also get rid of i = j
    :param nd.array(int) indices:
    :return:
    """
    ind1, ind2 = np.meshgrid(indices, indices)

    selection = ind1 != ind2

    ind1 = ind1[selection]
    ind2 = ind2[selection]

    return ind1, ind2


def filtered_index(values, nb_points):
    """
    Given a data set, will return a filtered list of indexes that limit the total number of values but ensure a correct
    sampling of each bins (from min to max)

    :param data: Input data set as numpy.array or masked array. Need to be 1D
    :param int nb_points: indicative max number of points we want. We will end up with less or the same number depending on
                      how evenly bins are populated
    :return: list of indexes
    :rtype: np.array(int)
    """

    nbins = 1000

    max_count = int(nb_points / nbins)

    # Get rid of masked values
    if isinstance(values, np.ma.MaskedArray):
        selection = ~values.mask
        # If maskedArray was created from a simple np.array, mask is just a boolean equal to False, and selection is just True
        # In that case, applying a selection add an empty dimension, effectively turning a (625,) array into a (1, 625) array
        # Hence this test to only apply the selection if there's something to select
        # (can't just test the type because it's not bool)
        if np.any(selection == False):
            values = values[selection]

    xmax = np.max(values)
    xmin = np.min(values)
    bin_width = (xmax - xmin) / nbins

    edges = np.arange(xmin, xmin + (nbins + 1) * bin_width, bin_width)

    # 0 correspond to values to the left of the leftmost edge. We have to shift the indexes
    digitized = np.digitize(values, edges, right=False) - 1

    # All bins are with left edge included, right edge excluded.
    # For the last bin, we need a special treatment to make sure
    # the outer edge is also included, or we will have a
    # fantom nbins+1 bin with only the values at exactly the maximum
    digitized[values == edges[-1]] = nbins - 1

    # We get rid of pixels outside of the range
    mask = (digitized < nbins) * (digitized >= 0)
    n = np.count_nonzero(mask)

    tmp_sparse_matrix = sparse.csr_matrix((values[mask], [digitized[mask], np.arange(n)]), shape=(nbins, n))

    # We get the exact mean radius for each bin
    indices = np.split(tmp_sparse_matrix.indices, tmp_sparse_matrix.indptr[1:-1])

    # Filter indices to keep a max number per bin
    filtered_ind = [g[:max_count] for g in indices]
    filtered_ind = np.concatenate(filtered_ind)

    return filtered_ind
