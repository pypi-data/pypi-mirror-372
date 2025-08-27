"""Simple auxiliary functions performing conversions etc.

"""
import numpy as np
import itertools

def handle_input(meas, gamma, debug=False):
    """
    Convert user input for computational measurements and noise levels.

    Typically, the user should not call this function directly.

    Parameters
    ----------
    meas : array-like
        Measurement values. Can be 1D or 2D.
    gamma : float, array-like, or None
        Noise level(s). If None, defaults to ones with the same shape as `meas`.
        If scalar, expanded to match the shape of `meas`.
    debug : bool, optional
        If True, prints intermediate values for debugging. Default is False.

    Returns
    -------
    meas : ndarray
        Processed measurement array with NaNs removed.
    gamma : ndarray
        Processed noise levels aligned with `meas`.
    cats : int
        Number of categories (2 for 1D measurements, otherwise rows of `meas`).
    nanlocs : ndarray of bool
        Boolean mask of removed NaN positions.

    """
    meas = np.array(meas)
    if meas.ndim == 2 and meas.shape[0] == 2:
        meas = meas[1]

    if gamma is None:
        gamma = np.ones(meas.shape)
        #gamma = np.ones(meas.shape, dtype=float)
    elif np.isscalar(gamma):
        gamma = gamma * np.ones(meas.shape)
        #gamma = gamma * np.ones(meas.shape, dtype=float)
    elif np.ndim(gamma) == 1 and np.ndim(meas) == 2:
        gamma = np.tile(gamma, (np.size(meas, 0), 1))
    else:
        gamma = np.array(gamma)

    if meas.ndim == 1:
        cats = 2
        
        nanlocs = np.isnan(meas)
        
        if debug:
            print("handle input")
            print(meas)
            print(gamma)
            print(nanlocs)
        
        meas = meas[~nanlocs]
        gamma = gamma[~nanlocs]
        
        
        
    else:
        cats = np.size(meas, 0)
        
        nanlocs = np.isnan(np.amin(meas, 0))
        
        meas = meas[:, ~nanlocs]
        meas = meas[1:, :].flatten('F')
        
        gamma = gamma[:, ~nanlocs]
        gamma = gamma[1:, :].flatten('F')

    return meas, gamma, cats, nanlocs

def handle_input_fixed(meas, fix_vec, gamma, debug=False):
    """
    Convert input measurements and fixed vectors, handling NaNs consistently.

    If one of the indices of `fix_vec` OR `meas` is NaN, then the corresponding
    indices of all vectors will also be NaN.

    Parameters
    ----------
    meas : array-like
        Measurement values. Can be 1D or 2D.
    fix_vec : array-like
        Fixed strain vector(s).
    gamma : float, array-like, or None
        Noise level(s). If None, defaults to ones with the same shape as `meas`.
        If scalar, expanded to match the shape of `meas`.
    debug : bool, optional
        If True, prints intermediate values for debugging. Default is False.

    Returns
    -------
    meas : ndarray
        Processed measurement array with NaNs removed.
    fix_vec : ndarray
        Processed fixed vector with NaNs removed and converted to binary matrix form.
    gamma : ndarray
        Processed noise levels aligned with `meas`.
    cats : int
        Number of categories.
    nanlocs : ndarray of bool
        Boolean mask of removed NaN positions.

    """
    
    meas = np.array(meas)
    if meas.ndim == 2 and meas.shape[0] == 2:
        meas = meas[1]
        
        
    fix_vec = np.array(fix_vec)
    

    if gamma is None:
        gamma = np.ones(meas.shape)
        #gamma = np.ones(meas.shape, dtype=float)
    elif np.isscalar(gamma):
        gamma = gamma * np.ones(meas.shape)
        #gamma = gamma * np.ones(meas.shape, dtype=float)
    elif np.ndim(gamma) == 1 and np.ndim(meas) == 2:
        gamma = np.tile(gamma, (np.size(meas, 0), 1))
    else:
        gamma = np.array(gamma)

    if meas.ndim == 1:

        cats = 2
        
        measnanlocs = np.isnan(meas)
        fnanlocs=np.isnan(fix_vec)
        nanlocs=np.logical_or(measnanlocs, fnanlocs)
        
        if debug:
            print("handle input fixed")
            print(meas)
            print(gamma)
            print("meas nan locs")
            print(measnanlocs)
            print("fixed vec")
            print(fix_vec)
            print("fixed vec nan locs")
            print(fnanlocs)
            print("nan locs")
            print(nanlocs)
        
        
        meas = meas[~nanlocs]
        fix_vec=fix_vec[~nanlocs]
        gamma = gamma[~nanlocs]
    else:
        
        cats = np.size(meas, 0)
        
        measnanlocs = np.isnan(np.amin(meas, 0))
        fnanlocs = np.isnan(np.amin(fix_vec, 0))#np.isnan(fix_vec)
        nanlocs = np.logical_or(measnanlocs, fnanlocs)
        
        meas = meas[:, ~nanlocs]
        meas = meas[1:, :].flatten('F')
        
        fix_vec = fix_vec[~nanlocs]
        fix_vec = strainvec2binmat(fix_vec, cats)
        fix_vec = fix_vec[1:, :].flatten('F')
                
        gamma = gamma[:, ~nanlocs]
        gamma = gamma[1:, :].flatten('F')

    return meas, fix_vec, gamma, cats, nanlocs


        

