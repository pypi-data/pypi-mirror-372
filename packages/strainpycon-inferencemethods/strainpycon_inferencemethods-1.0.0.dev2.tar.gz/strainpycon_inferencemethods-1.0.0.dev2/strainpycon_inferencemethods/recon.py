"""This module defines the StrainRecon class.

"""
from strainpycon_inferencemethods import utils, psimplex, integration
import numpy as np

class StrainRecon:
    """Stores parameters and provides functions for strain computations.

    We use the word `reconstruction` when referring to a single pair of strains
    and their frequencies that minimizes, for a given measurement, the properly
    defined misfit, i.e., some (weighted) sum of squares. In probabilistic
    terms, reconstruction corresponds to the maximum a posteriori (MAP)
    estimate under the assumption that the measurement error is Gaussian and
    the prior distributions for the strains and their frequencies are uniform.

    This class can also be used to compute posterior statistics under the
    additional assumption that the frequencies are listed in decreasing order.
    More precisely, posterior mean and the square root of the diagonal of the
    posterior covariance can be computed. The posterior covariance is related
    to the uncertainty that stems from the measurement error and/or from the
    non-unique matrix-vector decomposition that mathematically connects the
    measurement to the underlying mixing model.

    Attributes
    ----------
    nopt : int, optional
        Number of random initial vectors in the block coordinate descent
        optimization scheme when computing the reconstruction. Larger values
        lead to more accurate results but require more time. Default is 50.
    nint : int, optional
        Number of integration nodes in the Monte Carlo method when computing
        posterior means and variances. Default is 5000. Can be overridden when
        calling `posterior_stats`.
    lsqtol : float, optional
        Stopping criterion parameter in the linear least-squares subproblem
        arising in the block coordinate descent method. See
        `pystrainrecon.psimplex.lstsq_simplex` for details.
    lsqiter : int, optional
        Another stopping criterion parameter for
        `pystrainrecon.psimplex.lstsq_simplex` method.

    """
    def __init__(self, nopt=50, nint=5000, lsqtol=1e-8, lsqiter=100):
        self.nopt = nopt
        self.nint = nint
        self.lsqtol = lsqtol
        self.lsqiter = lsqiter


    def compute(self, meas, nstrains, gamma=None, uncertainty=False):
        """Computes the reconstruction, optionally also posterior statistics.

        Parameters
        ----------
        meas : vector or 2D-array
            If `meas` is a vector with shape (m,), then the strains are binary
            and each element in `meas` represents the relative amount of ones.
            Otherwise, `meas` must have shape (c, m), where c is the number of
            possible categories in strains. Then the i'th row represents the
            relative amount of the i'th category.
        nstrains : int
            Number of strains in the reconstruction.
        gamma : None, scalar, vector, or 2D-array, optional
            The (assumed) standard deviation of the Gaussian measurement noise.
            If None (default) or a scalar, the noise level is assumed to be
            independent of the measurement location and an unweighted
            least-squares problem is considered. Otherwise, can have shape
            (m,), specifying the level for each location (whether or not `meas`
            is a vector), or shape (c, m), specifying the level separately for
            each measurement entry.
        uncertainty : bool, optional
            If True, calls `posterior_stats(meas, nstrains, gamma)` and
            appends the output to the returned tuple. If True, `gamma` must not
            be None, and a scalar `gamma` specifies the common noise level for
            all measurements. The default is False.

        Returns
        -------
        strainmat : (`nstrains`, m) integer matrix
            Strain barcode reconstruction. Contains integers {0, ..., c-1},
            where c=2 if `meas` is a vector. If `meas` contains nans, then the
            corresponding columns in `strainmat` are nan.
        freqvec : (`nstrains`,) vector
            Reconstructed strain frequencies. The frequencies appear in
            descending order and they correspond to the rows of `strainmat`.
        meanmat, meanvec, devmat, devvec : arrays
            See the return values of `posterior_stats`. These are returned only
            if `uncertainty` is True.

        Notes
        -----
        Each column in a 2D `meas` should sum up to one. In the current
        implementation, the first row is simply discarded and replaced with a
        value that makes the column sums exactly one.

        Similarly, in 2D `gamma` the values in the first row are never used.

        """
        if uncertainty:
            (meanmat, meanvec, devmat, devvec) = self.posterior_stats(meas, nstrains, gamma)

        (meas, gamma, cats, nanlocs) = utils.handle_input(meas, gamma)
        mat_blocks = utils.binary_blocks(nstrains, cats)

        (strainmat, freqvec) = psimplex.lstsq_bilin(
                mat_blocks, meas, gamma, self.nopt, vecstep=self.lsqtol, veciters=self.lsqiter)[0:2]

        # freqvec must be sorted in descending order
        sort_idx = freqvec.argsort()[::-1]
        strainmat = strainmat[:, sort_idx]
        freqvec = freqvec[sort_idx]

        strainmat = utils.binmat2intmat(strainmat, cats)
        strainmat = utils.addnanrows(strainmat, nanlocs)
        strainmat = strainmat.T

        if uncertainty:
            return strainmat, freqvec, meanmat, meanvec, devmat, devvec

        return strainmat, freqvec

    
    def compute_fixed(self, meas, nstrains, fix_vec, gamma=None, uncertainty=False):
        """
        Computes the strain reconstruction while ensuring that the specified 
        `fix_vec` is included in the strain matrix. Optionally computes posterior 
        statistics.

        Parameters
        ----------
        meas : vector or 2D-array
            Measurement data for reconstruction. If `meas` is a vector with shape 
            (m,), the strains are binary, and each element represents the relative 
            amount of ones. Otherwise, `meas` must have shape (c, m), where `c` is 
            the number of possible categories in the strains, and the i-th row 
            represents the relative amount of the i-th category.
        nstrains : int
            Number of strains in the reconstruction.
        fix_vec : vector
            A fixed strain vector to be included in the strain matrix during the 
            reconstruction. Must align with the category structure in `meas`.
        gamma : None, scalar, vector, or 2D-array, optional
            The standard deviation of the Gaussian measurement noise. If None 
            (default) or a scalar, noise is assumed to be location-independent, and 
            an unweighted least-squares problem is solved. Otherwise:
            - Shape (m,): Specifies the noise level for each location in `meas` if 
              it's a vector.
            - Shape (c, m): Specifies noise levels separately for each measurement 
              entry if `meas` is 2D.
        uncertainty : bool, optional
            If True, calls `posterior_stats(meas, nstrains, gamma)` to compute 
            additional uncertainty statistics, appending them to the returned tuple. 
            Requires `gamma` to be specified and scalar. Default is False.

        Returns
        -------
        strainmat : (`nstrains`, m) integer matrix
            Strain barcode reconstruction matrix, containing integers {0, ..., c-1}, 
            where `c=2` if `meas` is a vector. If `meas` contains NaNs, the 
            corresponding columns in `strainmat` will also be NaN.
        freqvec : (`nstrains`,) vector
            Reconstructed strain frequencies in descending order, corresponding to 
            the rows of `strainmat`.
        meanmat, meanvec, devmat, devvec : arrays
            Additional outputs from `posterior_stats` if `uncertainty` is True.

        Notes
        -----
        - Each column in a 2D `meas` should sum to one. If not, the first row is 
          replaced with a value to make the column sums exactly one.
        - In 2D `gamma`, values in the first row are ignored.
        - The `fix_vec` is treated as a constraint, ensuring its inclusion in the 
          resulting strain matrix.

        """
        
        if uncertainty:
            (meanmat, meanvec, devmat, devvec) = self.posterior_stats(meas, nstrains, gamma)

        (meas, fix_vec, gamma, cats, nanlocs) = utils.handle_input_fixed(meas, fix_vec, gamma)
        mat_blocks = utils.binary_blocks(nstrains, cats)
        mat_blocks_p = utils.binary_blocks(nstrains-1, cats)

        (strainmat, freqvec) = psimplex.lstsq_bilin_fix_vec(
                mat_blocks, mat_blocks_p, meas, fix_vec, gamma, self.nopt, vecstep=self.lsqtol, veciters=self.lsqiter)[0:2]

        # freqvec must be sorted in descending order
        sort_idx = freqvec.argsort()[::-1]
        strainmat = strainmat[:, sort_idx]
        freqvec = freqvec[sort_idx]

        strainmat = utils.binmat2intmat(strainmat, cats)
        strainmat = utils.addnanrows(strainmat, nanlocs)
        strainmat = strainmat.T

        if uncertainty:
            return strainmat, freqvec, meanmat, meanvec, devmat, devvec

        return strainmat, freqvec
    
    def compute_for_STIM_threshold(self, meas, maxnstrains=5, misfitThresh=1.8e-7, gamma=None, uncertainty=False):
        """
        Compute reconstruction and misfit using a threshold to determine MOI.

        Parameters
        ----------
        meas : array_like
            Measurement vector or matrix.
        maxnstrains : int, optional
            Maximum number of strains to consider. Default is 5.
        misfitThresh : float, optional
            Threshold of misfit to stop the iteration. Default is 1.8e-7.
        gamma : scalar or array_like, optional
            Standard deviation of Gaussian measurement noise.
        uncertainty : bool, optional
            Whether to compute posterior statistics. Default is False.

        Returns
        -------
        reconstruction : tuple
            Strain matrix and frequency vector, optionally with posterior stats
            if `uncertainty` is True.
        misfit : float
            Misfit of the reconstruction.
        nstrains : int
            Number of strains used in the reconstruction.
        """
        meas_proc, gamma_proc, cats, nanlocs = utils.handle_input(meas, gamma)

        for nstrains in range(1, maxnstrains + 1):
            mat_blocks = utils.binary_blocks(nstrains, cats)

            estimation = psimplex.lstsq_bilin(
                mat_blocks, meas_proc, gamma_proc, self.nopt,
                vecstep=self.lsqtol, veciters=self.lsqiter
            )
            strainmat, freqvec, _, resnorm = estimation[:4]
            misfit = resnorm**2 / 2

            if misfit < misfitThresh or nstrains == maxnstrains:
                if uncertainty:
                    meanmat, meanvec, devmat, devvec = self.posterior_stats(meas_proc, nstrains, gamma_proc)
                break

        # Sort frequencies descending
        sort_idx = freqvec.argsort()[::-1]
        strainmat = strainmat[:, sort_idx]
        freqvec = freqvec[sort_idx]

        # Post-process matrix
        strainmat = utils.binmat2intmat(strainmat, cats)
        strainmat = utils.addnanrows(strainmat, nanlocs).T

        reconstruction = (strainmat, freqvec)
        if uncertainty:
            reconstruction = strainmat, freqvec, meanmat, meanvec, devmat, devvec
        
        return reconstruction, misfit, nstrains


    def misfits(self, meas, nrange, gamma=None, debug=False):
        """Strain reconstruction misfits.

        Computes the (squared) StrainRecon.jl style misfits, i.e., negative
        log-likelihoods, for a list of different number of strains.
        
        Parameters
        ----------
        meas : vector or 2D-array
            See the description of `meas` parameter in `compute`.
        nrange : int iterable
            Number of strains in the reconstructions.
        gamma : None, scalar, vector, or 2D-array, optional
            See the description of `gamma` parameter in `compute`. A scalar
            `gamma` is the common standard deviation for all measurements and
            it has a scaling effect in the misfits.

        Returns
        -------
        misfitvec : vector
            Numpy vector with misfits. Same length as nrange.

        """
        
        if debug:
            print("misfit pre handle")
            print(meas)
            print(gamma)
        (meas, gamma, cats, nanlocs) = utils.handle_input(meas, gamma, debug=debug)
        
        misfitvec = np.zeros(len(nrange))
        for n_idx in range(len(nrange)):
            nstrains = nrange[n_idx]
            mat_blocks = utils.binary_blocks(nstrains, cats)
            
            resnorm = psimplex.lstsq_bilin(
                    mat_blocks, meas, gamma, self.nopt, vecstep=self.lsqtol, veciters=self.lsqiter)[3]
            misfitvec[n_idx] = resnorm**2 / 2

        return misfitvec
    
    def misfits_fixed(self, meas, nrange, fix_vec, gamma=None, debug=False):
        """
        Computes the strain reconstruction misfits with a fixed strain.

        Similar to `misfits`, but ensures that the specified `fix_vec` is included 
        as a constraint during the reconstruction. Handles edge cases, such as when 
        there is only one strain.

        Parameters
        ----------
        meas : vector or 2D-array
            Measurement data for reconstruction. See the `meas` parameter 
            description in `compute`.
        nrange : int iterable
            Range of strain numbers to evaluate during reconstruction.
        fix_vec : vector
            A fixed strain vector to be included in the reconstruction. Must align 
            with the category structure in `meas`.
        gamma : None, scalar, vector, or 2D-array, optional
            Standard deviation of Gaussian measurement noise. See the `gamma` 
            parameter description in `compute`. If scalar, it applies uniformly to 
            all measurements and scales the misfits.

        Returns
        -------
        misfitvec : vector
            Numpy vector of misfits, representing negative log-likelihoods for each 
            value in `nrange`. Same length as `nrange`.

        Notes
        -----
        - Misfits are computed as half the squared residual norm (scaled by noise) 
          for each reconstruction.
        - Ensures `fix_vec` is incorporated into the strain matrix for every value 
          in `nrange`.
        """

        if debug:
            print("misfit fix pre handle")
            print(meas)
            print(gamma)
        (meas, fix_vec, gamma, cats, nanlocs) = utils.handle_input_fixed(meas, fix_vec, gamma, debug=debug)
        
        misfitvec = np.zeros(len(nrange))
        for n_idx in range(len(nrange)):
            nstrains = nrange[n_idx]
            mat_blocks = utils.binary_blocks(nstrains, cats)
            mat_blocks_p = utils.binary_blocks(nstrains-1, cats)
            
            resnorm = psimplex.lstsq_bilin_fix_vec(
                    mat_blocks, mat_blocks_p, meas, fix_vec, gamma, self.nopt, vecstep=self.lsqtol, veciters=self.lsqiter)[3]
            misfitvec[n_idx] = resnorm**2 / 2

        return misfitvec
    
    def compute_and_misfit_fixed(self, meas, nstrains, force_vec, gamma=None, uncertainty=False):
        """
        Compute reconstruction and misfit simultaneously with a fixed strain.

        Parameters
        ----------
        meas : array_like
            Measurement vector or matrix.
        nstrains : int
            Number of strains in the reconstruction.
        force_vec : array_like
            Fixed strain to include in the reconstruction.
        gamma : scalar or array_like, optional
            Standard deviation of Gaussian measurement noise.
        uncertainty : bool, optional
            Whether to compute posterior statistics. Default is False.

        Returns
        -------
        result : tuple
            Tuple of reconstructed strains and frequencies, optionally with posterior stats.
        misfit : float
            Misfit of the reconstruction.
        """
        # If uncertainty is needed, get posterior stats
        if uncertainty:
            (meanmat, meanvec, devmat, devvec) = self.posterior_stats(meas, nstrains, gamma)
    
        # Preprocess inputs
        (meas_proc, force_vec_proc, gamma_proc, cats, nanlocs) = utils.handle_input_fixed(meas, force_vec, gamma)
        mat_blocks = utils.binary_blocks(nstrains, cats)
        mat_blocks_p = utils.binary_blocks(nstrains - 1, cats)
    
        # Solve for strain matrix and frequency vector
        (strainmat, freqvec, _, resnorm) = psimplex.lstsq_bilin_fix_vec(
            mat_blocks, mat_blocks_p, meas_proc, force_vec_proc, gamma_proc, self.nopt,
            vecstep=self.lsqtol, veciters=self.lsqiter)
    
        # Sort strains by descending frequency
        sort_idx = freqvec.argsort()[::-1]
        strainmat = strainmat[:, sort_idx]
        freqvec = freqvec[sort_idx]
    
        # Post-process strain matrix
        strainmat = utils.binmat2intmat(strainmat, cats)
        strainmat = utils.addnanrows(strainmat, nanlocs)
        strainmat = strainmat.T
    
        # Compute misfit
        misfit = resnorm**2 / 2
    
        if uncertainty:
            return strainmat, freqvec, meanmat, meanvec, devmat, devvec, misfit
    
        return (strainmat, freqvec), misfit



    def posterior_stats(self, meas, nstrains, gamma, quad_nodes=None):
        """Posterior means and standard deviations for the matrix and vector.

        Parameters
        ----------
        meas : vector or 2D-array
            See the description of `meas` parameter in `compute`.
        nstrains : int
            Number of strains.
        gamma : scalar, vector, or 2D-array
            See the descriptions of `gamma` and `uncertainty` parameters in
            `compute`.
        quad_nodes : None, int, or 2D-array, optional
            If None, the quadrature nodes are drawn uniformly. The number of
            nodes is then determined by the `nint` attribute. An integer
            (scalar) argument can be used to override the number of nodes. The
            nodes can also be provided explicitly in a (k, `nstrains`) array,
            where k is a positive integer. Each node should be represented in
            descending order.

        Returns
        -------
        meanmat : 2D- or 3D-array
            Expected strain matrix (posterior mean). If the shape of `meas` is
            (m,), then `meanmat` has shape (`nstrains`, m). If `meas` is a
            (c, m) array, then the shape of `meanmat` is (c, `nstrains`, m) and
            each `meanmat[i]` contains the expected proportion of the i'th
            category.
        meanvec : vector
            Posterior mean of the frequency vector, shape is (`nstrains`,).
        devmat : 2D- or 3D-array
            Square roots of the posterior covariance for the strain matrix.
            Same shape as `meanmat`.
        devvec : vector
            Square roots of the posterior covariance for the frequency vector.

        Raises
        ------
        ValueError if gamma is None.

        """
        if gamma is None:
            raise ValueError("noise level required for posterior statistics")
        else:
            (meas, gamma, cats, nanlocs) = utils.handle_input(meas, gamma)

        if quad_nodes is None:
            quad_nodes = psimplex.rand_simplex(nstrains, self.nint, sort=-1)
        elif np.isscalar(quad_nodes):
            quad_nodes = psimplex.rand_simplex(nstrains, quad_nodes, sort=-1)

        mat_blocks = utils.binary_blocks(nstrains, cats)

        (meanmat, meanvec, varmat, varvec) = integration.mean_var(mat_blocks, meas, gamma, quad_nodes)
        devmat = np.sqrt(varmat)
        devvec = np.sqrt(varvec)

        if cats > 2:
            meanmat = np.reshape(meanmat, (-1, cats, nstrains)).swapaxes(0, 1)
            devmat = np.reshape(devmat, (-1, cats, nstrains)).swapaxes(0, 1)

        meanmat = utils.addnanrows(meanmat, nanlocs)
        devmat = utils.addnanrows(devmat, nanlocs)

        if cats > 2:
            meanmat = meanmat.swapaxes(1, 2)
            devmat = devmat.swapaxes(1, 2)
        else:
            meanmat = meanmat.T
            devmat = devmat.T

        return meanmat, meanvec, devmat, devvec


    def random_data(self, nmeas, nstrains, cats=None, gamma=None, fixed_freq=None, major_allelic_frequency=None):
        """Random measurement vector or matrix.

        Generates a random measurement by drawing the strain barcode matrix and
        the frequency vector from uniform distributions.

        Parameters
        ----------
        nmeas : int
            Number of measurements. This is the length of the measurement
            vector or the number of columns in a measurement matrix.
        nstrains : int
            Number of strains when generating the data.
        cats : None or int, optional
            Number of categories, i.e., the number of different elements in the
            barcode. None (default) corresponds to two categories with a vector
            format.
        gamma : None, scalar, vector, or 2D-array, optional
            Noise in the measurement. If None (default), no measurement noise
            is added. Otherwise, `gamma` determines the standard deviation of
            the independent, zero-mean Gaussian random variables representing
            the measurement noise. See also the description of `gamma`
            parameter in `compute`.
        fixed_freq: None, scalar, optional
            If specified, one of the strains will have the specified frequency
        major_allelic_frequency : float in (0, 1), optional
            If specified, the major allele is present at this probability across strains.

        Returns
        -------
        meas : vector or 2D-array
            Measurement array. If `cats` is None, the shape is (`nmeas`,).
            Otherwise, the shape is (`cats`, `nmeas`). See also the description
            of the `meas` parameter in `compute`.
        strains : 2D array
            Strain barcodes in a (`nstrains`, `nmeas`) integer array. Elements
            are in {0, ..., cats-1}.
        freq : vector
            Strain frequencies. These are sorted in descending order and they
            correspond to the rows in `strains`.

        """
        freq = psimplex.rand_simplex(nstrains, sort=-1, fixed_value=fixed_freq)

        if cats is None:
            if major_allelic_frequency is not None:
                # Draw from Bernoulli with success probability = major_allelic_frequency
                strains = np.random.binomial(1, major_allelic_frequency, (nstrains, nmeas)).astype(int)
            else:
                # default to 50/50
                strains = np.random.randint(0, 2, (nstrains, nmeas), dtype=int)
            meas = np.dot(freq, strains)
        else:
            if major_allelic_frequency is not None:
                print("Warning! Major Allele Frequency not yet implemented for cats>2. Reverting to default behavior.")
            strains = np.random.randint(0, cats, (nstrains, nmeas), dtype=int)
            binmat = utils.intmat2binmat(strains.T, cats-1)
            meas = np.dot(binmat, freq)
            meas = np.reshape(meas, (cats-1, nmeas), 'F')
            meas = np.vstack((1 - np.sum(meas, 0), meas))

        if gamma is not None:
            if not np.isscalar(gamma) and gamma.shape != meas.shape:
                # now gamma is 2D and meas is 3D
                gamma = np.tile(gamma, (np.size(meas, 0), 1))
            meas = meas + gamma * np.random.normal(size=meas.shape)

        return meas, strains, freq
    
    
    def random_paired_data(self, nmeas, nstrains, cats=None, gamma=0.01):
        """Generate paired random measurement data.

        This function creates two sets of paired measurement data. The strain barcode matrix is shared
        between the two datasets, but the frequency vectors are independently sampled. Optional Gaussian
        noise is added to the measurements.

        Parameters
        ----------
        nmeas : int
            Number of measurements. This is the length of each measurement vector.
        nstrains : int
            Number of strains when generating the data.
        cats : None or int, optional
            Number of categories. Only supports `None` (default), corresponding to two categories
            with a vector format. Raises an error if specified.
        gamma : scalar, optional
            Noise in the measurement. Default is 0.01. This determines the standard deviation of the
            independent, zero-mean Gaussian random variables representing the measurement noise.

        Returns
        -------
        data1 : tuple
            A tuple (meas1, strains, freq1) representing the first dataset:
            - meas1: Measurement vector (shape `(nmeas`,)).
            - strains: Shared strain barcode matrix (shape `(nstrains, nmeas)`).
            - freq1: Frequency vector for the first dataset (sorted in descending order).
        data2 : tuple
            A tuple (meas2, strains, freq2) representing the second dataset:
            - meas2: Measurement vector (shape `(nmeas`,)).
            - strains: Shared strain barcode matrix (shape `(nstrains, nmeas)`).
            - freq2: Frequency vector for the second dataset (sorted in descending order).

        Notes
        -----
        The function uses independent frequency vectors (`freq1` and `freq2`) to generate two
        paired measurement datasets with shared strain barcodes.
        """

        # Generate two random frequency vectors
        freq1 = psimplex.rand_simplex(nstrains, sort=-1)
        freq2 = psimplex.rand_simplex(nstrains, sort=-1)

        if cats is None:
            # Binary strain barcodes
            strains = np.random.randint(0, 2, (nstrains, nmeas), dtype=int)
            meas1 = np.dot(freq1, strains)
            meas2 = np.dot(freq2, strains)
        else:
            # Multi-category strain barcodes
            strains = np.random.randint(0, cats, (nstrains, nmeas), dtype=int)
            binmat = utils.intmat2binmat(strains.T, cats - 1)

            meas1 = np.dot(binmat, freq1)
            meas1 = np.reshape(meas1, (cats - 1, nmeas), 'F')
            meas1 = np.vstack((1 - np.sum(meas1, 0), meas1))

            meas2 = np.dot(binmat, freq2)
            meas2 = np.reshape(meas2, (cats - 1, nmeas), 'F')
            meas2 = np.vstack((1 - np.sum(meas2, 0), meas2))

        # Add Gaussian noise if specified
        if gamma is not None:
            if not np.isscalar(gamma) and gamma.shape != meas1.shape:
                # now gamma is 2D and meas is 3D
                gamma = np.tile(gamma, (np.size(meas1, 0), 1))
                
            meas1 = meas1 + gamma * np.random.normal(size=meas1.shape)
            meas2 = meas2 + gamma * np.random.normal(size=meas2.shape)

        return (meas1, strains, freq1), (meas2, strains, freq2)
    
    
    
    def random_data_with_shared_strain(self, nmeas, nstrains, shared_index=None, shared_freq=None, cats=None, gamma=0.01,
                                      major_allelic_frequency=None):
        """
        Generate two random datasets sharing one strain barcode.

        The shared strain may be either:
            - at a specified shared index (`shared_index`), OR
            - present with a specified shared frequency (`shared_freq`).

        This function creates two sets of measurement data with independently sampled strain barcodes,
        except for one strain that is shared between the two datasets. The shared strain can either
        occupy the same index in both strain matrices, or correspond to a strain associated with the same
        frequency value in both frequency vectors. Each dataset uses its own frequency vector, with one
        frequency optionally constrained to be shared. Optional Gaussian noise is added to the measurements.

        Exactly one of `shared_index` or `shared_freq` must be specified.

        Parameters
        ----------
        nmeas : int
            Number of measurements (columns in the strain matrix).
        nstrains : int
            Total number of strains per dataset.
        shared_index : int, optional
            Index at which the strain barcode is shared between the two datasets.
        shared_freq : float, optional
            Frequency value to be shared between both datasets. Must be in [0, 1].
        cats : None or int, optional
            Number of categories. If None (default), assumes binary (0/1) strain values.
        gamma : scalar or array, optional
            Standard deviation of Gaussian noise added to each measurement. Default is 0.01.
        major_allelic_frequency : float in (0, 1), optional
            If specified, the major allele is present at this probability across strains.

        Returns
        -------
        data1 : tuple
            A tuple (meas1, strains1, freq1) representing the first dataset.
        data2 : tuple
            A tuple (meas2, strains2, freq2) representing the second dataset.
        """

        
        if (shared_index is not None) and (shared_freq is not None):
            raise ValueError("Specify only one of shared_index or shared_freq.")
        if (shared_index is None) and (shared_freq is None):
            raise ValueError("You must specify either shared_index or shared_freq.")
            
        if shared_freq is not None:
            if not (0 <= shared_freq <= 1):
                raise ValueError("shared_freq must be between 0 and 1.")
        else:
            if not (0 <= shared_index < nstrains):
                raise ValueError(f"shared_index must be between 0 and nstrains-1 (got {shared_index})")
            
            
        # Generate random frequency vectors
        freq1 = psimplex.rand_simplex(nstrains, sort=-1, fixed_value=shared_freq)
        freq2 = psimplex.rand_simplex(nstrains, sort=-1, fixed_value=shared_freq)
            
        if shared_freq is not None:
            try:
                shared_index1 = np.where(np.isclose(freq1, shared_freq))[0][0]
                shared_index2 = np.where(np.isclose(freq2, shared_freq))[0][0]
            except IndexError:
                raise RuntimeError("Failed to find shared frequency in frequency vectors.")
        else:
            shared_index1 = shared_index2 = shared_index


        # Generate a shared strain barcode
        if cats is None:
            if major_allelic_frequency is not None:
                shared_strain = np.random.binomial(1, major_allelic_frequency, (1, nmeas)).astype(int)
            else:
                shared_strain = np.random.randint(0, 2, (1, nmeas), dtype=int)
        else:
            if major_allelic_frequency is not None:
                print("Warning! Major Allele Frequency not yet implemented for cats > 2. Reverting to uniform random.")
            shared_strain = np.random.randint(0, cats, (1, nmeas), dtype=int)

        def generate_strains():
            if cats is None:
                if major_allelic_frequency is not None:
                    strains1 = np.random.binomial(1, major_allelic_frequency, (nstrains, nmeas)).astype(int)
                    strains2 = np.random.binomial(1, major_allelic_frequency, (nstrains, nmeas)).astype(int)
                else:
                    strains1 = np.random.randint(0, 2, (nstrains, nmeas), dtype=int)
                    strains2 = np.random.randint(0, 2, (nstrains, nmeas), dtype=int)
            else:
                strains1 = np.random.randint(0, cats, (nstrains, nmeas), dtype=int)
                strains2 = np.random.randint(0, cats, (nstrains, nmeas), dtype=int)
            strains1[shared_index1] = shared_strain
            strains2[shared_index2] = shared_strain
            return strains1, strains2

        # Retry until exactly one shared strain
        max_attempts = 100
        for _ in range(max_attempts):
            strains1, strains2 = generate_strains()

            shared_count = sum(
                np.array_equal(strains1[i], strains2[j])
                for i in range(nstrains)
                for j in range(nstrains)
            )

            if shared_count == 1 and np.array_equal(strains1[shared_index1], strains2[shared_index2]):
                break
        else:
            raise RuntimeError("Failed to generate strains with exactly one shared strain after multiple attempts.")

        # Generate measurements
        if cats is None:
            meas1 = np.dot(freq1, strains1)
            meas2 = np.dot(freq2, strains2)
        else:
            binmat1 = utils.intmat2binmat(strains1.T, cats - 1)
            meas1 = np.dot(binmat1, freq1)
            meas1 = np.reshape(meas1, (cats - 1, nmeas), 'F')
            meas1 = np.vstack((1 - np.sum(meas1, 0), meas1))

            binmat2 = utils.intmat2binmat(strains2.T, cats - 1)
            meas2 = np.dot(binmat2, freq2)
            meas2 = np.reshape(meas2, (cats - 1, nmeas), 'F')
            meas2 = np.vstack((1 - np.sum(meas2, 0), meas2))

        # Add Gaussian noise
        if gamma is not None:
            if not np.isscalar(gamma) and gamma.shape != meas1.shape:
                gamma = np.tile(gamma, (np.size(meas1, 0), 1))

            meas1 = meas1 + gamma * np.random.normal(size=meas1.shape)
            meas2 = meas2 + gamma * np.random.normal(size=meas2.shape)

        return (meas1, strains1, freq1), (meas2, strains2, freq2)


    
    
    
   
    
    
    