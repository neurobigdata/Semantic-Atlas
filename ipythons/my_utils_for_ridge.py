import numpy as np
from utils import mult_diag

zs = lambda v: (v-v.mean(0))/v.std(0) ## z-score function

def precompute_svd(Rstim, singcutoff=1e-10):
    #logger.info("Doing SVD...")
    try:
        U,S,Vh = np.linalg.svd(Rstim, full_matrices=False)
    except np.linalg.LinAlgError, e:
        print "NORMAL SVD FAILED, trying more robust dgesvd.."
        #logger.info("NORMAL SVD FAILED, trying more robust dgesvd..")
        from text.regression.svd_dgesvd import svd_dgesvd
        U,S,Vh = svd_dgesvd(Rstim, full_matrices=False)

    ## Truncate tiny singular values for speed
    origsize = S.shape[0]
    ngoodS = np.sum(S>singcutoff)
    nbad = origsize-ngoodS
    U = U[:,:ngoodS]
    S = S[:ngoodS]
    Vh = Vh[:ngoodS]
    
    return U, S, Vh


def ridge_corr(Rstim, Pstim, Rresp, Presp, U, S, Vh, alphas, filename, 
               dtype=np.single, corrmin=0.2,use_corr=True):
    ## Precompute some products for speed
    UR = np.dot(U.T, Rresp)
    PVh = np.dot(Pstim, Vh.T)
    
    zPresp = zs(Presp)
    Prespvar = Presp.var(0)
    Rcorrs = [] ## Holds training correlations for each alpha
    
    result = list()
    for a in alphas:
        D = S/(S ** 2 + a ** 2) ## Reweight singular vectors by the (normalized?) ridge parameter
        pred = np.dot(mult_diag(D, PVh, left=False), UR) ## Best (1.75 seconds to prediction in test)

        if use_corr:
            Rcorr = (zPresp*zs(pred)).mean(0)
        else:
            resvar = (Presp-pred).var(0)
            Rcorr = np.clip(1-(resvar/Prespvar), 0, 1)
            
        Rcorr = np.nan_to_num(Rcorr)
        Rcorrs.append(Rcorr)
        result.append([a, np.mean(Rcorr)])
    
    np.save(filename, np.array(result))
    
    return Rcorrs