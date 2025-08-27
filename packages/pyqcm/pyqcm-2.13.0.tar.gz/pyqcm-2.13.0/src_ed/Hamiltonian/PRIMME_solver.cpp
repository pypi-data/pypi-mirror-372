/*
Interface to use PRIMME eigensolver for ground state calculation
*/

#ifdef WITH_PRIMME 

#include "primme.h"
#include "PRIMME_solver.hpp"
#include "types.hpp"

template<>
int call_primme<double>(double* evals, double* evecs, double* rnorm, primme_params* primme) {
    return dprimme(evals, evecs, rnorm, primme);
}

template<>
int call_primme<Complex>(double* evals, Complex* evecs, double* rnorm, primme_params* primme) {
    return zprimme(evals, evecs, rnorm, primme);
}

#endif
