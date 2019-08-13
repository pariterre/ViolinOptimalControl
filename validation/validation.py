import opensim as osim
import numpy as np
import biorbd
import pandas as pd
import matplotlib.pyplot as plt
from scipy import signal

# Load Biorbd model
model_path_biorbd = '../models/conv-arm26.bioMod'
model_biorbd = biorbd.s2mMusculoSkeletalModel(model_path_biorbd)

# Load data from opensim
data_excel = '../models/Opensim_model/validation-os.xlsx'
data = pd.read_excel(data_excel, sheet_name='utils')

time = list(data['time'])
nb_points = len(time)
freq_time = (nb_points-1)/(time[nb_points-1] - time[0])

# Create cut-off filter
freq_cut = 6
w = freq_cut / (freq_time/2)  # normalize the frequency
b, a = signal.butter(5, w, 'low')

# Create arrays for GenCoord
all_q = np.ndarray((model_biorbd.nbQ(), nb_points))
all_q_dot = np.ndarray((model_biorbd.nbQ(), nb_points-1))
all_q_ddot = np.ndarray((model_biorbd.nbQ(), nb_points-2))

q = [list(data['r_shoulder_elev']), list(data['r_elbow_flex'])]
q_dot = [[], []]
q_ddot = [[], []]

# Get q_dot
for i in range(len(time) - 1):
    q_dot[0].append((q[0][i + 1] - q[0][i]) / (time[i + 1] - time[i]))
    q_dot[1].append((q[1][i + 1] - q[1][i]) / (time[i + 1] - time[i]))

# Filter q_dot
q_dot_filtered = []
q_dot_filtered.append(signal.filtfilt(b, a, q_dot[0]))
q_dot_filtered.append(signal.filtfilt(b, a, q_dot[1]))

# Get q_ddot
for i in range(len(time) - 2):
    q_ddot[0].append((q_dot_filtered[0][i + 1] - q_dot_filtered[0][i]) / (time[i + 1] - time[i]))
    q_ddot[1].append((q_dot_filtered[1][i + 1] - q_dot_filtered[1][i]) / (time[i + 1] - time[i]))

# Filter q_ddot
q_ddot_filtered = []
q_ddot_filtered.append(signal.filtfilt(b, a, q_ddot[0]))
q_ddot_filtered.append(signal.filtfilt(b, a, q_ddot[1]))

# Gather values in array
for i in range(model_biorbd.nbQ()):
    all_q[i, :] = q[i][:]
    all_q_dot[i, :] = q_dot_filtered[i][:]
    all_q_ddot[i, :] = q_ddot_filtered[i][:]

# Get joint torque by inverse dynamics
tau_artic = np.ndarray((model_biorbd.nbQ(), nb_points-2))
for i in range(len(time)-2):
    tau = model_biorbd.InverseDynamics(all_q[:, i], all_q_dot[:, i], all_q_ddot[:, i]).get_array()
    tau_artic[0, i] = tau[0]
    tau_artic[1, i] = tau[1]

# Joint torque as long as Inverse Dyn does not work
r_shoulder_elev_moment = list(data['r_shoulder_elev_moment'])
r_elbow_flex_moment = list(data['r_elbow_flex_moment'])
tau_artic_input = np.ndarray((model_biorbd.nbQ(), nb_points-2))
for i in range(len(time)-2):
    tau_artic_input[0, i] = r_shoulder_elev_moment[i]
    tau_artic_input[1, i] = r_elbow_flex_moment[i]

# Initial muscle activations
# active_init = []
# for i in range(model_biorbd.nbMuscleTotal()):
#     active_init.append(biorbd.s2mMuscleStateActual(0, 0.1))
# print(active_init)

activation_from_os = np.ndarray((model_biorbd.nbMuscleTotal(), nb_points-2))
# Get muscle activations by static optimization
# for i in range(nb_points-2):
#     problem = biorbd.s2mStaticOptimization(model_biorbd, all_q[:, i], all_q_dot[:, i], tau_artic_input[:, i], active_init)
#     problem.run(True)
#     solution = problem.finalSolution().get_array()
#     for j in range(model_biorbd.nbMuscleTotal()):
#         activation_from_os[j, i] = solution[j]

# Get activations from Opensim
activation_tri_long = list(data['TRIlong'])
activation_tri_lat = list(data['TRIlat'])
activation_tri_med = list(data['TRImed'])
activation_bic_long = list(data['BIClong'])
activation_bic_short = list(data['BICshort'])
activation_bra = list(data['BRA'])

# Plot
plt.figure(1)
plt.subplot(4, 1, 1)
plt.plot(time, q[0], label='shoulder joint angle')
plt.plot(time, q[1], label='elbow joint angle')
plt.legend()

plt.subplot(4, 1, 2)
plt.plot(time[:-1], q_dot_filtered[0], label='shoulder joint angular velocity')
plt.plot(time[:-1], q_dot_filtered[1], label='elbow joint angular velocity')
plt.legend()

plt.subplot(4, 1, 3)
plt.plot(time[:-2], q_ddot_filtered[0], label='shoulder joint angular acceleration')
plt.plot(time[:-2], q_ddot_filtered[1], label='elbow joint angular acceleration')
plt.legend()

plt.subplot(4, 1, 4)
plt.plot(time[:], r_shoulder_elev_moment, label='shoulder joint torque')
plt.plot(time[:], r_elbow_flex_moment, label='elbow joint torque ')
plt.legend()

plt.figure(2)
plt.subplot(3, 2, 1)
plt.plot(time[:-2], activation_tri_long[:-2], label='Muscle activation of TRIlong from Opensim')
# plt.plot(time[:-2], activation_from_os[0, :], label='Muscle activation of TRIlong from biorbd')
plt.legend()

plt.subplot(3, 2, 2)
plt.plot(time[:-2], activation_tri_lat[:-2], label='Muscle activation of TRIlat from Opensim')
# plt.plot(time[:-2], activation_from_os[1, :], label='Muscle activation of TRIlat from biorbd')
plt.legend()

plt.subplot(3, 2, 3)
plt.plot(time[:-2], activation_tri_med[:-2], label='Muscle activation of TRImed from Opensim')
# plt.plot(time[:-2], activation_from_os[2, :], label='Muscle activation of TRImed from biorbd')
plt.legend()

plt.subplot(3, 2, 4)
plt.plot(time[:-2], activation_bic_long[:-2], label='Muscle activation of BIClong from Opensim')
# plt.plot(time[:-2], activation_from_os[3, :], label='Muscle activation of BIClong from biorbd')
plt.legend()

plt.subplot(3, 2, 5)
plt.plot(time[:-2], activation_bic_short[:-2], label='Muscle activation of BICshort from Opensim')
# plt.plot(time[:-2], activation_from_os[4, :], label='Muscle activation of BICshort from biorbd')
plt.legend()

plt.subplot(3, 2, 6)
plt.plot(time[:-2], activation_bra[:-2], label='Muscle activation of BRA from Opensim')
# plt.plot(time[:-2], activation_from_os[5, :], label='Muscle activation of BRA from biorbd')
plt.legend()


plt.show()
