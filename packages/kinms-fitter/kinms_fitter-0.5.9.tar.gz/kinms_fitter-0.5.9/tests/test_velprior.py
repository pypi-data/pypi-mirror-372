import numpy as np
from kinms_fitter.velocity_profs import velocity_profs       
import matplotlib.pyplot as plt
from gastimator import gastimator
from kinms_fitter.prior_funcs import prior_funcs

class physical_velocity_prior:  
    def __init__(self,rads,vel_zero_index):
        self.rads=rads
        self.zero_index=vel_zero_index
          
    def eval(self,x,allvalues=[],ival=0):
        if ival==self.zero_index:
            return 1
        else:
            if ((allvalues[ival-1]**2*self.rads[ival-1]/self.rads[ival])<x**2):
                return 1
            else:
                return 1e-300



                    
def model(param,bincentroids,mymodel):  
    return velocity_profs.eval(mymodel,bincentroids,param)




bincentroids=np.arange(0,30,5)
data=200*np.arctan(bincentroids/2.)
data[3]=0

mymodel=list_vars=[velocity_profs.tilted_rings(bincentroids,guesses=[0,250,260,260,250,230],minimums=np.zeros(bincentroids.size),maximums=np.zeros(bincentroids.size)+500)]

initial_guesses= np.concatenate([i.guess for i in list_vars])
minimums=np.concatenate([i.min for i in list_vars])
maximums=np.concatenate([i.max for i in list_vars])
fixed=np.concatenate([i.fixed for i in list_vars])
priorss=np.concatenate([i.priors for i in list_vars])
precision=np.concatenate([i.precisions for i in list_vars])
labels=np.concatenate([i.labels for i in list_vars])              

priorss[:]=prior_funcs.physical_velocity_prior(bincentroids,0).eval


mcmc = gastimator(model,bincentroids,mymodel)

mcmc.labels=labels
mcmc.guesses=initial_guesses
mcmc.min=minimums
mcmc.max=maximums
mcmc.fixed=fixed
mcmc.prior_func=priorss
mcmc.precision= precision
#mcmc.nprocesses=1    
    
outputvalue, outputll= mcmc.run(data,30,10000,nchains=1,plot=False)        



plt.plot(bincentroids,data)
plt.errorbar(bincentroids,np.median(outputvalue,1),yerr=np.std(outputvalue,1),fmt='o')
plt.show()