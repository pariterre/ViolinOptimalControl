
import numpy as np

import biorbd

import scipy.integrate as integrate

import scipy.interpolate as interpolate

import matplotlib.pyplot as plt


# Muscle parameters

# Slow fibers
S_Percent = 0.50  # percent of slow fibers in muscle
S_Specific_Tension = 1.0  # each muscle fiber type can develop its own unit force
fatigue_rate_s = 0.01  # fatigue rate
recovery_rate_s = 0.002  # recovery rate
develop_factor_s = 10  # development factor
recover_factor_s = 10  # recovery factor

# Fast Fatigue Resistant fibers
FR_Percent = 0.25
FR_Specific_Tension = 2.0
fatigue_rate_ffr = 0.05
recovery_rate_ffr = 0.01
develop_factor_ffr = 10
recover_factor_ffr = 10

# Fast Fatigable fibers ##
FF_Percent = 0.25
FF_Specific_Tension = 3.0
fatigue_rate_ff = 0.1
recovery_rate_ff = 0.02
develop_factor_ff = 10
recover_factor_ff = 10

# Target Load
target_load = 99  # percent of Maximal Voluntary Contraction
t_Max = 100

# Initial States
state_init_s0 = (0, 100, 0)  # ma, mr, mf
state_init_ffr0 = (0, 100, 0)
state_init_ff0 = (0, 100, 0)
state_init_activation0 = (1, 0, 0)
state_init_0 = (0, 100, 0, 0, 100, 0, 0, 100, 0, 1, 0, 0)


def fatigue(load):

    def dyn(t, x):
        [ma_s, mr_s, mf_s, ma_ffr, mr_ffr, mf_ffr, ma_ff, mr_ff, mf_ff, activ_s, activ_ffr, activ_ff] = x

        # Residual capacity
        recover_cap_s = S_Percent * S_Specific_Tension * (ma_s + mr_s)
        recover_cap_ffr = FR_Percent * FR_Specific_Tension * (ma_ffr + mr_ffr)
        # recover_cap_ff = FF_Percent * FF_Specific_Tension * ma_ff

        # Recruitment order
        activ_s = 1
        if load > recover_cap_s:
            activ_ffr = 1
            if load > recover_cap_s + recover_cap_ffr:
                activ_ff = 1
            else:
                activ_ff = 0
        else:
            activ_ffr = 0

        # Conditions of evolution
        def defdyn(recover_rate, fatigue_rate, develop_factor, recovery_factor, ma, mr, mf, activ, _load, percent, tension):
            if ma < _load:
                if mr > _load - ma:
                    c = develop_factor * (_load - ma)  # development & not fatigued
                else:
                    c = develop_factor * mr  # development & fatigued
            else:
                c = recovery_factor * (_load - ma)  # recovery
            c = percent * tension * c

            ma_dot = c * activ - fatigue_rate * ma
            mr_dot = -c * activ + recover_rate * mf
            mf_dot = fatigue_rate * ma - recover_rate * mf

            return ma_dot, mr_dot, mf_dot

        (madot_s, mrdot_s, mfdot_s) = defdyn(recovery_rate_s, fatigue_rate_s, develop_factor_s,
                                             recover_factor_s, ma_s, mr_s, mf_s, activ_s,
                                             load/(S_Percent*S_Specific_Tension), S_Percent, S_Specific_Tension)
        (madot_ffr, mrdot_ffr, mfdot_ffr) = defdyn(recovery_rate_ffr, fatigue_rate_ffr, develop_factor_ffr,
                                            recover_factor_ffr, ma_ffr, mr_ffr, mf_ffr, activ_ffr,
                                            (load - S_Percent*S_Specific_Tension*ma_s)/(FR_Percent*FR_Specific_Tension),
                                                   FR_Percent, FR_Specific_Tension)
        (madot_ff, mrdot_ff, mfdot_ff) = defdyn(recovery_rate_ff, fatigue_rate_ff, develop_factor_ff,
                                                recover_factor_ff, ma_ff, mr_ff, mf_ff, activ_ff,
                                                (load - S_Percent*S_Specific_Tension*ma_s - FR_Percent*FR_Specific_Tension*ma_ffr)/(FF_Percent*FF_Specific_Tension), FF_Percent,FF_Specific_Tension)

        return madot_s, mrdot_s, mfdot_s, madot_ffr, mrdot_ffr, mfdot_ffr, madot_ff, mrdot_ff, mfdot_ff,\
               activ_s, activ_ffr, activ_ff
    return dyn


