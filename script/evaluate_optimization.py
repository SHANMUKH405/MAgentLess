#!/usr/bin/env python3
"""
Script to evaluate the quality of agent-generated optimizations
"""

import json
import difflib
import re
from pathlib import Path

def evaluate_optimization(original_file: str, expected_file: str, agent_file: str) -> dict:
    """
    Evaluate the quality of an agent-generated optimization
    """
    with open(original_file, 'r') as f:
        original = f.read()
    
    with open(expected_file, 'r') as f:
        expected = f.read()
    
    with open(agent_file, 'r') as f:
        agent = f.read()
    
    # Check if agent output matches expected optimization
    expected_optimization = extract_optimization_diff(original, expected)
    agent_optimization = extract_optimization_diff(original, agent)
    
    # Calculate similarity
    similarity = calculate_similarity(expected_optimization, agent_optimization)
    
    # Check for specific patterns
    has_eval = '.eval()' in agent
    preserves_logic = check_logic_preservation(original, agent)
    
    return {
        'similarity_score': similarity,
        'has_eval_optimization': has_eval,
        'preserves_mathematical_logic': preserves_logic,
        'expected_optimization': expected_optimization,
        'agent_optimization': agent_optimization
    }

def extract_optimization_diff(original: str, optimized: str) -> str:
    """Extract the key differences between original and optimized code"""
    diff = difflib.unified_diff(
        original.splitlines(keepends=True),
        optimized.splitlines(keepends=True),
        lineterm=''
    )
    return ''.join(diff)

def calculate_similarity(expected: str, actual: str) -> float:
    """Calculate similarity between expected and actual optimizations"""
    if not expected or not actual:
        return 0.0
    
    # Use difflib to calculate similarity
    matcher = difflib.SequenceMatcher(None, expected, actual)
    return matcher.ratio()

def check_logic_preservation(original: str, optimized: str) -> bool:
    """Check if the mathematical logic is preserved"""
    # Simple heuristic: check if key mathematical operations are present
    math_ops = ['exp()', 'log()', 'sum(', 'maximum(', 'reshape(', 'broadcast(']
    
    original_ops = sum(1 for op in math_ops if op in original)
    optimized_ops = sum(1 for op in math_ops if op in optimized)
    
    # Allow some variation but not major changes
    return abs(original_ops - optimized_ops) <= 2

def main():
    """Main evaluation function"""
    benchmark_dir = Path("../validation-dataset/benchmarks/benchmark_001")
    
    original_file = benchmark_dir / "original.cpp"
    expected_file = benchmark_dir / "optimized.cpp"
    agent_file = benchmark_dir / "agent_optimized.cpp"
    
    if not all(f.exists() for f in [original_file, expected_file, agent_file]):
        print("❌ Missing required files for evaluation")
        return
    
    results = evaluate_optimization(
        str(original_file),
        str(expected_file), 
        str(agent_file)
    )
    
    print("🔍 Optimization Quality Evaluation")
    print("=" * 50)
    print(f"Similarity Score: {results['similarity_score']:.2f}")
    print(f"Has .eval() Optimization: {'✅' if results['has_eval_optimization'] else '❌'}")
    print(f"Preserves Mathematical Logic: {'✅' if results['preserves_mathematical_logic'] else '❌'}")
    
    if results['similarity_score'] > 0.7:
        print("🎉 Good optimization quality!")
    elif results['similarity_score'] > 0.4:
        print("⚠️  Moderate optimization quality")
    else:
        print("❌ Poor optimization quality")
    
    return results

if __name__ == "__main__":
    main() 