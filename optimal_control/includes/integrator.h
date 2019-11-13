#ifndef VIOLIN_OPTIMIZATION_INTEGRATOR_H
#define VIOLIN_OPTIMIZATION_INTEGRATOR_H
#include "RigidBody/Integrator.h"

namespace biorbd {
class Model;
namespace rigidbody {
class GeneralizedTorque;
}
}

class AcadoIntegrator : public biorbd::rigidbody::Integrator {
public:
    AcadoIntegrator(biorbd::Model &m);
    virtual void operator() (
            const state_type &x,
            state_type &dxdt,
            double t );

    void integrateKinematics(
            const biorbd::rigidbody::GeneralizedCoordinates& Q,
            const biorbd::rigidbody::GeneralizedCoordinates& QDot,
            const biorbd::rigidbody::GeneralizedTorque& GeneralizedTorque,
            double t0,
            double tend,
            double timeStep);
    void getIntegratedKinematics(
            unsigned int step,
            biorbd::rigidbody::GeneralizedCoordinates &Q,
            biorbd::rigidbody::GeneralizedCoordinates &QDot);
    unsigned int nbInterationStep() const;
    bool m_isKinematicsComputed;
};

#endif  // VIOLIN_OPTIMIZATION_INTEGRATOR_H
