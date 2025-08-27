# -*- coding: utf-8 -*-
r"""
Numerics for the probability simplex.

Probability simplex contains :math:`d`-dimensional vectors :math:`x` that
satisfy :math:`x_1 + \ldots + x_d = 1` and :math:`x_i \geq 0` for
:math:`i=1,...,d`.

"""
import numpy as np



def rand_simplex(dim, count=None, sort=0, fixed_value=None):
    """
    Draw uniform random vectors from the probability simplex.

    Parameters
    ----------
    dim : int
        Number of elements in a vector.
    count : None or int, optional
        Number of vectors. The default is None which corresponds to a single
        vector.
    sort : {0, 1, -1}, optional
        When sort equals 0 (default), the vectors are not sorted. If sort
        is 1, each vector is sorted in ascending order, and if sort is -1,
        each vector is sorted in descending order.
    fixed_value: [0,1), optional
        If specified, then this value will appear somewhere in each returned vector

    Returns
    -------
    ndarray
        If count is None, the shape of the output is (dim,). Otherwise, the
        shape is (count, dim).

    Notes
    -----
    Sorting the vectors after uniformly drawing them from the probability
    simplex is equivalent to drawing them uniformly from the specific part of
    the simplex that contains the ordered vectors.

    This function relies internally on numpy.random.random_sample when drawing
    random numbers.

    """
    flat_out = False
    if count is None:
        count = 1
        flat_out = True

    if fixed_value is not None:
        if count < 1:
            raise ValueError("count must be at least 1 when fixed_vector is provided")
        num_random = count - 1
    else:
        num_random = count

    # Determine dimension based on whether fixed_value is used
    dim2 = dim - 1 if fixed_value is not None else dim

    # Generate sorted random simplex vectors with 0 and 1 boundaries
    rands = np.random.random_sample((count, dim2 - 1))
    rands = np.hstack((np.zeros((count, 1)), np.sort(rands, axis=1), np.ones((count, 1))))
    vecs = np.diff(rands, axis=1)

    # Append fixed_value if provided
    if fixed_value is not None:
        vecs*=(1-fixed_value)
        vecs = np.hstack((vecs, np.full((count, 1), fixed_value)))

    if sort:
        vecs = np.sort(vecs)[:, ::sort]

    if flat_out:
        vecs = vecs.flatten()

    return vecs



def ordered_mean(dim, order=1):
    r"""
    Centroid of the sorted vectors of the probability simplex.

    The centroid means the expected vector when vectors are drawn uniformly
    from that part of the simplex that satisfies the ordering constraint.

    Parameters
    ----------
    dim : int
        Number of elements in the vector.
    order : {1, -1}, optional
        If 1 (default), the elements are sorted in ascending order. If -1, the
        elements are in descending order.

    Returns
    -------
    mean_vec : vector with shape (dim,)
        Centroid, or expected vector.
    
    Notes
    -----
    See [#]_ for the algorithm.

    References
    ----------
    .. [#] https://mathoverflow.net/a/238524

    """
    nums = 1.0 / np.arange(dim, 0, -1)
    return 1.0 / dim * np.cumsum(nums)[::order]


def proj_simplex(vec):
    r"""
    Euclidean projection of a given vector onto the probability simplex.

    Parameters
    ----------
    vec : vector
        Vector to be projected. Shape can be (`dim`,), (`dim`, 1), or
        (1, `dim`).

    Returns
    -------
    vector
        Same shape as the input.

    Notes
    -----
    This function uses an exact, non-iterative algorithm from [#]_.

    References
    ----------
    .. [#] "Projection onto the probability simplex: An efficient algorithm
           with a simple proof, and an application", W. Wang and M. Á.
           Carreira-Perpiñán, https://arxiv.org/abs/1309.1541

    """
    dim = np.size(vec)
    u = np.sort(vec)[::-1] # sort in descending order
    c = (np.cumsum(u) - 1) / np.arange(1, dim+1)
    vec = vec - c[np.sum(u > c) - 1]
    return np.maximum(vec, 0)


