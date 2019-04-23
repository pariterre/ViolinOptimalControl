"""
Example script for animating a model
"""

from pathlib import Path
import copy

import numpy as np
import scipy.integrate as integrate
import scipy.interpolate as interpolate

from pyomeca import Markers3d, RotoTrans, RotoTransCollection
from pyoviz.vtk import VtkModel, VtkWindow, Mesh, MeshCollection
import biorbd

import matplotlib.pyplot as plt

# Load the biorbd model
nFrame = 100
m = biorbd.s2mMusculoSkeletalModel("../models/Bras.pyoMod")
# all_Q = np.ones((1,100)) * np.linspace(0, np.pi/2, nFrame)
n_muscle = 18

##### State from the file

state_init = np.zeros((m.nbQ() + m.nbQdot()))

##### Controls from the file

# u = np.ones(n_muscle)*.5
u = np.ones(m.nbQddot())*5

#### integration

def dyn(t_int, X):
    # states_actual = biorbd.VecS2mMuscleStateActual(n_muscle)
    # for i in range(len(states_actual)):
    #     states_actual[i] = biorbd.s2mMuscleStateActual(0, u[i])
    # Tau = biorbd.s2mMusculoSkeletalModel.muscularJointTorque(m, states_actual, X[:m.nbQ()], X[m.nbQ():])

    QDDot = biorbd.s2mMusculoSkeletalModel.ForwardDynamics(m, X[:m.nbQ()], X[m.nbQ():], u).get_array()
    rsh = np.ndarray(m.nbQ() + m.nbQdot())
    for i in range(m.nbQ()):
        rsh[i] = X[m.nbQ()+i]
        rsh[i + m.nbQ()] = QDDot[i]

    return rsh


#### Interpolation
LI = integrate.solve_ivp(dyn, (0, .1), state_init)
Y = list()
Ydot = list()
time = LI.t
T = np.linspace(0, time[len(time)-1], nFrame)
for i in range(m.nbQ()):
    # Q
    tck = interpolate.splrep(time, LI.y[i, :], s=0)
    Y.append(interpolate.splev(T, tck, der=0))
    # Qdot
    tck = interpolate.splrep(time, LI.y[i+m.nbQ(), :], s=0)
    Ydot.append(interpolate.splev(T, tck, der=0))

###### visualisation

# plt.figure(1)
# for i in range(m.nbQ()):
#     plt.subplot(m.nbQ(), 2, 1+(2*i))
#     plt.plot(T, Y[i])
#     plt.title("états %i" %i)
#
#     plt.subplot(m.nbQ(), 2, 2+(2*i))
#     plt.plot(Ydot[i])
#     plt.title("états dérivés %i" %i)

# plt.figure(2)
# for j in range(m.nbTau()):
#     plt.subplot(m.nbTau(), 1, i+1)
#     plt.plot(u[i])
#     plt.title("contrôles %i" %j)
#
# plt.show()


# Path to data
nTags = m.nTags()
mark_tp = np.ndarray((3,  nTags, nFrame))
q_tp = np.ndarray((m.nbQ()))
for t in range(nFrame):
    for i in range(m.nbQ()):
        q_tp[i] = Y[i][t]*0
    Q = biorbd.s2mGenCoord(q_tp)
    markers_tp = m.Tags(m, Q)

    # Prepare markers
    for j in range(nTags):
        mark_tp[:, j, t] = markers_tp[j].get_array()
all_marks = Markers3d(mark_tp)

# Create a windows with a nice gray background
vtkWindow = VtkWindow(background_color=(.5, .5, .5))

# Add marker holders to the window
vtkModelReal = VtkModel(vtkWindow, markers_color=(1, 0, 0), markers_size=.005, markers_opacity=1)

# Animate all this
i = 0
while vtkWindow.is_active:
    # Update markers
    vtkModelReal.update_markers(all_marks.get_frame(i))

    # Update window
    vtkWindow.update_frame()
    i = (i + 1) % all_marks.get_num_frames()
