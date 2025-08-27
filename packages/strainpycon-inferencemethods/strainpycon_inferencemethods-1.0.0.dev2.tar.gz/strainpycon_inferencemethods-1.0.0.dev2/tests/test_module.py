import numpy as np
from strainpycon_inferencemethods import StrainRecon, StrainMatchB, StrainMatchT

np.random.seed(1)

def setup_data():
    """Helper to generate reproducible synthetic datasets."""
    S = StrainRecon()
    m, n = 24, 3  # SNP sites, number of strains

    (meas1, strains1, freq1), (meas2, strains2, freq2) = S.random_data_with_shared_strain(
        m, n, shared_index=0, gamma=0.00
    )
    (measZ, strainsZ, freqZ) = S.random_data(m, n, gamma=0.00)

    return S, meas1, strains1, meas2, strains2, measZ


def test_fixed_reconstructions():
    S, meas1, strains1, meas2, strains2, measZ = setup_data()
    strain_of_interest = strains1[0]

    strainmat, freqvec = S.compute_fixed(meas1, 4, strain_of_interest)
    assert strain_of_interest in strainmat

    strainmat, freqvec = S.compute_fixed(meas2, 4, strain_of_interest)
    assert strain_of_interest in strainmat

    strainmat, freqvec = S.compute_fixed(measZ, 4, strain_of_interest)
    assert strain_of_interest in strainmat


def test_strainmatch_b():
    S, meas1, strains1, meas2, strains2, measZ = setup_data()
    strain_of_interest = strains1[0]
    smb = StrainMatchB(S)

    assert smb.is_strain_in_sample(
        meas1, strain_of_interest, k=5, gamma=0.01, 
        bayes_k_threshold=0.1, fixed_proportion_threshold=0.05
    )

    assert smb.is_strain_in_sample(
        meas2, strain_of_interest, k=5, gamma=0.01, 
        bayes_k_threshold=0.1, fixed_proportion_threshold=0.05
    )

    assert not smb.is_strain_in_sample(
        measZ, strain_of_interest, k=5, gamma=0.01, 
        bayes_k_threshold=0.1, fixed_proportion_threshold=0.05
    )


def test_strainmatch_t():
    S, meas1, strains1, meas2, strains2, measZ = setup_data()
    smt = StrainMatchT(S)

    assert smt.determine_similarity_of_samples(
        meas1, meas2, maxK=3, gamma=0.01, STIMThresh=1.8e-7, 
        alpha=0.05, neutral_is_positive=True
    )

    assert not smt.determine_similarity_of_samples(
        meas1, measZ, maxK=3, gamma=0.01, STIMThresh=1.8e-7, 
        alpha=0.05, neutral_is_positive=True, verbose=False
    )
