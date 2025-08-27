import numpy as np
from strainpycon_inferencemethods import utils

class StrainMatchB:
    """
    The StrainMatchB class predicts whether a strain is or isnt in a particular sample.
    It uses a StrainRecon object to compute fixed and unfixed reconstructions of the sample, finds
    1) the relative likelihoods of the reconstructions
    2) the predicted proportion of the fixed strain,
    and uses these metrics to predict the presence or absence of the strain
    """

    def __init__(self, strain_recon):
        """
        Initialize with a reference to a StrainRecon object.

        Parameters
        ----------
        strain_recon : StrainRecon
            Reference to a StrainRecon object.
        """
        self.strain_recon = strain_recon

    
    
    def do_disambiguation_for_k(self, x, force_vec, k, gamma=0.05, debug=False):
        """
        Perform disambiguation for a given k using fixed strain matching.

        Parameters
        ----------
        x : array-like
            Input frequency vector.
        force_vec : np.ndarray
            Strain vector to fix during reconstruction (can contain NaNs for wildcard positions).
        k : int
            Number of strains to infer.
        gamma : float, optional
            Noise parameter. Default is 0.05.
        debug : bool, optional
            If True, prints debugging information. Default is False.

        Returns
        -------
        umf : float
            Unfixed misfit from standard strain reconstruction.
        fmf : float
            Misfit when fixing inclusion of `force_vec`.
        fsr : np.ndarray
            Reconstruction result when fixing `force_vec` as one of the strains.
        """
        
        umfs = self.strain_recon.misfits(x, (k,), gamma=gamma)
        # the above method returns a list containing misfits for every provided value of k. we only provided one.
        umf = umfs[0]

        fsr, fmf = self.strain_recon.compute_and_misfit_fixed(x, k, force_vec, gamma=gamma, uncertainty=False)

        return umf,fmf,fsr

    

    def process_disambiguation(self, unfixed_misfit, fixed_misfit, fixed_reconstruction, fix_vec):
        """
        Process disambiguation results by calculating Bayes factor and fixed strain proportion.

        Parameters
        ----------
        unfixed_misfit : float
            Misfit of the unfixed strain reconstruction.
        fixed_misfit : float
            Misfit of the fixed strain reconstruction.
        fixed_reconstruction : tuple
            Strain matrix and frequencies.
        fix_vec : np.ndarray
            Fixed strain vector.

        Returns
        -------
        bayes_factor : float
            Ratio of unfixed misfit to fixed misfit.
        fixed_prop : float
            Proportion of the fixed strain in the reconstruction.
        """
        
        # find proportion
        strainmat, freqs = fixed_reconstruction
        _, props_in_reconstruction = utils.find_strain_in_strains(strainmat, freqs, fix_vec)

        if not props_in_reconstruction:
            raise ValueError("Fixed strain not found in the strain reconstruction.")
        fixed_prop = props_in_reconstruction[0]

        # find bayes factor
        if fixed_misfit == 0:
            bayes_factor = float('inf')  # or some large constant, depending on your use case
        else:
            bayes_factor = unfixed_misfit**2 / fixed_misfit**2
        
        
        return bayes_factor, fixed_prop
    
    

    def is_strain_in_sample(self, sample_vector, strain_vector, k=5, gamma=0.01, bayes_k_threshold=0.1, fixed_proportion_threshold=0.05,
                           debug=False):
        """
        Determine if a specific strain is present in a given sample using MICOS-B.
        
        Parameters
        ----------
        sample_vector : np.ndarray
            Vector representation of the sample.
        strain_vector : np.ndarray
            Vector representation of the strain.
        k : int, optional
            Number of strains to reconstruct the sample with. Default is 5.
        gamma : float, optional
            Gaussian noise level in the sample. Default is 0.01.
        bayes_k_threshold : float, optional
            Minimum Bayes factor threshold for strain presence. Default is 0.1.
        fixed_proportion_threshold : float, optional
            Minimum fixed strain proportion threshold. Default is 0.05.
        debug : bool, optional
            If True, prints debugging info. Default is False.

        Returns
        -------
        bool
            True if the strain is likely present in the sample, False otherwise.
        """
        
        if debug:
            print("is strain in sample fix vec")
            print(strain_vector)
        
        unfixed_misfit, fixed_misfit, fixed_reconstruction = self.do_disambiguation_for_k(
            sample_vector, strain_vector, k, gamma=gamma, debug=debug
        )
        
        bayes_factor, fixed_proportion = self.process_disambiguation(
            unfixed_misfit, fixed_misfit, fixed_reconstruction, strain_vector
        )

        is_bayes_factor_high_enough = bayes_factor > bayes_k_threshold
        is_fixed_proportion_high_enough = fixed_proportion > fixed_proportion_threshold

        return is_bayes_factor_high_enough and is_fixed_proportion_high_enough
    
    



