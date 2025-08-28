#!/usr/bin/env python3
# coding: utf-8
import numpy as np
from kinms_fitter import kinms_fitter
import matplotlib.pyplot as plt
from gastimator import corner_plot
from kinms_fitter.sb_profs import sb_profs
from kinms_fitter.velocity_profs import velocity_profs  
import matplotlib.pyplot as plt

cube = "PGCwholecube_spw3.image.fits"

'''
load in your cube, and trim it if needed
spatial trim in pixels [xmin, xmax, ymin, ymax], spectral trim in channels.
Can also tell it a good set of channels that are line-free with linefree_chans=[start,end]
'''
fv=kinms_fitter(cube,spatial_trim=[128+5,192+5,128-5,192-5],spectral_trim=[70,122]) 

# make guesses of the free parameters - if you dont it will try and guess them, but isnt especially clever about it
fv.pa_guess=330
#fv.vsys_guess=6696+50
fv.inc_guess=70
#fv.xc_guess=192.42611085940155-(0.5/3600.)  # ra in degrees
#fv.yc_guess=15.16563877    # dec in degrees
fv.expscale_guess=1.
fv.inc_guess=60.


# nrings is crucial - this is the number of beam size elements you have across your galaxy. Set this too large and it will do crazy things in the outer parts where it isnt constrained!
fv.nrings=5

fv.vel_profile=[velocity_profs.arctan(guesses=np.array([250,0.1]),minimums=np.array([50,0.01]),maximums=[410,10])]

# #control the boxcar prior for each parameter
# # self.xcent_range=[min,max] #in degrees 
# # self.ycent_range=[min,max] #in degrees
# # self.pa_range=[min,max] # in degrees

# # self.vel_range=[min,max] # allowed velocity for each beamsize annulus in km/s.
# #self.inc_range=[min,max] # in degrees.
# #self.totflux_range=[min,max] # in the units of your mom0
#

### if you are usign the default expdisk/tilted ring fitting combo then these control the limits...
# #self.expscale_range=[min,max] # in arcseconds
# # self.vsys_range=[min,max] # systemic velocity range in km/s

# # options - here commented out for basic use (all default to false)
fv.show_corner=False # set this to true to show the corner plots for your fitted parameters
#fv.silent=True      # set to "True" to rig the code for silent running
# #fv.pdf=True         # set to "True" to output PDFs of the end plots.

#print(fv.vsys_guess)
fv.niters=3000
fv.output_cube_fileroot = 'bugtest'
bestvals, besterrs, outputvalue, outputll,fixed = fv.run(method='both',justplot=False)

print((bestvals[0]),(bestvals[1]))   
print((bestvals[0]-192.42603179589437)*3600.,(bestvals[1]-26.891970500175667)*3600.)
#figure = corner_plot.corner_plot(outputvalue[~fixed,:].T,like=outputll,quantiles=[0.16, 0.5, 0.84],verbose=False)
# for a,b in zip(fv.labels,bestvals):
#     print(a,b)

wewantx=192.4260875
wewanty=26.892013850824988

plt.show()
