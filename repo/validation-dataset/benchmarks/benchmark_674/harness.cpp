#include "athena_array.hpp"
#include <chrono>
#include <iostream>
#include <random>
#include <string>
#include <omp.h>

void PrimitiveToConserved(const AthenaArray<double>& prim, AthenaArray<double>& cons,
        int is, int ie, int js, int je, int ks, int ke, int nthreads);

AthenaArray<double> make_array(int size) {
    AthenaArray<double> arr(NHYDRO, size, size, size);
    std::mt19937 gen(42);
    std::uniform_real_distribution<double> dist(0.0, 1.0);
    for (int n = 0; n < NHYDRO; ++n)
        for (int k = 0; k < size; ++k)
            for (int j = 0; j < size; ++j)
                for (int i = 0; i < size; ++i)
                    arr(n,k,j,i) = dist(gen);
    return arr;
}

int main(int argc, char* argv[]) {
    std::string mode = "perf";
    int size = 20;
    int repeat = 500000;
    int threads = std::min(4, omp_get_max_threads());

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--mode=correct") mode = "correct";
        else if (arg == "--mode=perf") mode = "perf";
        else if (arg.rfind("--size=",0) == 0) size = std::stoi(arg.substr(7));
        else if (arg.rfind("--repeat=",0) == 0) repeat = std::stoi(arg.substr(9));
        else if (arg.rfind("--threads=",0) == 0) threads = std::stoi(arg.substr(10));
    }

    AthenaArray<double> prim = make_array(size);
    AthenaArray<double> cons(NHYDRO, size, size, size);

    if (mode == "correct") {
        PrimitiveToConserved(prim, cons, 0, size-1, 0, size-1, 0, size-1, threads);
        double sum = 0.0;
        for (double v : cons.data) sum += v;
        std::cout << sum << '\n';
    } else {
        using clock = std::chrono::high_resolution_clock;
        auto t1 = clock::now();
        for (int r = 0; r < repeat; ++r)
            PrimitiveToConserved(prim, cons, 0, size-1, 0, size-1, 0, size-1, threads);
        auto t2 = clock::now();
        std::cout << "Time: "
                  << std::chrono::duration_cast<std::chrono::milliseconds>(t2 - t1).count()
                  << " ms\n";
    }
    return 0;
}
