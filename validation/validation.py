import opensim

import static_optim.kinematic

import static_optim.dynamic_models

import biorbd

model_path_osim = '../models/Opensim_model/arm26.osim'
model_path_biorbd = '../models/convert-arm26.osim'
mot_path = 'results/result-arm26.mot'

mot = open(mot_path, 'w')
mot.write('Coordinates\n'
          'nRows=500\n'
          'nColumns=24\n'
          'endheader\n\n')
mot.write('time    dof1    dof2    dof3    ')



