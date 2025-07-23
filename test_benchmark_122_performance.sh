#!/bin/bash

set -e

echo "🔍 Testing Performance for Benchmark 122"
echo "========================================"

BENCH_DIR="repo/validation-dataset/benchmarks/benchmark_122"
COMPILER="g++-15"
CXXFLAGS="-std=c++17 -O3 -fopenmp"

# Function to compile and test a version
test_version() {
    local version=$1
    local source_file=$2
    local output_name=$3
    
    echo "📦 Compiling $version version..."
    $COMPILER $CXXFLAGS -I. -o $output_name $source_file $BENCH_DIR/harness.cpp
    
    echo "⚡ Testing $version performance (10 runs)..."
    total_time=0
    for i in {1..10}; do
        time_ms=$(./$output_name --mode=perf --repeat=500000 --size=20 --threads=4 2>&1 | grep "Time:" | awk '{print $2}')
        echo "  Run $i: ${time_ms}ms"
        total_time=$(echo "$total_time + $time_ms" | bc)
    done
    
    avg_time=$(echo "scale=2; $total_time / 10" | bc)
    echo "📊 $version average time: ${avg_time}ms"
    echo ""
    
    # Clean up
    rm -f $output_name
}

# Test original version
test_version "Original" "$BENCH_DIR/original.cpp" "bench_original"

# Test human-optimized version
test_version "Human-Optimized" "$BENCH_DIR/optimized.cpp" "bench_human"

# Test agent-optimized version  
test_version "Agent-Optimized" "$BENCH_DIR/agent_optimized.cpp" "bench_agent"

echo "✅ Performance testing complete!" 