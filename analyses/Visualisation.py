from pyoviz.BiorbdViz import BiorbdViz

import numpy as np

import biorbd

import scipy.integrate as integrate

import scipy.interpolate as interpolate

import matplotlib.pyplot as plt

##### Load the model
m = biorbd.s2mMusculoSkeletalModel("/home/lim/Programmation/ViolinOptimalControl/models/Bras.pyoMod")
bio = BiorbdViz(loaded_model = m)

bio.exec() # so visualisation window doesnt shut off