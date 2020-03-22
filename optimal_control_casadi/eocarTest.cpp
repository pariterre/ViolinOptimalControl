// C++ (and CasADi) from here on
#include <casadi/casadi.hpp>
#include "casadi/core/optistack.hpp"

int main(){
    // PREPARING THE PROBLEM
    double T(5.0);
    double mass(5);
    double g(-9.81);
    int N(30);
    int nx(2);
    int nu(1);
    double dt = T/static_cast<double>(N); // length of a control interval
    casadi::Opti opti;
    casadi::MX x(opti.variable(nx, N+1));
    casadi::MX u(opti.variable(nu, N));

    // OBJECTIVE FUNCTIONS
    casadi::MX obj(0);
    for (int j=0; j<nu; ++j){
        obj += casadi::MX::dot(u(j, casadi::Slice(0, N)), u(j, casadi::Slice(0, N))) * dt;
    }
    opti.minimize(obj);

    // DYNAMIC FUNCTION
    casadi::MX x_sym = casadi::MX::sym("x", nx, 1);
    casadi::MX u_sym = casadi::MX::sym("u", nu, 1);
    casadi::Function dyn = casadi::Function(
                "Dynamic",
                {x_sym, u_sym},
                {vertcat(
                    x_sym(casadi::Slice(static_cast<int>(nx/2), nx), 0),
                    u_sym / mass + g)
                });


    // CONSTRAINTS
    // Continuity constraints (rk4)
    std::vector<casadi::MX> var;
    var.push_back(casadi::MX(nx, 1));
    var.push_back(casadi::MX(nu, 1));

    // RK4
    for (int i=0; i<N; ++i){ // loop over control intervals
        var[1] = u(casadi::Slice(0, nu), i);

        // Runge-Kutta 4 integration
        var[0] = x(casadi::Slice(0, nx), i);
        casadi::MX k1 = dyn(var)[0];

        var[0] = x(casadi::Slice(0, nx), i)+dt/2*k1;
        casadi::MX k2 = dyn(var)[0];

        var[0] = x(casadi::Slice(0, nx), i)+dt/2*k2;
        casadi::MX k3 = dyn(var)[0];

        var[0] = x(casadi::Slice(0, nx), i)+dt  *k3;
        casadi::MX k4 = dyn(var)[0];

        casadi::MX x_next = x(casadi::Slice(0, nx), i) + dt/6 * (k1 + 2*k2 + 2*k3 + k4);

        opti.subject_to(x(casadi::Slice(0, nx), i+1)==x_next); // close the gaps
    }

    // Boundary conditions
    opti.subject_to(x(0, 0) == 0);
    opti.subject_to(x(1, 0) == 0);
    opti.subject_to(x(0, N) == 10);
    opti.subject_to(x(1, N) == 0);

    for (int i=0; i<N+1; ++i){
        opti.subject_to(x(casadi::Slice(0, nx), i) >= -500);
        opti.subject_to(x(casadi::Slice(0, nx), i) <=  500);
    }
    for (int i=0; i<N; ++i){
        opti.subject_to(u(casadi::Slice(0, nu), i) >= -100);
        opti.subject_to(u(casadi::Slice(0, nu), i) <=  100);
    }

    // INITIAL GUESS

    // SOLVING
    opti.solver("ipopt");
    casadi::OptiSol sol = opti.solve();

    // SHOWING THE RESULTS
    std::cout << sol.value(x) << std::endl << std::endl;
    std::cout << sol.value(u) << std::endl << std::endl;

    return 0;
}
