#include <vector>
#include <cstddef>
#include <random>

constexpr size_t BUCKETS = 256;
constexpr size_t THREADS = 8;

void radix_iter0(volatile unsigned int* src, unsigned int* radixCount,
                 size_t N, size_t shift, size_t threadIndex) {
    size_t startID = threadIndex * N / THREADS;
    size_t endID = (threadIndex + 1) * N / THREADS;
    const unsigned int mask = BUCKETS - 1;
    for (size_t i = 0; i < BUCKETS; ++i)
        radixCount[threadIndex * BUCKETS + i] = 0;
    for (size_t i = startID; i < endID; ++i) {
        unsigned int index = (src[i] >> shift) & mask;
        radixCount[threadIndex * BUCKETS + index]++;
    }
}

void radix_iter1(volatile unsigned int* src, unsigned int* dst, unsigned int* radixCount,
                 size_t N, size_t shift, size_t threadIndex, size_t threadCount) {
    size_t startID = threadIndex * N / threadCount;
    size_t endID = (threadIndex + 1) * N / threadCount;
    const unsigned int mask = BUCKETS - 1;

    alignas(64) unsigned int total[BUCKETS];
#pragma omp simd
    for (size_t i = 0; i < BUCKETS; ++i)
        total[i] = 0;
    for (size_t i = 0; i < threadCount; ++i) {
#pragma omp simd
        for (size_t j = 0; j < BUCKETS; ++j)
            total[j] += radixCount[i * BUCKETS + j];
    }

    alignas(64) unsigned int offset[BUCKETS];
    offset[0] = 0;
    for (size_t i = 1; i < BUCKETS; ++i)
        offset[i] = offset[i - 1] + total[i - 1];

    for (size_t i = 0; i < threadIndex; ++i) {
#pragma omp simd
        for (size_t j = 0; j < BUCKETS; ++j)
            offset[j] += radixCount[i * BUCKETS + j];
    }

    for (size_t i = startID; i < endID; ++i) {
        unsigned int elt = src[i];
        unsigned int index = (elt >> shift) & mask;
        dst[offset[index]++] = elt;
    }
}

void run_sort(volatile unsigned int* src, unsigned int* dst, size_t N) {
    std::vector<unsigned int> counts(THREADS * BUCKETS);
    for (size_t t = 0; t < THREADS; ++t)
        radix_iter0(src, counts.data(), N, 0, t);
    for (size_t t = 0; t < THREADS; ++t)
        radix_iter1(src, dst, counts.data(), N, 0, t, THREADS);
}