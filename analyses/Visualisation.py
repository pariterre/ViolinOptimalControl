from pyoviz.BiorbdViz import BiorbdViz

import numpy as np

import biorbd

import scipy.integrate as integrate

import scipy.interpolate as interpolate

import matplotlib.pyplot as plt

##### Load the model
m = biorbd.s2mMusculoSkeletalModel("/home/lim/Programmation/ViolinOptimalControl/models/testconversion0.biomod")
bio = BiorbdViz(loaded_model = m, show_meshes=False)

bio.exec() # so visualisation window doesnt shut off