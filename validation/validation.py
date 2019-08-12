import opensim as osim
import biorbd
import pandas as pd

# Biorbd
model_path_biorbd = '../models/conv-arm26.bioMod'
model_biorbd = biorbd.s2mMusculoSkeletalModel(model_path_biorbd)
data_excel = '../models/Opensim_model/validation-os.xlsx'

data = pd.read_excel(data_excel, sheet_name='arm26.mot')

time = list(data['time'])
q = [list(data['r_shoulder_elev']), list(data['r_elbow_flex'])]

q_dot = [[], []]
q_ddot = [[], []]

for i in range(len(time) - 1):
    q_dot[0].append((q[0][i + 1] - q[0][i]) / (time[i + 1] - time[i]))
    q_dot[1].append((q[1][i + 1] - q[1][i]) / (time[i + 1] - time[i]))

for i in range(len(time) - 2):
    q_ddot[0].append((q_dot[0][i + 1] - q_dot[0][i]) / (time[i + 1] - time[i]))
    q_ddot[1].append((q_dot[1][i + 1] - q_dot[1][i]) / (time[i + 1] - time[i]))
# TODO convert q, qdot in s2mGenCoord

tau_artic = [[], []]
for i in range(len(time)-2):
    #[tau_artic[0], tau_artic[1]] =
    print(model_biorbd.InverseDynamics(q[i], q_dot[i], q_ddot[i]))