def binary_blocks(n, cats=2, debug=False):
    """All possible binary rows or blocks.

    Returns either all possible binary vectors having given number of elements,
    or all possible binary blocks having given number of columns and column
    sums of at most one.

    Parameters
    ----------
    n : int
        Number of elements in a vector or number of columns in a block.
    cats : int, optional
        Number of categories for each column in a block. Must be at least 2. If
        `cats` is 2 (default), then a column can be either 0 and 1, i.e., a
        scalar. Otherwise, there are cats-1 different columns having sum of at
        most one.

    Returns
    -------
    blocks : 2D- or 3D-array
        If cats is 2, the shape is (2**n, n). Otherwise, the shape is
        (cats**n, cats-1, n).

    Examples
    --------
    >>> from strainpycon.utils import binary_blocks
    >>> binary_blocks(2)
    array([[0, 0],
           [0, 1],
           [1, 0],
           [1, 1]])
    >>> binary_blocks(2, cats=3)
    array([[[0, 0],
            [0, 0]],
           [[0, 1],
            [0, 0]],
           [[0, 0],
            [0, 1]],
           [[1, 0],
            [0, 0]],
           [[1, 1],
            [0, 0]],
           [[1, 0],
            [0, 1]],
           [[0, 0],
            [1, 0]],
           [[0, 1],
            [1, 0]],
           [[0, 0],
            [1, 1]]])

    """
    
    #edge case
    if n == 0:
        return None
    
    int_blocks = np.array(list(itertools.product(range(0, cats), repeat=n)))

    if cats == 2:
        return int_blocks

    binary_blocks = intmat2binmat(int_blocks, cats-1)
    ret = np.reshape(binary_blocks, (-1, cats-1, n))
    
    
    if debug:
        print("n:", str(n))
        print(int_blocks)
        print("cats:", str(cats))
        print(binary_blocks)
        print(ret)
        
    return ret


def intmat2binmat(intmat, maxint):
    """Converts non-negative integer matrix to a binary matrix.

    Every positive integer k is converted to a unit vector which has one in the
    k'th position (when counting starts from one) and zero in the remaining
    positions. Zero is converted to a zero vector. The returned matrix has the
    same number of columns as the input matrix, i.e., the conversion is
    performed vertically.

    Parameters
    ----------
    intmat : 2D-array
        Matrix with non-negative integers.
    maxint : int
        Maximum allowed integer in `intmat`. Determines the length of the unit
        vectors. Must be greater than or equal to the actual maximum value in
        `intmat`.

    Returns
    -------
    binmat : 2D-array
        If `intmat` has shape (m, n), then the shape of binmat is
        (maxint * m, n).

    See Also
    --------
    strainpycon.utils.binmat2intmat

    Examples
    --------
    >>> from strainpycon.utils import intmat2binmat
    >>> mat = np.array([[0, 1, 2], [2, 1, 0]])
    >>> mat
    array([[0, 1, 2],
           [2, 1, 0]])
    >>> intmat2binmat(mat, 2)
    array([[0, 1, 0],
           [0, 0, 1],
           [0, 1, 0],
           [1, 0, 0]])

    """
    intmat = np.array(intmat)
    (m, n) = intmat.shape
    binmat = np.zeros((maxint * m, n), dtype=int)
    for row_idx in range(m):
        block = np.zeros((maxint+1, n), dtype=int)
        block[intmat[row_idx, :], range(n)] = 1
        binmat[range(maxint * row_idx, maxint * (row_idx+1))] = block[1:, :]
    return binmat


