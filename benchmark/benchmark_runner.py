#!/usr/bin/env python3
"""
Comprehensive LogLog GUI Performance Benchmarking System

This benchmarks:
- File opening performance for various file sizes
- Tab switching performance with multiple tabs
- Folding/unfolding performance at different tree levels
- Memory usage during operations

Results are stored in CSV format with version tracking for regression analysis.
"""

import os
import sys
import time
import csv
import subprocess
import statistics
import gc
import psutil
import threading
from datetime import datetime
from pathlib import Path

# Add parent directory to Python path to import loglog modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from loglog_gui import ModernLogLogGUI, SystemTheme
from loglog_tree_model import LogLogTree

class PerformanceBenchmark:
    """Comprehensive performance benchmarking for LogLog GUI"""
    
    def __init__(self):
        self.benchmark_dir = Path(__file__).parent
        self.results_file = self.benchmark_dir / "performance_results.csv"
        self.test_files = [
            "small.log",      # ~10 items
            "medium.log",     # ~50 items  
            "large.log",      # ~200 items
            "xlarge.log",     # ~500 items
            "huge.log",       # ~1000 items
            "massive.log"     # ~2000 items
        ]
        self.version_id = self.get_version_id()
        self.process = psutil.Process()
        
    def get_version_id(self):
        """Get current git commit hash as version identifier"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--short', 'HEAD'], 
                capture_output=True, 
                text=True,
                cwd=self.benchmark_dir.parent
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        # Fallback to timestamp if git not available
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def measure_time(self, func, iterations=5):
        """Measure average execution time of a function over multiple iterations"""
        times = []
        
        for i in range(iterations):
            gc.collect()  # Clean up before measurement
            start_time = time.perf_counter()
            
            try:
                func()
            except Exception as e:
                print(f"Error in measurement iteration {i}: {e}")
                return None
            
            end_time = time.perf_counter()
            times.append((end_time - start_time) * 1000)  # Convert to milliseconds
            
            # Small delay between iterations
            time.sleep(0.1)
        
        return {
            'mean': statistics.mean(times),
            'median': statistics.median(times),
            'min': min(times),
            'max': max(times),
            'std': statistics.stdev(times) if len(times) > 1 else 0
        }
    
    def measure_memory_usage(self):
        """Get current memory usage in MB"""
        return self.process.memory_info().rss / 1024 / 1024
    
    def benchmark_file_opening(self):
        """Benchmark file opening performance for various file sizes"""
        print("\\n=== Benchmarking File Opening Performance ===")
        results = []
        
        for test_file in self.test_files:
            file_path = self.benchmark_dir / test_file
            if not file_path.exists():
                print(f"Warning: {test_file} not found, skipping...")
                continue
            
            print(f"Testing {test_file}...")
            
            def open_file_test():
                try:
                    # Create the actual GUI app as users would
                    app = ModernLogLogGUI()
                    app.root.withdraw()  # Hide for headless testing
                    
                    # Use the app's public API to load file (as users do)
                    app.load_file(str(file_path))
                    
                    # Ensure all GUI updates complete
                    app.root.update_idletasks()
                    
                    # Clean up
                    app.root.destroy()
                    
                except Exception as e:
                    print(f"Error in file opening test: {e}")
                    raise
            
            timing = self.measure_time(open_file_test, iterations=3)
            if timing:
                file_size = file_path.stat().st_size
                line_count = len(file_path.read_text().splitlines())
                
                results.append({
                    'test_type': 'file_open',
                    'file_name': test_file,
                    'file_size_bytes': file_size,
                    'line_count': line_count,
                    'mean_time_ms': timing['mean'],
                    'median_time_ms': timing['median'],
                    'min_time_ms': timing['min'],
                    'max_time_ms': timing['max'],
                    'std_time_ms': timing['std']
                })
                
                print(f"  {test_file}: {timing['mean']:.2f}ms (±{timing['std']:.2f}ms)")
        
        return results
    
    def benchmark_tab_switching(self):
        """Benchmark tab switching performance with multiple tabs"""
        print("\\n=== Benchmarking Tab Switching Performance ===")
        results = []
        
        for num_tabs in [2, 3, 5, 8]:
            print(f"Testing with {num_tabs} tabs...")
            
            def tab_switching_test():
                try:
                    # Create the actual GUI app
                    app = ModernLogLogGUI()
                    app.root.withdraw()  # Hide for headless testing
                    
                    # Load multiple files using app's public API (as users do)
                    test_files_subset = self.test_files[:num_tabs]
                    file_paths = []
                    
                    for test_file in test_files_subset:
                        file_path = self.benchmark_dir / test_file
                        if file_path.exists():
                            # Use the same method users use to open files
                            app.load_file(str(file_path))
                            file_paths.append(str(file_path))
                    
                    # Wait for all files to load
                    app.root.update_idletasks()
                    time.sleep(0.1)
                    
                    # Measure tab switching using the actual tab system
                    if len(file_paths) >= 2:
                        # Switch between tabs using the same method users use
                        for _ in range(3):
                            app.on_tab_select(file_paths[0])
                            app.root.update_idletasks()
                            app.on_tab_select(file_paths[1]) 
                            app.root.update_idletasks()
                    
                    # Clean up
                    app.root.destroy()
                    
                except Exception as e:
                    print(f"Error in tab switching test: {e}")
                    raise
            
            timing = self.measure_time(tab_switching_test, iterations=3)
            if timing:
                results.append({
                    'test_type': 'tab_switch',
                    'num_tabs': num_tabs,
                    'mean_time_ms': timing['mean'],
                    'median_time_ms': timing['median'],
                    'min_time_ms': timing['min'],
                    'max_time_ms': timing['max'],
                    'std_time_ms': timing['std']
                })
                
                print(f"  {num_tabs} tabs: {timing['mean']:.2f}ms (±{timing['std']:.2f}ms)")
        
        return results
    
    def benchmark_folding_operations(self):
        """Benchmark folding/unfolding performance at different tree levels"""
        print("\\n=== Benchmarking Folding/Unfolding Performance ===")
        results = []
        
        # Use medium-sized file for folding tests
        test_file = self.benchmark_dir / "large.log"
        if not test_file.exists():
            print("Warning: large.log not found, skipping folding tests...")
            return results
        
        for operation in ['fold', 'unfold']:
            for level in [1, 2, 3]:
                print(f"Testing {operation} at level {level}...")
                
                def folding_test():
                    try:
                        # Create the actual GUI app
                        app = ModernLogLogGUI()
                        app.root.withdraw()  # Hide for headless testing
                        
                        # Load file using the app's public API
                        app.load_file(str(test_file))
                        app.root.update_idletasks()
                        
                        # Perform folding operation using app's methods (as users do via keyboard shortcuts)
                        if operation == 'fold':
                            app.tree_renderer.fold_to_level(level)
                        else:  # unfold
                            app.tree_renderer.unfold_all()
                        
                        app.root.update_idletasks()
                        
                        # Clean up
                        app.root.destroy()
                        
                    except Exception as e:
                        print(f"Error in folding test: {e}")
                        raise
                
                timing = self.measure_time(folding_test, iterations=5)
                if timing:
                    results.append({
                        'test_type': f'{operation}_level',
                        'level': level,
                        'mean_time_ms': timing['mean'],
                        'median_time_ms': timing['median'],
                        'min_time_ms': timing['min'],
                        'max_time_ms': timing['max'],
                        'std_time_ms': timing['std']
                    })
                    
                    print(f"  {operation} level {level}: {timing['mean']:.2f}ms (±{timing['std']:.2f}ms)")
        
        return results
    
    def save_results(self, all_results):
        """Save benchmark results to CSV with version tracking"""
        fieldnames = [
            'timestamp', 'version_id', 'test_type', 'file_name', 'file_size_bytes', 
            'line_count', 'num_tabs', 'level', 'mean_time_ms', 'median_time_ms',
            'min_time_ms', 'max_time_ms', 'std_time_ms', 'memory_mb'
        ]
        
        file_exists = self.results_file.exists()
        current_memory = self.measure_memory_usage()
        timestamp = datetime.now().isoformat()
        
        with open(self.results_file, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            for result in all_results:
                # Add common fields to each result
                result.update({
                    'timestamp': timestamp,
                    'version_id': self.version_id,
                    'memory_mb': current_memory
                })
                
                # Fill in missing fields with None
                for field in fieldnames:
                    if field not in result:
                        result[field] = None
                
                writer.writerow(result)
        
        print(f"\\nResults saved to {self.results_file}")
        print(f"Version ID: {self.version_id}")
        print(f"Memory usage: {current_memory:.2f} MB")
    
    def compare_with_previous(self):
        """Compare current results with previous run"""
        if not self.results_file.exists():
            print("No previous results to compare with.")
            return
        
        print("\\n=== Performance Comparison ===")
        
        # Read all results
        with open(self.results_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            all_results = list(reader)
        
        if len(all_results) < 2:
            print("Need at least 2 benchmark runs to compare.")
            return
        
        # Group by version
        version_groups = {}
        for result in all_results:
            version = result['version_id']
            if version not in version_groups:
                version_groups[version] = []
            version_groups[version].append(result)
        
        versions = sorted(version_groups.keys())
        if len(versions) < 2:
            print("Need at least 2 different versions to compare.")
            return
        
        current_version = versions[-1]
        previous_version = versions[-2]
        
        print(f"Comparing {previous_version} → {current_version}")
        
        # Compare by test type
        test_types = set()
        for result in all_results:
            test_types.add(result['test_type'])
        
        for test_type in sorted(test_types):
            current_results = [r for r in version_groups[current_version] if r['test_type'] == test_type]
            previous_results = [r for r in version_groups[previous_version] if r['test_type'] == test_type]
            
            if current_results and previous_results:
                current_avg = statistics.mean([float(r['mean_time_ms']) for r in current_results if r['mean_time_ms']])
                previous_avg = statistics.mean([float(r['mean_time_ms']) for r in previous_results if r['mean_time_ms']])
                
                change_pct = ((current_avg - previous_avg) / previous_avg) * 100
                direction = "⬆️" if change_pct > 0 else "⬇️" if change_pct < 0 else "➡️"
                
                print(f"  {test_type:15s}: {previous_avg:6.2f}ms → {current_avg:6.2f}ms {direction} {change_pct:+5.1f}%")
    
    def run_full_benchmark(self):
        """Run the complete benchmark suite"""
        print(f"Running LogLog GUI Performance Benchmark")
        print(f"Version: {self.version_id}")
        print(f"Timestamp: {datetime.now()}")
        
        all_results = []
        
        # Run all benchmark categories
        all_results.extend(self.benchmark_file_opening())
        all_results.extend(self.benchmark_tab_switching())
        all_results.extend(self.benchmark_folding_operations())
        
        # Save results
        self.save_results(all_results)
        
        # Compare with previous results
        self.compare_with_previous()
        
        print("\\n=== Benchmark Complete ===")
        return all_results

def main():
    """Main benchmark execution"""
    # Generate test files if they don't exist
    benchmark_dir = Path(__file__).parent
    test_files = ["small.log", "medium.log", "large.log", "xlarge.log", "huge.log", "massive.log"]
    
    missing_files = [f for f in test_files if not (benchmark_dir / f).exists()]
    if missing_files:
        print(f"Generating missing test files: {missing_files}")
        from generate_test_files import create_test_files
        create_test_files()
    
    # Run benchmark
    benchmark = PerformanceBenchmark()
    benchmark.run_full_benchmark()

if __name__ == "__main__":
    main()