def lstsq_simplex(a, b, minstep=1e-8, maxiter=100):
    r"""
    Least-squares solution to a simplex-constrained linear equation.

    Finds a vector :math:`x \in S` that minimizes :math:`\|A x - b \|` with
    :math:`S` denoting the probability simplex.

    Parameters
    ----------
    a : array
        Any real matrix :math:`A`. (should be tall?)
    b : vector
        "Right hand side" vector.
    minstep : float, optional
        Stopping criterion parameter. The APG iteration stops when the norm
        between subsequent iterates goes below this value.
    maxiter : int, optional
        Maximum number of iterations. Set to zero to use `minstep` as the only
        stopping criterion.

    Returns
    -------
    sol : vector
        Minimizing vector.
    iters : int
        Number of APG iterations (0 means no APG was needed).

    Notes
    -----
    This function first tries to solve the problem without non-negativity
    constraints by using a KKT-like matrix for the sum-to-one equality
    constraint. If the resulting vector contains negative values, then the
    iterative accelerated projected gradient (APG) method [#]_ is employed.

    The APG method is fast if the condition number of the matrix is small. In
    particular, if the matrix is rank-deficient, then APG may need a lot of
    iterations to converge. In the latter case, the minimizing vector may also
    be non-unique. One of the minimizing vectors is then returned.

    References
    ----------
    .. [#] "Least-squares on the simplex for multispectral unmixing", L.
           Condat, http://www.gipsa-lab.grenoble-inp.fr/~laurent.condat/publis/Condat-unmixing.pdf

    """
    dim = np.size(a, 1)

    # construct KKT-like system and solve without non-negativity constraint
    constr = np.ones((1, dim))
    ac = np.block([ [np.dot(a.T, a), constr.T], [constr, 0] ])
    b1 = np.hstack((np.dot(a.T, b), 1))
    x = np.linalg.lstsq(ac, b1, rcond=None)[0][:-1]

    # check nonnegativity
    if all(x >= 0):
        return x

    # APG starts here
    aa = ac[0:dim, 0:dim]
    ab = b1[0:dim]
    x = proj_simplex(x)

    eig = np.linalg.eigvalsh(aa)
    mu = eig[0]
    beta = eig[-1]

    u = x
    alpha = 1
    for j in range(0, maxiter):
        x_prev = x
        x = proj_simplex(u - 1/(beta+mu) * (np.dot(aa, u) - ab))
        if np.linalg.norm(x-x_prev) < minstep:
            return x
        c = mu / (beta+mu)
        alpha_prev = alpha
        alpha = (-alpha**2 + (alpha**4 - 2*c*alpha**2 + 4*alpha**2 + c**2)**.5 + c) / 2
        gamma = alpha_prev * (1-alpha_prev) / (alpha_prev**2 + alpha)
        u = x + gamma * (x-x_prev)

    return x


