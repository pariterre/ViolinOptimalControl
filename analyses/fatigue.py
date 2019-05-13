from pyoviz.BiorbdViz import BiorbdViz

import numpy as np

import biorbd

import scipy.integrate as integrate

import scipy.interpolate as interpolate

import matplotlib.pyplot as plt


### Muscle parameters ###

## Slow fibers ##

S_Percent = 0.50 # percent of slow fibers in muscle
S_Specific_Tension = 1.0
F_S = 0.01 # fatigue rate
R_S = 0.002 # recovery rate
LD_S = 10 # development factor
LR_S = 10 # recovery factor

## Fast Fatigue Resistant fibers ##

FR_Percent = 0.25
FR_Specific_Tension = 2.0
F_FR = 0.05
R_FR = 0.01
LD_FR = 10
LR_FR = 10

## Fast Fatigable fibers ##

FF_Percent = 0.25
FF_Specific_Tension = 3.0
F_FF = 0.1
R_FF = 0.02
LD_FF = 10
LR_FF = 10

### Load ###

TL = 60 # percent of Maximal Voluntary Contraction
t_Max = 1000

### Initial States ###

state_init_S0 = (0, 100, 0)
state_init_FR0 = (0, 100, 0)
state_init_FF0 = (0, 100, 0)
state_init_activation0 = (1, 0, 0)
state_init_0 = (0, 100, 0, 0, 100, 0, 0, 100, 0, 1, 0, 0)

def defdyn(R, F, LD, LR, ma, mr, mf, activ, T, percent):
    if ma < T:
        if mr > T - ma:
            c = LD * (T - ma)
        else:
            c = LD * mr
    else:
        c = LR * (T - ma)
    c = percent*c

    madot = c*activ - F * ma
    mrdot = -c*activ + R * mf
    mfdot = F * ma - R * mf

    return madot, mrdot, mfdot


def dyn(t, X):
    [ma_S, mr_S, mf_S, ma_FR, mr_FR, mf_FR, ma_FF, mr_FF, mf_FF, activ_S, activ_FR, activ_FF] = X

    # Residual capacity
    rc_S = S_Percent * (ma_S + mr_S)
    rc_FR = FR_Percent * (ma_FR)
    rc_FF = FF_Percent * (ma_FF)

    # Recruitment order
    activ_S = 1
    if TL > rc_S:
        activ_FR = 1
        if TL > rc_S + rc_FR:
            activ_FF = 1
        else:
            activ_FF = 0
    else:
        activ_FR = 0


    (madot_S, mrdot_S, mfdot_S) = defdyn(R_S, F_S, LD_S, LR_S, ma_S, mr_S, mf_S, activ_S, TL/S_Percent, S_Percent)
    (madot_FR, mrdot_FR, mfdot_FR) = defdyn(R_FR, F_FR, LD_FR, LR_FR, ma_FR, mr_FR, mf_FR, activ_FR, (TL-S_Percent*ma_S)/FR_Percent, FR_Percent)
    (madot_FF, mrdot_FF, mfdot_FF) = defdyn(R_FF, F_FF, LD_FF, LR_FF, ma_FF, mr_FF, mf_FF, activ_FF, (TL-S_Percent*ma_S - FR_Percent*ma_FR)/FF_Percent, FF_Percent)

    return madot_S, mrdot_S, mfdot_S, madot_FR, mrdot_FR, mfdot_FR, madot_FF, mrdot_FF, mfdot_FF, activ_S, activ_FR, activ_FF


X = integrate.solve_ivp(dyn, (0, t_Max), state_init_0)
t = X.t
X_S = (X.y[0, :], X.y[1, :], X.y[2, :])
X_FR = (X.y[3, :], X.y[4, :], X.y[5, :])
X_FF = (X.y[6, :], X.y[7, :], X.y[8, :])
activation =(X.y[9, :], X.y[10, :], X.y[11, :])

## Brain effort
BE_S = TL/(X.y[0,:] + X.y[1,:])
for i in range(len(BE_S)) :
    if BE_S[i] >= 1:
        BE_S[i] = 1

BE_FR = TL/(X.y[3,:] + X.y[4,:])
for i in range(len(BE_FR)) :
    if BE_FR[i] >= 1:
        BE_FR[i] = 1

BE_FF = TL/(X.y[6,:] + X.y[7,:])
for i in range(len(BE_FF)) :
    if BE_FF[i] >= 1:
        BE_FF[i] = 1

## Total activity
ma_total = S_Percent*X.y[0, :] + FR_Percent*X.y[3, :] + FF_Percent*X.y[6, :]

## Endurance Time
timing_endurance = list()
for i in range(len(ma_total)):
    if abs((ma_total[i] - TL)/TL) < 0.05:
        timing_endurance.append(t[i])
endur_Time = max(timing_endurance) - min(timing_endurance)
print('ET =', endur_Time)

### Plot Activation
plt.figure(1)

plt.subplot(3, 1, 1)
plt.plot(t, X_S[0], label = 'Activated')
plt.plot(t, X_S[1], label = 'Resting')
plt.plot(t, X_S[2], label = 'Fatigued')
plt.title("Slow fibers")
plt.xlabel('time')
plt.ylabel('%MVC')

plt.subplot(3, 1, 2)
plt.plot(t, X_FR[0], label = 'Activated')
plt.plot(t, X_FR[1], label = 'Resting')
plt.plot(t, X_FR[2], label = 'Fatigued')
plt.title("Fast Fatigue Resistant fibers")
plt.xlabel('time')
plt.ylabel('%MVC')

plt.subplot(3, 1, 3)
plt.plot(t, X_FF[0], label = 'Activated')
plt.plot(t, X_FF[1], label = 'Resting')
plt.plot(t, X_FF[2], label = 'Fatigued')
plt.title("Fast Fatigable fibers")
plt.xlabel('time')
plt.ylabel('%MVC')

plt.legend()

plt.figure(2)

plt.plot(t, ma_total)
plt.xlabel('time')
plt.ylabel('%MVC')

plt.figure(3)

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

plt.show()