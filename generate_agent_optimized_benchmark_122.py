#!/usr/bin/env python3

import requests
import json
import os
import sys

def call_ollama_api(prompt):
    """Call Ollama API to generate optimized code"""
    url = "http://localhost:11434/api/generate"
    
    data = {
        "model": "codellama:7b",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "top_p": 0.9,
            "max_tokens": 4000
        }
    }
    
    try:
        response = requests.post(url, json=data, timeout=120)
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

def main():
    # File paths
    original_file = "../validation-dataset/benchmarks/benchmark_122/original.cpp"
    output_file = "../validation-dataset/benchmarks/benchmark_122/agent_optimized.cpp"
    
    # Read original code
    original_code = read_file(original_file)
    if not original_code:
        print("❌ Failed to read original code")
        return
    
    print("📖 Original code loaded successfully")
    
    # Create optimization prompt
    prompt = f"""You are an expert C++ performance optimization specialist. Your task is to optimize the following C++ code for maximum performance using advanced techniques like:

1. **OpenMP Parallelization**: Use #pragma omp parallel for, #pragma omp simd
2. **SIMD Vectorization**: Explicit vectorization with compiler directives
3. **Loop Optimization**: Loop unrolling, cache-friendly access patterns
4. **Memory Access Optimization**: Optimize data layout and access patterns
5. **Compiler Optimizations**: Use appropriate compiler hints and directives

Here is the original code to optimize:

```cpp
{original_code}
```

Please provide an optimized version that:
- Maintains exact functional equivalence (same numerical output)
- Uses advanced performance optimization techniques
- Includes OpenMP parallelization where beneficial
- Optimizes memory access patterns
- Uses SIMD vectorization
- Includes comments explaining the optimizations

Return ONLY the optimized C++ code without any explanations or markdown formatting."""

    print("🤖 Calling Ollama API for optimization...")
    
    # Call Ollama API
    response = call_ollama_api(prompt)
    if not response:
        print("❌ Failed to get response from Ollama")
        return
    
    print("✅ Received response from Ollama")
    
    # Extract optimized code
    optimized_code = extract_code_from_response(response)
    if not optimized_code:
        print("❌ Failed to extract code from response")
        print("Response:", response)
        return
    
    print("📝 Extracted optimized code")
    
    # Write optimized code to file
    write_file(output_file, optimized_code)
    
    print(f"🎉 Successfully generated agent_optimized.cpp for benchmark_122")
    print(f"📁 Output file: {output_file}")

if __name__ == "__main__":
    main() 