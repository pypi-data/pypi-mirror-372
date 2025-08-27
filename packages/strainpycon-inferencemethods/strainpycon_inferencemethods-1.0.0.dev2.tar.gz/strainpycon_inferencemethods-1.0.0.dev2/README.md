# Introduction

The Strain Inference Methods (SIM)(strainpycon_inferencemethods) are a fork of the 
Python 3 strainpycon package used to disambiguate multiple strains in mixed samples of DNA. 
SIM builds upon strainpycon with methods to:
-disambiguate samples with many genetic markers (tested up to 2461 markers)
-fix a particular strain within a sample reconstruction
-compare samples for shared strains
-detect the presence or absence of particular strains in samples


# Contacts

Please direct questions to:
Gary Vestal, mojihaka@protonmail.com

# Installation

$pip install strainpycon_inferencemethods

# Test usage

import numpy as np
from strainpycon_inferencemethods import StrainRecon, StrainMatchB, StrainMatchT

S = StrainRecon()
m, n = 24, 3  # SNP sites, number of strains

(meas1, strains1, freq1), (meas2, strains2, freq2) = S.random_data_with_shared_strain(
	m, n, shared_index=0, gamma=0.00
)

strainmat, freqvec = S.compute_fixed(meas1, 4, strain_of_interest)
strainmat, freqvec = S.compute_fixed(meas2, 4, strain_of_interest)



strain_of_interest = strains1[0]
smb = StrainMatchB(S)

smb.is_strain_in_sample(
        meas1, strain_of_interest, k=5, gamma=0.01, 
        bayes_k_threshold=0.1, fixed_proportion_threshold=0.05
)



smt = StrainMatchT(S)

smt.determine_similarity_of_samples(
	meas1, meas2, maxK=3, gamma=0.01, STIMThresh=1.8e-7, 
	alpha=0.05, neutral_is_positive=True
)

# Test cases...

...are in the /test/ folder

# Strainpycon

This library was forked from strainpycon 
by Ymir Vigfusson, Lars Ruthotto, Rebecca M. Mitchell, Lauri Mustonen, and Xiangxi Gao, 
under the MIT License.

Please refer to the full documentation of StrainPycon at:
https://www.ymsir.com/strainpycon/