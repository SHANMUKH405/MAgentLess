#!/usr/bin/env python3

import json
import subprocess
import os

def call_ollama(prompt, model="codellama:7b"):
    """Call Ollama API directly"""
    request_data = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "top_p": 0.9,
            "num_predict": 2048
        }
    }
    
    cmd = [
        "curl", "-s", "-X", "POST",
        "http://localhost:11434/api/generate",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(request_data)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    
    if result.returncode == 0:
        response = json.loads(result.stdout)
        return response.get("response", "")
    else:
        print(f"Error calling Ollama: {result.stderr}")
        return ""

def read_original_code():
    """Read the original.cpp file"""
    with open("repo/validation-dataset/benchmarks/benchmark_674/original.cpp", "r") as f:
        return f.read()

def extract_code_from_response(response):
    """Extract code from the LLM response"""
    if '```cpp' in response:
        start = response.find('```cpp') + 6
        end = response.find('```', start)
        if end != -1:
            return response[start:end].strip()
        else:
            return response[start:].strip()
    elif '```' in response:
        start = response.find('```') + 3
        end = response.find('```', start)
        if end != -1:
            return response[start:end].strip()
        else:
            return response[start:].strip()
    else:
        return response

def main():
    print("🔧 Generating agent_optimized.cpp using Ollama...")
    
    # Read the original code
    original_code = read_original_code()
    print(f"📖 Read original code ({len(original_code)} characters)")
    
    # Create the prompt
    prompt = f"""You are an expert C++ optimization engineer. Your task is to optimize the following C++ code for better performance using vectorization, OpenMP parallelism, and SIMD optimizations.

Original code:
```cpp
{original_code}
```

Please provide an optimized version that:
1. Maintains the same functionality and output
2. Uses OpenMP for parallelization where beneficial
3. Applies SIMD vectorization optimizations
4. Improves memory access patterns
5. Adds helpful comments explaining the optimizations

Return only the optimized C++ code, no explanations outside the code comments.
"""

    print("🤖 Calling Ollama API...")
    
    # Call Ollama
    response = call_ollama(prompt)
    
    if response:
        print(f"✅ Received response ({len(response)} characters)")
        
        # Extract the code
        optimized_code = extract_code_from_response(response)
        
        if optimized_code:
            # Write the optimized file
            output_path = "repo/validation-dataset/benchmarks/benchmark_674/agent_optimized.cpp"
            with open(output_path, "w") as f:
                f.write(optimized_code)
            
            print(f"✅ Created {output_path}")
            print(f"📝 Generated {len(optimized_code)} characters of optimized code")
            
            # Also copy to the other location
            other_path = "/Users/shannu405/Desktop/MAGENTLESS 4/validation-dataset/benchmarks/benchmark_674/agent_optimized.cpp"
            with open(other_path, "w") as f:
                f.write(optimized_code)
            print(f"✅ Also created {other_path}")
            
        else:
            print("❌ Could not extract code from response")
            print("Response:", response[:500] + "..." if len(response) > 500 else response)
    else:
        print("❌ Failed to get response from Ollama")

if __name__ == "__main__":
    main() 