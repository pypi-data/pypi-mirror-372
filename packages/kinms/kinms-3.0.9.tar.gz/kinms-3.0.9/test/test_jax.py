
from kinms import KinMS
from kinms.KinMS_jax import KinMS as KinMS_jax
from kinms.utils.KinMS_figures import KinMS_plotter
import numpy as np
from scipy import interpolate
import time

def expdisk(scalerad=10, inc=60,fileName=None,toplot=False,jax=False):
    """
    A test procedure to demonstrate the KinMS code, and check if it works on your system. This procedure demonstrates how
    to create a simulation of an exponential disk of molecular gas. The user can input values for the scalerad and inc
    variables, and the procedure will the create the simulation and display it to screen.
    :param scalerad: Scale radius for the exponential disk (in arcseconds)
    :param inc: Inclination to project the disk (in degrees)
    :return: N/A
    """

    # Set up the cube parameters
    xsize = 128
    ysize = 128
    vsize = 1400
    cellsize = 1
    dv = 10
    beamsize = [4, 4, 0]
    posang = 90

    # Set up exponential disk SB profile/velocity
    x = np.arange(0, 100, 0.1)
    fx = np.exp(-x / scalerad)
    velfunc = interpolate.interp1d([0, 0.5, 1, 3, 500], [0, 50, 100, 210, 210], kind='linear')
    vel = velfunc(x)

    # Create the cube
    if jax:
        func=KinMS_jax
    else:
        func=KinMS
        
    instance=  func(xsize, ysize, vsize, cellsize, dv, beamsize, huge_beam=False)
    cube = instance.model_cube(inc, sbProf=fx, sbRad=x, velProf=vel, intFlux=30,
                 posAng=posang, gasSigma=10, toplot=toplot,fileName=fileName,ra=12,dec=10)    
    t=time.time()
    for i in range(0,5):
        cube = instance.model_cube(inc, sbProf=fx, sbRad=x, velProf=vel, intFlux=30,
                     posAng=posang, gasSigma=10, toplot=False,fileName=fileName,ra=12,dec=10)
    tout=(time.time()-t)/5.#print()
    # If you want to change something about the plots, or save them directly to your disk, you can use the plotting
    # script separately:
    #KinMS_plotter(cube, xsize, ysa.sum(axis=0).Tize, vsize, cellsize, dv, beamsize, posang=posang, savepath='.', savename='exp_disk',
    #              pdf=True).makeplots()
    
    return cube,tout

#expdisk(scalerad=10, inc=60,jax=True,toplot=True)
#expdisk(scalerad=10, inc=60,jax=False,toplot=True)
#expdisk(scalerad=5, inc=30,jax=True,toplot=True)
#expdisk(scalerad=15, inc=90,jax=True,toplot=True)

cube,toutj=expdisk(jax=True)
print("JAX",toutj)    
cube,tout=expdisk()    
print("Original",tout)  
print("Speedup",tout/toutj)

'''
import jax.numpy as jnp
import jax.scipy as jscipy
import numpy as np
import scipy
from astropy.convolution import convolve
psf=jnp.zeros((17,17))
psf=psf.at[7:9,7:9].set(0.5)
psf=psf.at[8,8].set(1)
im=jnp.zeros((128,128))
for i in range(0,10):
    im=im.at[np.random.choice(128),np.random.choice(128)].set(1)
out=jscipy.signal.convolve2d(im, psf)   
out2=scipy.signal.convolve2d(im, psf)   
out3=convolve(im,psf)

'''