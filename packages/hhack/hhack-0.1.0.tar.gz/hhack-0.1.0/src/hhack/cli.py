"""Command line interface for Harmony Benchmark."""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

from .core import HarmonyBenchmark
from .config import BenchmarkConfig, ModelMode


def load_dataset_from_file(file_path: str) -> List[Dict[str, Any]]:
    """Load dataset from JSON file."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            raise ValueError("Dataset file must contain a JSON array")
        
        return data
    except FileNotFoundError:
        print(f"❌ Dataset file not found: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in dataset file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        sys.exit(1)


def create_config_from_args(args) -> BenchmarkConfig:
    """Create BenchmarkConfig from command line arguments."""
    config_dict = {}
    
    # Mode selection
    if args.mode:
        config_dict['mode'] = ModelMode(args.mode)
    
    # API settings
    if args.api_key:
        config_dict['api_key'] = args.api_key
    if args.api_model:
        config_dict['api_model'] = args.api_model
    if args.api_base_url:
        config_dict['api_base_url'] = args.api_base_url
    
    # Local Transformers settings
    if args.local_model:
        config_dict['local_model_name'] = args.local_model
    if args.device:
        config_dict['device'] = args.device
    if args.max_length:
        config_dict['max_length'] = args.max_length
    
    # Ollama settings
    if args.ollama_model:
        config_dict['ollama_model'] = args.ollama_model
    if args.ollama_host:
        config_dict['ollama_host'] = args.ollama_host
    if args.ollama_port:
        config_dict['ollama_port'] = args.ollama_port
    
    # General settings
    if args.max_workers:
        config_dict['max_workers'] = args.max_workers
    if args.no_plot:
        config_dict['show_plots'] = False
    if args.no_save:
        config_dict['save_results'] = False
    if args.results_file:
        config_dict['results_file'] = args.results_file
    
    return BenchmarkConfig(**config_dict)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Harmony LLM Benchmark - Evaluate LLM responses with different content formats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # API mode with OpenAI
  harmony-benchmark data.json --mode api --api-key sk-xxx --api-model gpt-3.5-turbo
  
  # Local Transformers mode
  harmony-benchmark data.json --mode local_transformers --local-model microsoft/DialoGPT-medium
  
  # Local Ollama mode
  harmony-benchmark data.json --mode local_ollama --ollama-model llama2
  
Installation modes:
  # API only (lightweight)
  uv add harmony-llm-benchmark
  
  # With Transformers support
  uv add 'harmony-llm-benchmark[local]'
  
  # With Ollama support
  uv add 'harmony-llm-benchmark[ollama]'
  
  # With all local options
  uv add 'harmony-llm-benchmark[full-local]'
        """
    )
    
    # Required arguments
    parser.add_argument('dataset', help='Path to JSON dataset file')
    
    # Mode selection
    parser.add_argument(
        '--mode', 
        choices=['api', 'local_transformers', 'local_ollama'],
        default='api',
        help='LLM execution mode (default: api)'
    )
    
    # API settings
    api_group = parser.add_argument_group('API Settings')
    api_group.add_argument('--api-key', help='API key for the service')
    api_group.add_argument('--api-model', default='gpt-3.5-turbo', help='API model name')
    api_group.add_argument('--api-base-url', help='Custom API base URL')
    
    # Local Transformers settings
    local_group = parser.add_argument_group('Local Transformers Settings')
    local_group.add_argument('--local-model', help='Hugging Face model name')
    local_group.add_argument('--device', choices=['auto', 'cpu', 'cuda'], help='Device to run model on')
    local_group.add_argument('--max-length', type=int, help='Maximum generation length')
    
    # Ollama settings
    ollama_group = parser.add_argument_group('Ollama Settings')
    ollama_group.add_argument('--ollama-model', help='Ollama model name')
    ollama_group.add_argument('--ollama-host', default='localhost', help='Ollama host')
    ollama_group.add_argument('--ollama-port', type=int, default=11434, help='Ollama port')
    
    # General settings
    general_group = parser.add_argument_group('General Settings')
    general_group.add_argument('--max-workers', type=int, help='Maximum number of worker threads')
    general_group.add_argument('--no-plot', action='store_true', help='Disable result plots')
    general_group.add_argument('--no-save', action='store_true', help='Disable saving results to file')
    general_group.add_argument('--results-file', help='Custom results file name')
    
    # Parse arguments
    args = parser.parse_args()
    
    try:
        # Load dataset
        print(f"📂 Loading dataset from: {args.dataset}")
        dataset = load_dataset_from_file(args.dataset)
        
        # Create configuration
        config = create_config_from_args(args)
        
        # Run benchmark
        benchmark = HarmonyBenchmark(config)
        benchmark.load_dataset(dataset)
        results = benchmark.run_benchmark()
        
        print("\n🎉 Benchmark completed successfully!")
        
    except KeyboardInterrupt:
        print("\n❌ Benchmark interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()