X = integrate.solve_ivp(fatigue(target_load), (0, t_Max), state_init_0)
t = X.t
X_S = (X.y[0, :], X.y[1, :], X.y[2, :])
X_FR = (X.y[3, :], X.y[4, :], X.y[5, :])
X_FF = (X.y[6, :], X.y[7, :], X.y[8, :])
activation =(X.y[9, :], X.y[10, :], X.y[11, :])

# Brain effort
BE_S = target_load/(X.y[0, :] + X.y[1, :])
for i in range(len(BE_S)):
    if BE_S[i] >= 1:
        BE_S[i] = 1

BE_FR = target_load/(X.y[3, :] + X.y[4, :])
for i in range(len(BE_FR)):
    if BE_FR[i] >= 1:
        BE_FR[i] = 1

BE_FF = target_load/(X.y[6, :] + X.y[7, :])
for i in range(len(BE_FF)):
    if BE_FF[i] >= 1:
        BE_FF[i] = 1

# Total activity
ma_total = S_Percent * S_Specific_Tension * X.y[0, :]\
           + FR_Percent * FR_Specific_Tension * X.y[3, :]\
           + FF_Percent * FF_Specific_Tension * X.y[6, :]

def find_endur_time(_load, _t_max, state_init):
    x = integrate.solve_ivp(fatigue(_load), (0, _t_max), state_init)
    _t = x.t

    ma_t = S_Percent * x.y[0, :] + FR_Percent * x.y[3, :] + FF_Percent * x.y[6, :]

    _endur_time = 0
    for i in range(len(ma_t)):
        if abs((ma_t[i] - _load) / _load) < 0.05:
            _endur_time = _t[i]

    return _endur_time


#list_target_load = np.linspace(1, 100, 50)
#endur_time = np.ndarray(len(list_target_load))
#for i in range(len(list_target_load)):
#    endur_time[i] = find_endur_time(list_target_load[i], 1000, state_init_0)
#    print(endur_time[i])

# Plot
plt.figure(1)

plt.subplot(4, 1, 1)
plt.plot(t, X_S[0]*S_Percent, label='Force developed by active')
plt.plot(t, X_S[1]*S_Percent, label='Potential force from resting')
plt.plot(t, X_S[2]*S_Percent, label='Force lost from fatigue')
plt.title("Slow fibers")
plt.xlabel('time')
plt.ylabel('%MVC')

plt.subplot(4, 1, 2)
plt.plot(t, X_FR[0]*FR_Percent, label='Force developed by active')
plt.plot(t, X_FR[1]*FR_Percent, label='Potential force from resting')
plt.plot(t, X_FR[2]*FR_Percent, label='Force lost from fatigue')
plt.title("Fast Fatigue Resistant fibers")
plt.xlabel('time')
plt.ylabel('%MVC')

plt.subplot(4, 1, 3)
plt.plot(t, X_FF[0]*FF_Percent, label='Force developed by active')
plt.plot(t, X_FF[1]*FF_Percent, label='Potential force from resting')
plt.plot(t, X_FF[2]*FF_Percent, label='Force lost from fatigue')
plt.title("Fast Fatigable fibers")
plt.xlabel('time')
plt.ylabel('%MVC')
plt.legend(bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0)

plt.subplot(4, 1, 4)
plt.plot(t, ma_total)
plt.plot([0.0, 100.0], [target_load, target_load], 'r-', lw=0.5)  # Red straight line
plt.plot([0, 100], [0.95*target_load, 0.95*target_load], 'r--', lw=0.5)  # Red dashed straight line
plt.plot([0, 100], [1.05*target_load, 1.05*target_load], 'r--', lw=0.5)  # Red dashed straight line
plt.xlabel('time')
plt.ylabel('%MVC')


plt.figure(2)

plt.subplot(3, 1, 1)
plt.plot(t, BE_S)
plt.title("Slow fibers")
plt.xlabel('time')
plt.ylabel('Brain effort')

plt.subplot(3, 1, 2)
plt.plot(t, BE_FR)
plt.title("Fast Fatigue Resistant fibers")
plt.xlabel('time')
plt.ylabel('Brain effort')

plt.subplot(3, 1, 3)
plt.plot(t, BE_FF)
plt.title("Fast Fatigable fibers")
plt.xlabel('time')
plt.ylabel('Brain effort')


#plt.figure(3)

#plt.plot(list_target_load, endur_time)
#plt.title("Endurance Time")
#plt.xlabel('Target Load (%MVC)')
#plt.ylabel('Time')

plt.show()



