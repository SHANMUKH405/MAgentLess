#include <chrono>
#include <iostream>
#include <string>
#include <vector>
#include <random>

constexpr size_t BUCKETS = 256;
constexpr size_t THREADS = 8;

// The benchmark compiles either original.cpp or optimized.cpp.  Both provide
// the same function name so the harness doesn't need conditional linking.
void run_sort(volatile unsigned int* src, unsigned int* dst, size_t N);

int main(int argc, char* argv[]) {
    std::string mode = "perf";
    std::string impl = "original"; // kept for compatibility but unused
    size_t N = 5000;
    // Large repeat count ensures the original implementation runs >10s
    size_t repeat = 450000;

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--mode=correct") mode = "correct";
        else if (arg == "--mode=perf") mode = "perf";
        else if (arg.rfind("--impl=",0)==0) impl = arg.substr(8);
        else if (arg.rfind("--size=",0)==0) N = std::stoul(arg.substr(7));
        else if (arg.rfind("--repeat=",0)==0) repeat = std::stoul(arg.substr(9));
    }

    std::vector<unsigned int> dst(N);
    volatile unsigned int* src = new unsigned int[N];
    std::mt19937 rng(42);
    std::uniform_int_distribution<unsigned int> dist(0, UINT32_MAX);
    for (size_t i = 0; i < N; ++i) src[i] = dist(rng);

    if (mode == "correct") {
        run_sort(src, dst.data(), N);
        unsigned long long sum = 0;
        for (unsigned v : dst) sum += v;
        std::cout << sum << '\n';
    } else {
        using clock = std::chrono::high_resolution_clock;
        auto t1 = clock::now();
        for (size_t r = 0; r < repeat; ++r)
            run_sort(src, dst.data(), N);
        auto t2 = clock::now();
        std::cout << "Time: "
                  << std::chrono::duration_cast<std::chrono::milliseconds>(t2 - t1).count()
                  << " ms\n";
    }
    return 0;
}

