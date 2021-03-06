from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
from math import sin, cos, pi, sqrt, log, pi, exp, log10
import math
import sys 
sys.path.append('..')
import mapOnRectangle as mor
from fwdProblem import *
from invProblem2d import *
from rectangle import *
from fenics import *
from measures import *

rect = Rectangle((0,0), (180,78), resol=6)
gamma = 0.001

N_obs = 1000

u_D = mor.mapOnRectangle(rect, "handle", lambda x, y: 0*x)

def boundary_D_boolean(x):
	if x[1] > 10**(-8):
		return True
	else:
		return False

f = mor.mapOnRectangle(rect, "handle", lambda x, y: (((x-40)**2 + (y-20)**2) < 4)*(-.01))

fwd = linEllipt2dRectangle(rect, f, u_D, boundary_D_boolean)
prior1 = GaussianFourier2d(rect, np.zeros((7,7)), 1.0, 3.0)
prior2 = GeneralizedGaussianWavelet2d(rect, 1.0, 1.0, 3)

invProb1 = inverseProblem(fwd, prior1, gamma)
invProb2 = inverseProblem(fwd, prior2, gamma)


obspos = [np.random.uniform(0, 180, N_obs), np.random.uniform(0, 78, N_obs)]

invProb1.obspos = obspos
invProb2.obspos = obspos

uTruth1 = prior1.sample()
uTruth2 = prior2.sample()

uTruth1 = uTruth1 * (1.0/np.max(np.abs(uTruth1.values)))
uTruth2 = uTruth2 * (1.0/np.max(np.abs(uTruth2.values)))


uTruth = uTruth1 + uTruth2


kTruth = mor.mapOnRectangle(invProb1.rect, "handle", lambda x,y: np.exp(uTruth.handle(x,y)))

sol = invProb1.Ffnc(uTruth)


obs = invProb1.Gfnc(uTruth) + np.random.normal(0, gamma, (N_obs,))

prior = GeneralizedGaussianWavelet2d(rect, 0.01, 1.0, 5)
invProb = inverseProblem(fwd, prior, gamma)
invProb.obs = obs
invProb.obspos = obspos

invProb1.obs = obs
invProb2.obs = obs
invProb1.plotSolAndLogPermeability(uTruth, obs=obs)

u01 = mor.mapOnRectangle(rect, "fourier", prior1._mean)
u02 = mor.mapOnRectangle(rect, "wavelet", prior._mean)

u_new, u_new_mean, us = invProb.EnKF(obs, 256, KL=False)
vals_new = np.array([invProb.I(uu, obs) for uu in u_new])
vals = np.array([invProb.I(uu, obs) for uu in us])
invProb.plotSolAndLogPermeability(u_new_mean)
#plt.figure();plt.subplot(2,1,1);plt.hist(vals,50);plt.subplot(2,1,2);plt.hist(vals_new,50)
#uOpt1 = invProb1.find_uMAP(u01, 400000, 400000)
#uOpt = invProb.find_uMAP(u02, 4000, 4000)

"""# now cross-checking: try to fit gaussians to wavelets and vice versa
obs1 = invProb1.Gfnc(uTruth2) + np.random.normal(0, gamma, (N_obs,))
obs2 = invProb2.Gfnc(uTruth1) + np.random.normal(0, gamma, (N_obs,))
invProb11 = inverseProblem(fwd, prior1, gamma, obs=obs2, obspos=obspos)
invProb22 = inverseProblem(fwd, prior2, gamma, obs=obs1, obspos=obspos)
uOpt11 = invProb11.find_uMAP(u01)
uOpt22 = invProb11.find_uMAP(u02)"""

