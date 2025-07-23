#!/usr/bin/env python3

import requests
import json
import os
import sys
import time

def call_ollama_api(prompt, model="codellama:7b", temperature=0.1, max_tokens=4000):
    """Call Ollama API with enhanced parameters"""
    url = "http://localhost:11434/api/generate"
    
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "top_p": 0.95,
            "top_k": 40,
            "repeat_penalty": 1.1,
            "max_tokens": max_tokens
        }
    }
    
    try:
        response = requests.post(url, json=data, timeout=180)
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        print(f"Error calling Ollama API: {e}")
        return None

def read_file(filepath):
    """Read file content"""
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return None

def write_file(filepath, content):
    """Write content to file"""
    try:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"✅ Successfully wrote: {filepath}")
    except Exception as e:
        print(f"Error writing file {filepath}: {e}")

def extract_code_from_response(response):
    """Extract C++ code from the LLM response"""
    # Look for code blocks
    if "```cpp" in response:
        start = response.find("```cpp") + 6
        end = response.find("```", start)
        if end != -1:
            return response[start:end].strip()
    
    # If no code blocks, try to extract from the response
    lines = response.split('\n')
    code_lines = []
    in_code = False
    
    for line in lines:
        if line.strip().startswith('#include') or line.strip().startswith('void') or line.strip().startswith('int') or line.strip().startswith('double'):
            in_code = True
        if in_code:
            code_lines.append(line)
    
    return '\n'.join(code_lines)

def create_enhanced_prompt(original_code, benchmark_name):
    """Create an enhanced optimization prompt"""
    
    prompt = f"""You are a world-class C++ performance optimization expert with 20+ years of experience in HPC, SIMD programming, and compiler optimization. Your task is to create a highly optimized version of the following C++ code.

**BENCHMARK**: {benchmark_name}

**ORIGINAL CODE**:
```cpp
{original_code}
```

**OPTIMIZATION REQUIREMENTS**:

1. **PERFORMANCE TARGET**: Achieve maximum possible speedup while maintaining exact numerical correctness
2. **HARDWARE TARGET**: Modern x86-64 with AVX2/AVX-512 support, multi-core CPU
3. **COMPILER**: GCC/Clang with -O3 optimization

**REQUIRED OPTIMIZATION TECHNIQUES**:

1. **OpenMP Parallelization**:
   - Use `#pragma omp parallel for` for loop parallelization
   - Use `#pragma omp simd` for SIMD vectorization
   - Use `#pragma omp parallel for reduction` for reductions
   - Set appropriate `num_threads()` and `schedule()` clauses

2. **SIMD Vectorization**:
   - Explicit vectorization with `#pragma omp simd`
   - Use `__restrict__` keywords for pointer aliasing
   - Align data structures for optimal memory access
   - Use vector intrinsics if beneficial

3. **Memory Access Optimization**:
   - Cache-friendly loop ordering (i,j,k vs k,j,i)
   - Minimize cache misses with proper data layout
   - Use blocking/tiling for large arrays
   - Optimize stride patterns

4. **Loop Optimization**:
   - Loop unrolling with `#pragma unroll`
   - Loop fusion where beneficial
   - Loop interchange for better cache locality
   - Strength reduction and induction variable optimization

5. **Compiler Hints**:
   - Use `__builtin_expect()` for branch prediction
   - Use `__attribute__((aligned))` for data alignment
   - Use `__attribute__((hot))` for hot functions
   - Use `__attribute__((noinline))` for small functions

6. **Advanced Techniques**:
   - Function inlining where beneficial
   - Constant propagation and folding
   - Dead code elimination
   - Register allocation optimization

**OUTPUT FORMAT**:
- Return ONLY the optimized C++ code
- Include detailed comments explaining each optimization
- Ensure exact functional equivalence
- Use modern C++17 features if beneficial

**EVALUATION CRITERIA**:
- Performance improvement (target: 2-10x speedup)
- Code maintainability
- Correctness verification
- Compiler compatibility

Generate the most aggressive, performance-optimized version possible:"""

    return prompt

def create_iterative_prompt(original_code, previous_attempt, benchmark_name, attempt_num):
    """Create an iterative improvement prompt"""
    
    prompt = f"""You are a C++ performance optimization expert. This is iteration {attempt_num} to improve the optimization.

**BENCHMARK**: {benchmark_name}

**ORIGINAL CODE**:
```cpp
{original_code}
```

**PREVIOUS OPTIMIZATION ATTEMPT**:
```cpp
{previous_attempt}
```

**ANALYSIS**: The previous attempt achieved some optimization but can be improved further. Focus on:

1. **More aggressive SIMD vectorization** - Use explicit vector intrinsics
2. **Better memory access patterns** - Optimize cache locality
3. **Advanced OpenMP techniques** - Use nested parallelism, task-based parallelism
4. **Loop transformations** - More aggressive unrolling, fusion, interchange
5. **Compiler-specific optimizations** - Target specific compiler features

**GOAL**: Create a significantly faster version than the previous attempt while maintaining correctness.

Return ONLY the improved optimized C++ code:"""

    return prompt

def main():
    # Configuration - Updated to use correct repo path
    benchmark_name = "benchmark_122"  # Change this for different benchmarks
    original_file = f"repo/validation-dataset/benchmarks/{benchmark_name}/original.cpp"
    output_file = f"repo/validation-dataset/benchmarks/{benchmark_name}/agent_optimized.cpp"
    
    # Model options (try different models)
    models = [
        "codellama:7b",           # Current model
        "codellama:13b",          # Larger model if available
        "codellama:34b",          # Even larger if available
        "llama3.2:3b",            # Alternative model
        "deepseek-coder:6.7b"     # Another code-focused model
    ]
    
    # Read original code
    original_code = read_file(original_file)
    if not original_code:
        print("❌ Failed to read original code")
        return
    
    print(f"📖 Original code loaded for {benchmark_name}")
    
    # Try different models and strategies
    best_result = None
    best_model = None
    
    for model in models:
        print(f"\n🤖 Trying model: {model}")
        
        # Strategy 1: Enhanced single-shot optimization
        prompt = create_enhanced_prompt(original_code, benchmark_name)
        
        print("🔄 Generating enhanced optimization...")
        response = call_ollama_api(prompt, model=model, temperature=0.05, max_tokens=6000)
        
        if response:
            optimized_code = extract_code_from_response(response)
            if optimized_code:
                print(f"✅ Generated optimization with {model}")
                best_result = optimized_code
                best_model = model
                break
        
        time.sleep(2)  # Rate limiting
    
    # If no result, try with default model
    if not best_result:
        print("🔄 Falling back to default model...")
        prompt = create_enhanced_prompt(original_code, benchmark_name)
        response = call_ollama_api(prompt, model="codellama:7b", temperature=0.1, max_tokens=4000)
        
        if response:
            best_result = extract_code_from_response(response)
            best_model = "codellama:7b"
    
    # Write the result
    if best_result:
        write_file(output_file, best_result)
        print(f"🎉 Successfully generated agent_optimized.cpp for {benchmark_name}")
        print(f"📁 Output file: {output_file}")
        print(f"🤖 Model used: {best_model}")
    else:
        print("❌ Failed to generate optimization")

if __name__ == "__main__":
    main() 