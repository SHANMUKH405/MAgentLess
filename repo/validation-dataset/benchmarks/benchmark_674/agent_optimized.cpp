#include "athena_array.hpp"
#include <omp.h>

void PrimitiveToConserved(const AthenaArray<double>& prim, AthenaArray<double>& cons,
        int is, int ie, int js, int je, int ks, int ke, int nthreads) {
    double igm1 = 1.0 / (GAMMA - 1.0);
    
    // Optimized version with better loop ordering and memory access patterns
    #pragma omp parallel default(shared) num_threads(nthreads)
    {
        // Loop over k first for better cache locality
        for (int k = ks; k <= ke; ++k) {
            #pragma omp for schedule(dynamic)
            for (int j = js; j <= je; ++j) {
                // Vectorized inner loop with better memory access pattern
                #pragma omp simd
                for (int i = is; i <= ie; ++i) {
                    // Load all primitive variables at once for better cache efficiency
                    double w_d  = prim(IDN,k,j,i);
                    double w_vx = prim(IVX,k,j,i);
                    double w_vy = prim(IVY,k,j,i);
                    double w_vz = prim(IVZ,k,j,i);
                    double w_p  = prim(IEN,k,j,i);
                    
                    // Compute conserved variables with optimized calculations
                    cons(IDN,k,j,i) = w_d;
                    cons(IM1,k,j,i) = w_vx * w_d;
                    cons(IM2,k,j,i) = w_vy * w_d;
                    cons(IM3,k,j,i) = w_vz * w_d;
                    
                    // Optimized energy calculation with reduced arithmetic operations
                    double ke = 0.5 * w_d * (w_vx*w_vx + w_vy*w_vy + w_vz*w_vz);
                    cons(IEN,k,j,i) = w_p * igm1 + ke;
                }
            }
        }
    }
}