def lstsq_bilin(mat_rows, b, weights=None, trials=100, target_norm=0.0, vecstep=1e-8, veciters=100):
    r"""
    Least-squares solution to a constrained bilinear system.

    Finds a matrix :math:`A` in some finite set and a vector :math:`x` in the
    probability simplex such that the sum of squares :math:`\| A x - b \|_2^2`
    is minimized. More generally, finds a minimizing matrix and vector for the
    weighted sum :math:`\sum_i w_i^2 (A_{i,:} \cdot x - b_i)^2`, where the
    weights :math:`w_i` are given.

    The rows in the matrix are restricted to the set provided by the user.
    Alternatively, instead of rows, the user may also provide the feasible
    blocks that can be stacked vertically to form the minimizing matrix.

    Parameters
    ----------
    mat_rows : array
        If the shape is (K, N), then each row in the output matrix `a` is a
        row in `mat_rows`. If the shape is (K, P, N), then `a` contains blocks
        of shape (P, N), stacked on top of each other, such that each block is
        `mat_rows[i]` for some `i`. In both cases, repetitions are allowed in
        `a`.
    b : vector
        "Right hand side" vector. If the shape of `mat_rows` is (K, P, N), then
        the length of `b` must be divisible by P.
    weights : None or array, optional
        If None (default), unweighted least-squares problem is considered.
        Otherwise must have as many elements as there are blocks in `a` (i.e.,
        the length of `b` divided by P).
    trials : int, optional
        Number of initializations for the BCD method. Higher value requires
        more time, but makes finding global minimizers more likely. Default is
        100.

    Returns
    -------
    a : array
        Minimizing matrix with shape (M,N), where M is the length of `b`.
    x : vector
        Minimizing vector with shape (N,).
    trials : int
        Actual number of BCD trials.
    resnorm : float
        Residual (non-squared) norm `|| ax - b ||`, or weighted norm if
        `weights` is an array.

    Other parameters
    ----------------
    target_norm : float, optional
        Do not start new instances of the BCD method if the (weighted) residual
        norm goes below this value. Default is 0 which means that BCD is
        initialized `trials` times unless exact minimizers are found (which is
        usually very unlikely).
    vecstep : float, optional
        Step size stopping criterion in the simplex-constrained least squares
        problem, passed as `minstep` to strainpycon.psimplex.lstsq_simplex.
    veciters : int, optional
        Maximum number of iterations in the simplex-constrained least squares
        problem, passed as `maxiter` to strainpycon.psimplex.lstsq_simplex.

    See Also
    --------
    strainpycon.psimplex.lstsq_simplex

    Notes
    -----
    This function employs the block coordinate descent (BCD) method which
    alternately minimizes the matrix (for a fixed vector) and the vector (for
    a fixed matrix). The initial vectors are drawn uniformly from the
    probability simplex.

    For each output (`a`, `x`) there exist factorial of N equally good
    solutions corresponding to different ordering of the rows in `a` and the
    elements in `x`. Due to implementation details, the output is "biased"
    towards some orderings. More precisely, `x` is often sorted in descending
    order.

    Examples
    --------
    Restrict `a` to be a binary matrix with three columns. Therefore, `x` has
    also three elements.

    >>> import numpy as np
    >>> import strainpycon
    >>> import itertools
    >>> mat_rows = np.array(list(itertools.product([0,1], repeat=3)))
    >>> mat_rows
    array([[0, 0, 0],
           [0, 0, 1],
           [0, 1, 0],
           [0, 1, 1],
           [1, 0, 0],
           [1, 0, 1],
           [1, 1, 0],
           [1, 1, 1]])
    >>> b = np.array([0, 0.97, .49, .51])
    >>> result = strainpycon.lstsq_bilin(mat_rows, b)
    >>> result[0]
    array([[0, 0, 0],
           [1, 1, 0],
           [0, 1, 0],
           [1, 0, 1]])
    >>> result[1]
    array([0.48, 0.49, 0.03])
    >>> # The solution is an exact match:
    >>> np.dot(result[0], result[1])
    array([0.  , 0.97, 0.49, 0.51])

    Let us now assume that an even row in `a` must always be the "negation" of
    the previous row.

    >>> mat_rows2 = np.array([mat_rows, 1-mat_rows]).swapaxes(0,1)
    >>> mat_rows2.shape
    (8, 2, 3)
    >>> mat_rows2
    array([[[0, 0, 0],
            [1, 1, 1]],
           [[0, 0, 1],
            [1, 1, 0]],
           [[0, 1, 0],
            [1, 0, 1]],
           [[0, 1, 1],
            [1, 0, 0]],
           [[1, 0, 0],
            [0, 1, 1]],
           [[1, 0, 1],
            [0, 1, 0]],
           [[1, 1, 0],
            [0, 0, 1]],
           [[1, 1, 1],
            [0, 0, 0]]])
    >>> result2 = strainpycon.lstsq_bilin(mat_rows2, b)
    >>> result2[0]
    array([[0, 0, 1],
           [1, 1, 0],
           [0, 1, 1],
           [1, 0, 0]])
    >>> result2[1]
    array([0.51, 0.475, 0.015])
    >>> # This time the residual does not go to zero:
    >>> np.dot(result[0], result[1])
    array([0.015 , 0.985, 0.49, 0.51])

    Notice that because the method uses random numbers, the results may be
    different than shown above.

    """
    dim = np.size(mat_rows, -1)
    if mat_rows.ndim > 2:
        bmat = np.reshape(b, (-1, np.size(mat_rows, 1)))

    x0 = rand_simplex(dim, trials, sort=-1)
    row_combs = set()
    minnorm = np.inf

    for trial in range(0, trials):
        x = x0[trial]

        while True:
            row_prods = np.dot(mat_rows, x)
            if mat_rows.ndim == 2:
                row_comb = tuple([np.abs(row_prods - elem).argmin() for elem in b])
            else:
                row_comb = tuple([np.sum((row_prods - block)**2, -1).argmin() for block in bmat])

            if row_comb in row_combs:
                break # already computed
            row_combs.add(row_comb)

            a = np.reshape(mat_rows[row_comb, :], (-1, dim))

            if weights is None:
                x = lstsq_simplex(a, b, vecstep, veciters)
                resnorm = np.linalg.norm(np.dot(a, x) - b)
            else:
                wa = (weights*(a.T)).T
                wb = weights*b
                x = lstsq_simplex(wa, wb, vecstep, veciters)
                resnorm = np.linalg.norm(np.dot(wa, x) - wb)

            if resnorm <= target_norm:
                return a, x, trial+1, resnorm

            if resnorm < minnorm:
                mina = a
                minx = x
                minnorm = resnorm

    return mina, minx, trial+1, minnorm


