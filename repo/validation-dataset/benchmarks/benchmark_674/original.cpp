#include "athena_array.hpp"
#include <omp.h>

void PrimitiveToConserved(const AthenaArray<double>& prim, AthenaArray<double>& cons,
        int is, int ie, int js, int je, int ks, int ke, int nthreads) {
    double igm1 = 1.0 / (GAMMA - 1.0);
#pragma omp parallel default(shared) num_threads(nthreads)
    {
        for (int k = ks; k <= ke; ++k) {
#pragma omp for schedule(dynamic)
            for (int j = js; j <= je; ++j) {
#pragma simd
                for (int i = is; i <= ie; ++i) {
                    double w_d  = prim(IDN,k,j,i);
                    double w_vx = prim(IVX,k,j,i);
                    double w_vy = prim(IVY,k,j,i);
                    double w_vz = prim(IVZ,k,j,i);
                    double w_p  = prim(IEN,k,j,i);
                    cons(IDN,k,j,i) = w_d;
                    cons(IM1,k,j,i) = w_vx * w_d;
                    cons(IM2,k,j,i) = w_vy * w_d;
                    cons(IM3,k,j,i) = w_vz * w_d;
                    cons(IEN,k,j,i) = w_p * igm1 + 0.5 * w_d * (w_vx*w_vx + w_vy*w_vy + w_vz*w_vz);
                }
            }
        }
    }
}