def strainvec2binmat(intstrain, nclasses):
    """
    Convert a single integer strain vector to a binary matrix representation.

    Parameters
    ----------
    intstrain : array-like of int
        Strain vector with integer values.
    nclasses : int
        Number of classes (categories). Must be >= max(intstrain) + 1.

    Returns
    -------
    meas : ndarray of int, shape (nclasses, len(intstrain))
        Binary matrix representation of the strain vector.

    """
    npps = len(intstrain)

    binmat = intmat2binmat([intstrain], nclasses-1)

    meas = np.reshape(binmat, (nclasses-1, npps), 'F')
    meas = np.vstack((1 - np.sum(meas, 0), meas))
    
    return meas


def binmat2intmat(binmat, cats):
    """Converts binary block matrix to a non-negative integer matrix.

    This function is the inverse of pystrainrecon.utils.intmat2binmat function.

    Parameters
    ----------
    binmat : 2D array
        Binary block matrix where blocks have `cats`-1 rows and each column in
        a block sums up to 1 or 0.
    cats : int
        Size of the block plus one. Must be at least 2.

    Returns
    -------
    intmat : 2D array
        Matrix with integers {0, ..., cats-1}.

    See Also
    --------
    strainpycon.utils.binmat2intmat

    Example
    -------
    >>> mat = np.array([[0, 1, 0], [0, 0, 1], [0, 1, 0], [1, 0, 0]])
    >>> mat
    array([[0, 1, 0],
           [0, 0, 1],
           [0, 1, 0],
           [1, 0, 0]])
    >>> binmat2intmat(mat, 3)
    array([[0, 1, 2],
           [2, 1, 0]])

    """
    mat = np.array(binmat).T # work with the transpose
    n = np.size(mat, 0)
    m = np.size(mat, 1) // (cats - 1)

    # add the "missing rows" (here, columns)
    mat = np.reshape(mat, (m * n, cats - 1))
    mat = np.column_stack((1 - np.sum(mat, 1), mat))

    # row indices of nonzero entries (here, column indices)
    mat = np.nonzero(mat)[1]

    mat = np.reshape(mat, (n, m))

    return mat.T



def addnanrows(mat, nanlocs):
    """Returns array with nan rows added to specific locations.

    Parameters
    ----------
    mat : 2D- or 3D-array
        If `mat` is 3D, then the rows are added to `mat[i]` for each i.
    nanlocs : bool vector
        Vector specifying the nan row indices in the returned matrix. True
        corresponds to nan. The shape must be (k,), where k equals (number of
        rows in mat) + (number of Trues in nanlocs).

    Returns
    -------
    mat : 2D- or 3D-array
        Array augmented with nans.

    """
    mat = np.array(mat)

    def addnanrows2d(mat2d):
        (m, n) = mat2d.shape
        m_full = m + np.sum(nanlocs)
        fullmat = np.empty((m_full, n))
        fullmat.fill(np.nan)
        fullmat[~nanlocs, :] = mat2d
        return fullmat

    if mat.ndim == 2:
        return addnanrows2d(mat)
    else:
        return np.array([addnanrows2d(mat2d) for mat2d in mat])
    
    
def find_strain_in_strains(strains, props, force_vec):
    """
    Identify indices and proportions of a given strain within a list of strains.

    Parameters
    ----------
    strains : list of ndarray or ndarray
        List or array of strain vectors.
    props : list or ndarray
        Corresponding proportions for each strain.
    force_vec : ndarray
        Strain vector to match. NaN entries are ignored.

    Returns
    -------
    force_indexes : list of int
        Indices where `force_vec` matches a strain.
    force_props : list
        Proportions corresponding to matched strains.

    """
    force_indexes = []
    force_props = []

    # Create a mask for positions in force_vec that are not NaN
    valid_mask = ~np.isnan(force_vec)

    for i in range(len(strains)):
        strain = strains[i]

        # Compare only the valid (non-NaN) entries
        if np.array_equal(strain[valid_mask], force_vec[valid_mask]):
            force_indexes.append(i)
            force_props.append(props[i])

    return force_indexes, force_props