def lstsq_bilin_fix_vec(mat_rows, mat_rows_p, b, fix_vec, weights=None, trials=100, target_norm=0.0, vecstep=1e-8, veciters=100):
    r"""
    Same as strainpycon.psimplex.lstsq_bilin, but now, we give a vector (fix_vec)
    and constrain the solutions such that fix_vec must appear in the returned solutions
    

    Parameters
    ----------
    mat_rows : array
        If the shape is (K, N), then each row in the output matrix `a` is a
        row in `mat_rows`. If the shape is (K, P, N), then `a` contains blocks
        of shape (P, N), stacked on top of each other, such that each block is
        `mat_rows[i]` for some `i`. In both cases, repetitions are allowed in
        `a`.
    mat_rows_p : array
        Same as mat_rows, but for TODO 
    b : vector
        "Right hand side" vector. If the shape of `mat_rows` is (K, P, N), then
        the length of `b` must be divisible by P.
    fix_vec: vector
        The vector that must appear in the returned solution
    weights : None or array, optional
        If None (default), unweighted least-squares problem is considered.
        Otherwise must have as many elements as there are blocks in `a` (i.e.,
        the length of `b` divided by P).
    trials : int, optional
        Number of initializations for the BCD method. Higher value requires
        more time, but makes finding global minimizers more likely. Default is
        100.

    Returns
    -------
    a : array
        Minimizing matrix with shape (M,N), where M is the length of `b`.
    x : vector
        Minimizing vector with shape (N,).
    trials : int
        Actual number of BCD trials.
    resnorm : float
        Residual (non-squared) norm `|| ax - b ||`, or weighted norm if
        `weights` is an array.

    Other parameters
    ----------------
    target_norm : float, optional
        Do not start new instances of the BCD method if the (weighted) residual
        norm goes below this value. Default is 0 which means that BCD is
        initialized `trials` times unless exact minimizers are found (which is
        usually very unlikely).
    vecstep : float, optional
        Step size stopping criterion in the simplex-constrained least squares
        problem, passed as `minstep` to strainpycon.psimplex.lstsq_simplex.
    veciters : int, optional
        Maximum number of iterations in the simplex-constrained least squares
        problem, passed as `maxiter` to strainpycon.psimplex.lstsq_simplex.

    See Also
    --------
    strainpycon.psimplex.lstsq_bilin

    Notes
    -----
    This function employs the block coordinate descent (BCD) method which
    alternately minimizes the matrix (for a fixed vector) and the vector (for
    a fixed matrix). The initial vectors are drawn uniformly from the
    probability simplex.

    For each output (`a`, `x`) there exist factorial of N equally good
    solutions corresponding to different ordering of the rows in `a` and the
    elements in `x`. Due to implementation details, the output is "biased"
    towards some orderings. More precisely, `x` is often sorted in descending
    order.

    Examples
    --------
    
    if dim = 2 and fix_vec=[1,1]
    then the possible return values for 'a' can be
    [1,1]
    [0,0]
    
    [1,1]
    [0,1]
    
    [1,1]
    [1,0]
    
    [0,0]
    [1,1]
    
    [0,1]
    [1,1]
    
    [1,0]
    [1,1]
    
    

    """
    
    
 
        
    dim = np.size(mat_rows, -1)
    dimp=dim-1
    
    if mat_rows.ndim > 2:
        bmat = np.reshape(b, (-1, np.size(mat_rows, 1)))

    x0 = rand_simplex(dim, trials, sort=-1)
    
    minnorm = np.inf
    mina=None
    minx=None
    
    for strainnum in range(dim):
        # for each strainnum i in dim, assume that the fix_vec is that strain
        # now solve the problem for dim'=dim-1 vectors
        # by tweaking the target b vector to account for fix_vec * x
        # a[strainnum] = fix_vec
        # a' = a minus the ith element (which will be fix_vec)
        # b' = b - fix_vec * (proportion of fix_vec)
        # x' = x minus (proportion of fix_vec)
        # and solve a' x' = b' to find an optimal a'
        # and use that to get a
        # and then use that to find an optimal x
        
        row_combs = set()
        
        for trial in range(0, trials):
            x = x0[trial]

            while True:
                # optimize for a....
                
                #edge case for dim==1
                if dim==1:
                    a=np.array([fix_vec]).T
                    row_comb=None
                else:
                    
                    xp=np.concatenate([x[:strainnum], x[strainnum+1:]])

                    row_prods = np.dot(mat_rows_p, xp)      
                    
                    bfixed = [snp*x[strainnum] for snp in fix_vec]
                    bp = [b[i] - bfixed[i] for i in range(len(b))]

                    if mat_rows_p.ndim == 2:
                        # optimize for a'
                        # by solving a' x' = b'   

                        row_comb = tuple([np.abs(row_prods - elem).argmin() for elem in bp])
                    else:                        
                        bmatp = np.reshape(bp, (-1, np.size(mat_rows_p, 1)))

                        row_comb = tuple([np.sum((row_prods - block)**2, -1).argmin() for block in bmatp])

                    #get a from a'
                    ap = np.reshape(mat_rows_p[row_comb, :], (-1, dimp))
                    a = np.concatenate([ap.T[:strainnum], [fix_vec], ap.T[strainnum:]]).T
                    
                if row_comb in row_combs:
                    break # already computed
                row_combs.add(row_comb)

                #optimize for x...
                if weights is None:
                    x = lstsq_simplex(a, b, vecstep, veciters)
                    resnorm = np.linalg.norm(np.dot(a, x) - b)
                else:
                    wa = (weights*(a.T)).T
                    wb = weights*b
                    x = lstsq_simplex(wa, wb, vecstep, veciters)
                    resnorm = np.linalg.norm(np.dot(wa, x) - wb)
                
                    
                # evaluate the x and a we found...
                if resnorm <= target_norm:
                    return a, x, trial+1, resnorm

                if resnorm < minnorm:
                    mina = a
                    minx = x
                    minnorm = resnorm

    return mina, minx, trial+1, minnorm