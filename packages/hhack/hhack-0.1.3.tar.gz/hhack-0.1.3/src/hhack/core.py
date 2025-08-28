"""Core benchmarking logic for Harmony LLM Benchmark."""

import importlib
import json
import concurrent.futures
from typing import List, Dict, Any, Optional, Tuple
import matplotlib.pyplot as plt
from .config import BenchmarkConfig, ModelMode
from .llm_handlers import get_llm_handler


class HarmonyBenchmark:
    """Main benchmarking class."""
    
    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.llm_handler = get_llm_handler(config)
        self.dataset = []
        self.results = {}
    
    def load_dataset(self, dataset: Optional[List[Dict[str, Any]]] = None ):
        """
        Load benchmark dataset.
        
        Args:
            dataset: List of dicts with 'original' and 'transformed_analysis' keys,
             If None, the dataset is loaded from a 'dataset.py' file.
        """
        if dataset is None:
            try:
                from dataset import dataset as dt
                dataset = dt
            except ImportError:
                raise RuntimeError("No dataset provided and 'dataset.py' could not be imported.")        
        required_keys = ['original', 'transformed_analysis']
        for i, item in enumerate(dataset):
            for key in required_keys:
                if key not in item:
                    raise ValueError(f"Dataset item {i} missing required key: {key}")
        
        self.dataset = dataset
        print(f"✅ Loaded dataset with {len(dataset)} items")
    
    def harmony_hack_format(self, content: str) -> str:
        """
        Apply Harmony hack formatting to content.
        This is a placeholder - implement your specific formatting logic.
        """
        # Add your specific Harmony formatting logic here
        formatted = f"[HARMONY FORMATTED]\n{content}\n[END HARMONY]"
        return formatted
    
    def _process_content_batch(self, contents: List[Tuple[str, str]], description: str) -> int:
        """Process a batch of content with threading."""
        print(f"\n📊 Processing {description}...")
        answered_count = 0
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            futures = {
                executor.submit(self.llm_handler.ask_llm, content[0], content[1]): content 
                for content in contents
            }
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        answered_count += 1
                except Exception as e:
                    print(f"Error processing content: {e}")
        
        print(f"✅ {description} finished. Answered count: {answered_count}")
        return answered_count
    
    def run_benchmark(self) -> Dict[str, Any]:
        """Run the complete benchmark."""
        if not self.dataset:
            raise ValueError("No dataset loaded. Call load_dataset() first.")
        
        print("✨ Starting Harmony hack processing... ✨")
        print(f"🔧 Mode: {self.config.mode.value}")
        print(f"🧵 Max workers: {self.config.max_workers}")
        
        # Prepare content batches
        original_contents = [(item["original"], item["original"]) for item in self.dataset]
        harmony_original_contents = [
            (self.harmony_hack_format(item["original"]), item['original']) 
            for item in self.dataset
        ]
        transformed_contents = [
            (item["transformed_analysis"], item["transformed_analysis"]) 
            for item in self.dataset
        ]
        harmony_transformed_contents = [
            (self.harmony_hack_format(item["transformed_analysis"]), item['original']) 
            for item in self.dataset
        ]
        
        # Process each batch
        answered_original_count = self._process_content_batch(
            original_contents, "original contents"
        )
        
        harmony_original_count = self._process_content_batch(
            harmony_original_contents, "harmony-formatted original contents"
        )
        
        answered_transformed_count = self._process_content_batch(
            transformed_contents, "transformed contents"
        )
        
        answered_hack_harmony_count = self._process_content_batch(
            harmony_transformed_contents, "harmony-formatted transformed contents"
        )
        
        # Calculate results
        total_questions = len(self.dataset)
        
        self.results = {
            'total_questions': total_questions,
            'answered_original_count': answered_original_count,
            'harmony_original_count': harmony_original_count,
            'answered_transformed_count': answered_transformed_count,
            'answered_hack_harmony_count': answered_hack_harmony_count,
            'percent_answered_original': (answered_original_count / total_questions) * 100 if total_questions > 0 else 0,
            'percent_harmony_original': (harmony_original_count / total_questions) * 100 if total_questions > 0 else 0,
            'percent_answered_transformed': (answered_transformed_count / total_questions) * 100 if total_questions > 0 else 0,
            'percent_answered_hack_harmony': (answered_hack_harmony_count / total_questions) * 100 if total_questions > 0 else 0,
            'config': self.config.to_dict()
        }
        
        self._print_results()
        
        if self.config.show_plots:
            self._plot_comparison_graph()
        
        if self.config.save_results:
            self._save_results()
        
        return self.results
    
    def _print_results(self):
        """Print benchmark results summary."""
        r = self.results
        
        print("\n" + "="*50)
        print("📈 BENCHMARK RESULTS SUMMARY")
        print("="*50)
        print(f"Total Questions: {r['total_questions']}")
        print(f"Original Questions Answered: {r['answered_original_count']} ({r['percent_answered_original']:.2f}%)")
        print(f"Original + Harmony Answered: {r['harmony_original_count']} ({r['percent_harmony_original']:.2f}%)")
        print(f"Analysis Questions Answered: {r['answered_transformed_count']} ({r['percent_answered_transformed']:.2f}%)")
        print(f"Analysis + Harmony Answered: {r['answered_hack_harmony_count']} ({r['percent_answered_hack_harmony']:.2f}%)")
        print("="*50)
    
    def _plot_comparison_graph(self):
        """Create and display comparison graph."""
        try:
            r = self.results
            categories = ['Original', 'Original +\nHarmony', 'Analysis', 'Analysis +\nHarmony']
            percentages = [
                r['percent_answered_original'],
                r['percent_harmony_original'],
                r['percent_answered_transformed'],
                r['percent_answered_hack_harmony']
            ]
            
            plt.figure(figsize=(12, 6))
            bars = plt.bar(categories, percentages, color=['#3498db', '#2ecc71', '#e74c3c', '#f39c12'])
            
            plt.title('LLM Response Rates by Content Type', fontsize=16, fontweight='bold')
            plt.ylabel('Response Rate (%)', fontsize=12)
            plt.xlabel('Content Type', fontsize=12)
            plt.ylim(0, 100)
            
            # Add percentage labels on bars
            for bar, pct in zip(bars, percentages):
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{pct:.1f}%', ha='center', va='bottom', fontweight='bold')
            
            plt.grid(axis='y', alpha=0.3)
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            print(f"Failed to generate plot: {e}")
    
    def _save_results(self):
        """Save results to JSON file."""
        try:
            with open(self.config.results_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"📁 Results saved to: {self.config.results_file}")
        except Exception as e:
            print(f"Failed to save results: {e}")
    
    def get_results(self) -> Dict[str, Any]:
        """Get the latest benchmark results."""
        return self.results