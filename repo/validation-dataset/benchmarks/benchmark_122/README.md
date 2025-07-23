# Benchmark 122: OpenMP parallelization of nodal gradient calculation

This benchmark originates from [commit 81b78ed](https://github.com/OPM/opm-common/commit/81b78edb6bdcb5d2a7eeea99d7a413d4206b2b21) which parallelized a heavy loop computing nodal gradients by using OpenMP. The original implementation iterated over all nodes sequentially while for each node accumulating contributions from neighbouring elements. The patch added `#pragma omp parallel for schedule(dynamic)` to distribute the work across threads.

The simplified benchmark mimics this behaviour with a small hexahedral mesh. The `original` version processes nodes sequentially while the `optimized` version parallelizes the outer loop using OpenMP. The workload is chosen so that the sequential version runs for several seconds, revealing the performance benefit of the parallel loop.
