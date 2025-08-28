"""
Example usage of Harmony LLM Benchmark package.

This example shows how to use the package programmatically.
"""

from hhack import HarmonyBenchmark, BenchmarkConfig, ModelMode

# Sample dataset

def example_api_mode():
    """Example using API mode (requires API key)."""
    print("=== API Mode Example ===")

    token  = 'OPEN ROUTER TOKEN'
    
    config = BenchmarkConfig(
        mode=ModelMode.API,
        api_key=token,
        api_model="openai/gpt-oss-20b",
        api_base_url="https://openrouter.ai/api/v1/chat/completions",
        max_workers=5,
        show_plots=True
    )
    
    benchmark = HarmonyBenchmark(config)
    benchmark.load_dataset()
    results = benchmark.run_benchmark()
    
    return results


def example_transformers_mode():
    """Example using local Transformers mode."""
    print("=== Local Transformers Mode Example ===")
    
    config = BenchmarkConfig(
        mode=ModelMode.LOCAL_TRANSFORMERS,
        local_model_name="microsoft/DialoGPT-small",  # Smaller model for demo
        device="auto",
        max_length=256,
        max_workers=2,  # Lower for local processing
        show_plots=True
    )
    
    benchmark = HarmonyBenchmark(config)
    benchmark.load_dataset()
    results = benchmark.run_benchmark()
    
    return results


def example_ollama_mode():
    """Example using local Ollama mode."""
    print("=== Local Ollama Mode Example ===")
    
    config = BenchmarkConfig(
        mode=ModelMode.LOCAL_OLLAMA,
        ollama_model="llama2:7b",
        ollama_host="localhost",
        ollama_port=11434,
        max_workers=3,
        show_plots=True
    )
    
    benchmark = HarmonyBenchmark(config)
    benchmark.load_dataset()
    results = benchmark.run_benchmark()
    
    return results


def main():
    """Run examples based on available dependencies."""
    
    print("Harmony Format LLM Benchmark Examples\n")
    
    try:
        # API mode (always available)
        print("Note: Set your API key in the code to run API mode example")
        results = example_api_mode()
        # Transformers mode (requires local dependencies)
        print("\nTrying Transformers mode...")
        try:
            results = example_transformers_mode()
            print("✅ Transformers mode completed successfully!")
        except ImportError:
            print("❌ Transformers mode not available. Install with:")
            print("   uv add 'harmony-llm-benchmark[local]'")
        
    
        print("\nTrying Ollama mode...")
        try:
            results = example_ollama_mode()
            print("✅ Ollama mode completed successfully!")
        except ImportError:
            print("❌ Ollama mode not available. Install with:")
            print("   uv add 'harmony-llm-benchmark[ollama]'")
        except RuntimeError as e:
            print(f"❌ Ollama mode failed: {e}")
            print("   Make sure Ollama is running and the model is available")
    
    except Exception as e:
        print(f"❌ Example failed: {e}")


if __name__ == "__main__":
    main()