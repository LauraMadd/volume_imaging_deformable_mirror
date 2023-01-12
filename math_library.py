import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
from scipy.fftpack import fft, ifft, fft2, ifft2, fftn, ifftn,fftshift,ifftshift

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
from inspect import currentframe
def debug_hint():
    frameinfo = currentframe()
    print '\n{line: ', frameinfo.f_back.f_lineno,'}\n'
    return None
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def FT(f):
    return fftshift(fft(fftshift(f)))
    
def FT2(f):
    return fftshift(fft2(fftshift(f)))

def FT3(f):
    return fftshift(fftn(fftshift(f)))

def IFT(F):
    return ifftshift(ifft(ifftshift(F)))

def IFT2(F):
    return ifftshift(ifft2(ifftshift(F)))
    
def IFT3(F):
    return ifftshift(ifftn(ifftshift(F)))
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def rebin(arr, new_shape):
    shape = (new_shape[0], arr.shape[0] // new_shape[0],
             new_shape[1], arr.shape[1] // new_shape[1])
    return arr.reshape(shape).mean(-1).mean(1)
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def step(x):
    """Step function:
                    - x = domain.
    """
    return .5*(1+sp.sign(x))
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def rect(x,p=[0.,1.]):
    """Rectangular function
                      - x = domain;
                      - p[0] = center;
                      - p[1] = width.
    """
    return step((x-p[0])/p[1]+.5)-step((x-p[0])/p[1]-.5)
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def gaus(x, p = [0,1]):
    """Gaussian with:
                      - x = domain;
                      - p[0] = center;
                      - p[1] = width.
    """
                      
    return np.exp(-np.pi*(x-p[0])**2/(p[1]**2))
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def gaus_2d_forFit((X, Y), p0, p1, p2, p3):
    return np.exp(-(np.pi*(X-p0)**2)/(p1**2)-(np.pi*(Y-p2)**2)/(p3**2))\
            .ravel()
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def double_gaus_2d_forFit((X, Y), Xp1, XWp1, Yp1, YWp1, Xp2, XWp2, Yp2, YWp2,\
                                    Hp1, Hp2):
    return (Hp1*np.exp(-(np.pi*(X-Xp1)**2)/\
                                    (XWp1**2)-(np.pi*(Y-Yp1)**2)/(YWp1**2))\
            +Hp2*np.exp(-(np.pi*(X-Xp2)**2)/\
                                    (XWp2**2)-(np.pi*(Y-Yp2)**2)/(YWp2**2)))\
            .ravel()
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def crossCorr (f, g):
    """Cross-correlation function, with padding. For flows: it will
        highligh a flow of particle f --> g;
                        - f = first signal;
                        - g = second signal.
        """   
    N = len(f)
    one, two = np.pad(np.copy(f),\
                    (N/2),\
                            mode = 'constant', constant_values=(0)),\
               np.pad(np.copy(g),\
                    (N/2),\
                            mode = 'constant', constant_values=(0))
    F, G = FT(one), FT(two)
    
    cross = np.real(ifft(np.conj(ifftshift(F))*(ifftshift(G))))[:N]
    
    return cross
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def crossCorrFluct (f, g):
    """Cross-correlation function of the
        fluctuations of two signals, with padding, normalized for
        average intensities(<I>).
        For flows: it will highligh a flow of particle g --> f;
                        - f = first signal;
                        - g = second signal.
        """   
    N = len(f)
    mean_f, mean_g = np.mean(f), np.mean(g)
    
    one, two = np.pad(np.copy(f-mean_f),\
                    (N/2),\
                            mode = 'constant', constant_values=(0)),\
               np.pad(np.copy((g-mean_g)),\
                    (N/2),\
                            mode = 'constant', constant_values=(0))
    F, G = FT(one), FT(two) 
    
    return np.real(ifft(np.conj(ifftshift(F))*(ifftshift(G)))\
                                                        /mean_f/mean_g)[:N]
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def spatial_Xcorr_2(f, g):
    """
    Cross-correlation between two 2D functions (f * g)
    """
    M, N = f.shape[0], f.shape[1]
    
    one, two = np.pad(np.copy(f),\
                    ((M/2, M/2),(N/2, N/2)),\
                            mode = 'constant', constant_values=(0,0)),\
               np.pad(np.copy(g),\
                    ((M/2, M/2),(N/2, N/2)),\
                            mode = 'constant', constant_values=(0,0))
                            
    ONE, TWO =   FT2(one), FT2(two)

    spatial_cross = ifftshift(ifft2(ifftshift(ONE) * np.conj(ifftshift(TWO))))\
    [M/2 :M/2+M, N/2 : N/2+N]

    return spatial_cross
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def stics(f, mean_space, delay, duration):
    """ STICS normalized for time and space, with Heaviside in FT domain.
    """
    #
    # set up all the elements and parameters
    #
    T, M, N = f.shape
    cross = np.zeros((M, N))
    #
    # spatial correlation
    #
    
    for k in range(duration - delay):
        cross += np.real(\
            spatial_Xcorr_2(f[k, :, :], f[k+delay, :, :]))/\
                    mean_space[k]/mean_space[k+delay]
        
    return cross
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def norm_for_slm(matrix, norm = 256., full_phase_pixel_value = 161):
    """
    Make the input suitable for SLM
    (rescaled into 256 levels, uint8)
    """
    if (matrix.ptp() > 0.):
        return (((matrix - matrix.min())/(matrix.ptp()/256.)).astype(np.uint8))\
                *full_phase_pixel_value * 255
    else:
        print '\n\n I tried to rescale a matrix of zeros @ \n\n' 
        debug_hint()
        return matrix
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -






















