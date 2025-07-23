# Benchmark 674: outer-loop vectorization

This benchmark is based on [Athena++](https://github.com/PrincetonUniversity/athena-public-version) commit `e33f62e4` which modified the `PrimitiveToConserved` routine in the equation of state module. The change removes an OpenMP parallel region and instead applies `#pragma simd` on the outer loop while disabling vectorization of the innermost loop with `#pragma novector`.

The goal is to demonstrate how replacing OpenMP with explicit vectorization directives can impact performance.