import numpy as np
from scipy.stats import norm
from statsmodels.stats.multitest import multipletests

class StrainMatchT:
    """
    The StrainMatchT class provides methods to determine strain similarity 
    of strains found using StrainRecon
    based on the differences in their SNPs
    and the uncertainties in those SNPs.
    
    Currently, StrainMatchT only works for strains made from
    biallelic SNPs.
    """

    def __init__(self, strain_recon):
        """
        Initialize with a reference to a StrainRecon object.

        Parameters
        ----------
        strain_recon : StrainRecon
            Reference to a StrainRecon object.
        """
        self.strain_recon = strain_recon
        
       
    def calculate_p_value(self, mean_snp, sdev, value):
        """
        Calculate the p-value for a given SNP value.

        Parameters
        ----------
        mean_snp : float
            Mean SNP value.
        sdev : float
            Standard deviation of the SNP.
        value : float
            SNP value to test.

        Returns
        -------
        float
            P-value for the hypothesis test.
        """
        if sdev == 0 or mean_snp == value:
            return 1.0 if mean_snp == value else 0.0
        z = (mean_snp - value) / sdev
        return norm.sf(abs(z))

    def snp_probability(self, mean_snp, sdev, target):
        """
        Compute the probability of a SNP being the target allele.

        Parameters
        ----------
        mean_snp : float
            Mean SNP value.
        sdev : float
            Standard deviation of the SNP.
        target : int
            Target allele (0 or 1).

        Returns
        -------
        float
            Probability that the SNP equals the target value.
        """
        p_target = self.calculate_p_value(mean_snp, sdev, target)
        p_other = self.calculate_p_value(mean_snp, sdev, 1 - target)

        # Handle edge case: if both probabilities are 0
        if p_target == 0 and p_other == 0:
            if mean_snp > 0.5:
                return 1.0 if target == 1 else 0.0
            if mean_snp < 0.5:
                return 0.0 if target == 1 else 1.0
            return 0.5  # mean_snp == 0.5

        return p_target / (p_target + p_other)

    def same_side_chance(self, mean_snp1, sdev1, mean_snp2, sdev2):
        """
        Calculate the probability that two SNPs fall on the same allele side.

        Parameters
        ----------
        mean_snp1 : float
            Mean SNP value of the first SNP.
        sdev1 : float
            Standard deviation of the first SNP.
        mean_snp2 : float
            Mean SNP value of the second SNP.
        sdev2 : float
            Standard deviation of the second SNP.

        Returns
        -------
        float
            Probability that both SNPs correspond to the same allele (both 0 or both 1).
        """
        if np.isnan(mean_snp1) or np.isnan(mean_snp2):
            return 0.5

        p_both_1 = self.snp_probability(mean_snp1, sdev1, 1) * self.snp_probability(mean_snp2, sdev2, 1)
        p_both_0 = self.snp_probability(mean_snp1, sdev1, 0) * self.snp_probability(mean_snp2, sdev2, 0)

        return p_both_1 + p_both_0

    def snp_match_probabilities(self, mean_strain_vec1, sdevs1, mean_strain_vec2, sdevs2):
        """
        Compute match probabilities for each SNP across two strains.

        Parameters
        ----------
        mean_strain_vec1 : array-like of float
            Mean SNP values for strain 1.
        sdevs1 : array-like of float
            Standard deviations for strain 1 SNPs.
        mean_strain_vec2 : array-like of float
            Mean SNP values for strain 2.
        sdevs2 : array-like of float
            Standard deviations for strain 2 SNPs.

        Returns
        -------
        list of float
            Probabilities that each SNP pair matches.
        """
  
        n = len(mean_strain_vec1)
        if not all(len(lst) == n for lst in [sdevs1, mean_strain_vec2, sdevs2]):
            raise ValueError(
                f"Input vectors must all have the same length. Got lengths: "
                f"mean1={len(mean_strain_vec1)}, sdev1={len(sdevs1)}, "
                f"mean2={len(mean_strain_vec2)}, sdev2={len(sdevs2)}"
            )
        
        return [
            self.same_side_chance(mean_strain_vec1[i], sdevs1[i], mean_strain_vec2[i], sdevs2[i])
            for i in range(n)
        ]

    def do_all_snps_match(self, prob_same, alpha):
        """
        Determine whether all SNPs match with confidence level (1 - alpha).

        Parameters
        ----------
        prob_same : list of float
            Probabilities that each SNP pair matches.
        alpha : float
            Significance level.

        Returns
        -------
        def_the_same : bool
            True if all SNPs match with confidence, False otherwise.
        snps_that_match : list of bool
            Indicator for which SNPs matched.
        """
        snps_that_match = [p >= 1 - alpha for p in prob_same]
        def_the_same = all(snps_that_match)
        return def_the_same, snps_that_match

    def determine_similarity_of_strains_using_means_and_sdevs(self, mean_strain_vec1, sdevs1, mean_strain_vec2, sdevs2, alpha=0.05, verbose=False, neutral_is_positive=True):
        """
        Determine whether two strains are similar based on SNP distributions.

        Parameters
        ----------
        mean_strain_vec1 : array-like
            Mean SNP values for strain 1.
        sdevs1 : array-like
            Standard deviations for strain 1 SNPs.
        mean_strain_vec2 : array-like
            Mean SNP values for strain 2.
        sdevs2 : array-like
            Standard deviations for strain 2 SNPs.
        alpha : float, default=0.05
            Significance level for hypothesis testing.
        verbose : bool, default=False
            If True, print detailed results.
        neutral_is_positive : bool, default=True
            If True, treat neutral comparisons as positive.

        Returns
        -------
        int or float
            -1 if strains are different, 1 if the same, or a fraction
            indicating uncertainty.
        """
        prob_same = self.snp_match_probabilities(mean_strain_vec1, sdevs1, mean_strain_vec2, sdevs2)

        # Apply Benjamini-Yekutieli correction
        same_rejections, _, _, _ = multipletests(prob_same, alpha, method='fdr_by')
        reject_def_the_same = bool(sum(same_rejections))

        # Determine if all SNPs match with 1-alpha confidence
        def_the_same, snps_that_match = self.do_all_snps_match(prob_same, alpha)

        if verbose:
            print("Comparing these two strains...")
            print("Failed matches:", same_rejections)
            print("Are they definitely different?...", reject_def_the_same)
            print("Matching SNPs:", snps_that_match)
            print("Are they definitely the same?...", def_the_same)

        # Negative results
        if reject_def_the_same:
            return -1

        # Positive results
        if def_the_same or neutral_is_positive:
            return 1

        # Neutral results
        n_matching_snps = sum(snps_that_match)
        return n_matching_snps / len(prob_same)
    
    
    

    
    
    def reconstruct_with_uncertainties(self, x, maxK=5, gamma=0.01, STIMThresh=1.8e-7):
        """
        Reconstruct a sample with uncertainties and estimate multiplicity of infection (MOI).

        Parameters
        ----------
        x : array-like
            Input measurement vector.
        maxK : int, default=5
            Maximum number of strains to test.
        gamma : float, default=0.01
            Noise level added to the measurement.
        STIMThresh : float, default=1.8e-7
            Misfit threshold for MOI.

        Returns
        -------
        misfit : float
            Misfit for predicted MOI.
        moi : int
            Predicted multiplicity of infection (MOI).
        reconstruction : tuple
            Reconstruction result containing strain matrix, frequency vector,
            mean matrix, deviation matrix, etc.
        """
        # Step 1: Calculate misfits using the provided data `x` and range of k-values
        mfs = self.strain_recon.misfits(x, np.arange(1,maxK+1), gamma=gamma)

        # Step 2: Determine the Multiplicity of Infection (MOI) by counting misfits above the threshold
        STIM_MOI = sum(mfs > STIMThresh) + 1

        # Step 3: Perform the reconstruction for the predicted MOI, including uncertainties
        reconstruction = self.strain_recon.compute(x, STIM_MOI, gamma=gamma, uncertainty=True)

        # Return the misfit corresponding to the predicted MOI, the predicted MOI, and the reconstruction
        return mfs[STIM_MOI - 1], STIM_MOI, reconstruction
    
    def determine_similarity_of_samples_means_and_sdevs(self, meanmat1, devmat1, meanmat2, devmat2,
                                                    alpha=0.05, verbose=False, neutral_is_positive=True):
        """
        Compare mean and standard deviation matrices from two samples.

        Parameters
        ----------
        meanmat1 : array-like
            Mean SNP matrices from sample 1.
        devmat1 : array-like
            Standard deviation matrices from sample 1.
        meanmat2 : array-like
            Mean SNP matrices from sample 2.
        devmat2 : array-like
            Standard deviation matrices from sample 2.
        alpha : float, default=0.05
            Significance level.
        verbose : bool, default=False
            If True, print debugging information.
        neutral_is_positive : bool, default=True
            If True, treat neutral comparisons as positive.

        Returns
        -------
        bool
            True if any strain pair matches, False otherwise.
        """
        strainMatchFound = False

        for mean_strain_vec1, sdevs1 in zip(meanmat1, devmat1):
            for mean_strain_vec2, sdevs2 in zip(meanmat2, devmat2):
                matchinessOfStrainPair = self.determine_similarity_of_strains_using_means_and_sdevs(
                    mean_strain_vec1, sdevs1, mean_strain_vec2, sdevs2,
                    alpha=alpha, verbose=verbose, neutral_is_positive=neutral_is_positive)
                if verbose:
                    print("Matchiness of this pair of strains is..." + str(matchinessOfStrainPair))

                if matchinessOfStrainPair == 1:
                    strainMatchFound = True
                    break
            if strainMatchFound:
                break

        return strainMatchFound


    def determine_similarity_of_samples(self, meas1, meas2, maxK=5, gamma=0.01, STIMThresh=1.8e-7, 
                                        alpha=0.05, verbose=False, neutral_is_positive=True):
        """
        Determine whether two measurement samples share a strain.

        Parameters
        ----------
        meas1 : array-like
            First measurement sample.
        meas2 : array-like
            Second measurement sample.
        maxK : int, default=5
            Maximum number of strains to test.
        gamma : float, default=0.01
            Noise level in reconstruction.
        STIMThresh : float, default=1.8e-7
            Threshold for MOI determination.
        alpha : float, default=0.05
            Significance level for strain comparison.
        verbose : bool, default=False
            If True, print debugging information.
        neutral_is_positive : bool, default=True
            If True, treat neutral comparisons as positive.

        Returns
        -------
        bool
            True if the samples share at least one strain, False otherwise.

        Notes
        -----
        Both samples are reconstructed with uncertainties prior to comparison.
        """
        
        # Step 1: Reconstruct the first measurement with uncertainties
        mf1, moi1, reconstruction1 = self.reconstruct_with_uncertainties(
            meas1, maxK=maxK, gamma=gamma, STIMThresh=STIMThresh)

        # Step 2: Reconstruct the second measurement with uncertainties
        mf2, moi2, reconstruction2 = self.reconstruct_with_uncertainties(
            meas2, maxK=maxK, gamma=gamma, STIMThresh=STIMThresh)

        # Extract strain matrices and deviation matrices for both measurements
        strainmat1, freqvec1, meanmat1, meanvec1, devmat1, devvec1 = reconstruction1
        strainmat2, freqvec2, meanmat2, meanvec2, devmat2, devvec2 = reconstruction2
        
        if verbose:
            print("reconstruction 1:")
            print("MOI = " + str(moi1))
            print(strainmat1)
            print(meanmat1)
            print(devmat1)
            print("reconstruction 2:")
            print("MOI = " + str(moi2))
            print(strainmat2)
            print(meanmat2)
            print(devmat2)

        # Step 3: Compare reconstructed strain means and stds
        strainMatchFound = self.determine_similarity_of_samples_means_and_sdevs(
            meanmat1, devmat1, meanmat2, devmat2,
            alpha=alpha, verbose=verbose, neutral_is_positive=neutral_is_positive)

        # Return whether a strain match was found
        return strainMatchFound




