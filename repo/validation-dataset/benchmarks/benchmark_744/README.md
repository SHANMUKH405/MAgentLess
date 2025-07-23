# Benchmark 744: Embree parallel_sort vectorization

This benchmark is based on [Embree](https://github.com/embree/embree) commit `1148cb7`
which added `#pragma simd` directives to several loops inside `parallel_sort.h` to
force vectorization under the Intel compiler. The original loops zeroed arrays and
accumulated bucket counts without explicit vectorization hints. The patch added
`#pragma simd` before those loops to improve performance.

The simplified benchmark models the same pattern with a radix sort pass operating
on `BUCKETS` counters. The original version disables automatic vectorization so
that the loops execute scalar code. The optimized version uses `#pragma omp simd`
to mimic the added `#pragma simd` and enables vectorization.


The harness builds each version as a separate executable. Both expose the function
`run_sort(volatile unsigned int* src, unsigned int* dst, size_t N)`.  The harness
initializes a random input array and repeatedly calls this function.  Use
`--size` and `--repeat` to adjust the workload; the defaults (5000 elements and
450000 iterations) ensure the original version runs for more than ten seconds.
