import opensim as osim
import biorbd

# Opensim
model_path_osim = '../models/Opensim_model/arm26.osim'
model_osim = osim.Model(model_path_osim)
model_osim.finalizeFromProperties()
state, actuators, muscle_actuators = [], [], []
actual_q, actual_qdot, actual_qddot = [], [], []
n_dof, n_actuators, n_muscles = [], [], []


# Biorbd
model_path_biorbd = '../models/convert-arm26.biomod'
model_biorbd = biorbd.s2mMusculoSkeletalModel(model_path_biorbd)


def forward_dynamics(model, x, n_times=0):
    # set residual forces
    fs = model.getForceSet()
    for i in range(n_muscles, fs.getSize()):
        coord = osim.CoordinateActuator.safeDownCast(fs.get(i))
        if coord:
            coord.setOverrideActuation(state, x[i] * x[i])

    # update muscles
    muscle_activation = x[: n_muscles]
    for m in range(n_muscles):
        muscle_actuators.get(m).setActivation(state, muscle_activation[m])
    try:
        model.equilibrateMuscles(state)
        model.realizeAcceleration(state)
        return state.getUDot()
    except RuntimeError:
        if n_times > 10:
            raise RuntimeError("equilibrateMuscles failed too much times")
        return forward_dynamics(x + 0.001, n_times + 1)
