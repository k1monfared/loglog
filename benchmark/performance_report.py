#!/usr/bin/env python3
"""
Performance Report Generator for LogLog GUI

Generates detailed performance reports from benchmark data with:
- Performance trends over time
- Regression detection  
- Performance impact analysis
- Recommendations for optimization
"""

import csv
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
import statistics

class PerformanceReporter:
    """Generate comprehensive performance reports from benchmark data"""
    
    def __init__(self):
        self.benchmark_dir = Path(__file__).parent
        self.results_file = self.benchmark_dir / "performance_results.csv"
        self.reports_dir = self.benchmark_dir / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        
    def load_data(self):
        """Load benchmark data from CSV"""
        if not self.results_file.exists():
            print("No benchmark data found. Run benchmark_runner.py first.")
            return None
        
        try:
            df = pd.read_csv(self.results_file)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        except Exception as e:
            print(f"Error loading data: {e}")
            return None
    
    def generate_trend_analysis(self, df):
        """Generate performance trend analysis"""
        print("\\n=== Performance Trend Analysis ===")
        
        # Group by test type and version
        trends = {}
        
        for test_type in df['test_type'].unique():
            if pd.isna(test_type):
                continue
                
            test_data = df[df['test_type'] == test_type]
            
            # Calculate average performance by version
            version_performance = test_data.groupby('version_id')['mean_time_ms'].mean()
            
            if len(version_performance) > 1:
                versions = list(version_performance.index)
                times = list(version_performance.values)
                
                # Calculate trend
                if len(times) >= 2:
                    latest_change = ((times[-1] - times[-2]) / times[-2]) * 100
                    overall_change = ((times[-1] - times[0]) / times[0]) * 100
                    
                    trends[test_type] = {
                        'latest_change_pct': latest_change,
                        'overall_change_pct': overall_change,
                        'versions': versions,
                        'times': times
                    }
                    
                    print(f"{test_type:20s}: Latest: {latest_change:+6.1f}%, Overall: {overall_change:+6.1f}%")
        
        return trends
    
    def detect_regressions(self, df, threshold=10.0):
        """Detect performance regressions (>threshold% slower)"""
        print(f"\\n=== Regression Detection (>{threshold}% threshold) ===")
        
        regressions = []
        
        for test_type in df['test_type'].unique():
            if pd.isna(test_type):
                continue
                
            test_data = df[df['test_type'] == test_type].sort_values('timestamp')
            
            if len(test_data) >= 2:
                recent_runs = test_data.tail(2)
                if len(recent_runs) == 2:
                    old_time = recent_runs.iloc[0]['mean_time_ms']
                    new_time = recent_runs.iloc[1]['mean_time_ms']
                    
                    if old_time and new_time:
                        change_pct = ((new_time - old_time) / old_time) * 100
                        
                        if change_pct > threshold:
                            regressions.append({
                                'test_type': test_type,
                                'old_version': recent_runs.iloc[0]['version_id'],
                                'new_version': recent_runs.iloc[1]['version_id'],
                                'old_time': old_time,
                                'new_time': new_time,
                                'change_pct': change_pct
                            })
                            
                            print(f"⚠️  REGRESSION: {test_type}")
                            print(f"   {recent_runs.iloc[0]['version_id']} → {recent_runs.iloc[1]['version_id']}")
                            print(f"   {old_time:.2f}ms → {new_time:.2f}ms ({change_pct:+.1f}%)")
        
        if not regressions:
            print("✅ No performance regressions detected!")
        
        return regressions
    
    def analyze_file_size_scaling(self, df):
        """Analyze how performance scales with file size"""
        print("\\n=== File Size Scaling Analysis ===")
        
        file_open_data = df[df['test_type'] == 'file_open'].dropna(subset=['line_count', 'mean_time_ms'])
        
        if len(file_open_data) > 3:
            # Group by file size and calculate average performance
            scaling_data = file_open_data.groupby('line_count').agg({
                'mean_time_ms': 'mean',
                'file_name': 'first'
            }).reset_index()
            
            print("File Size Performance Scaling:")
            for _, row in scaling_data.iterrows():
                lines_per_ms = row['line_count'] / row['mean_time_ms'] if row['mean_time_ms'] > 0 else 0
                print(f"  {row['file_name']:12s}: {row['line_count']:4.0f} lines in {row['mean_time_ms']:6.2f}ms ({lines_per_ms:.1f} lines/ms)")
        
        return scaling_data if 'scaling_data' in locals() else None
    
    def generate_recommendations(self, trends, regressions):
        """Generate optimization recommendations"""
        print("\\n=== Optimization Recommendations ===")
        
        recommendations = []
        
        # Check for consistent slow operations
        slow_operations = []
        for test_type, trend_data in trends.items():
            avg_time = statistics.mean(trend_data['times'])
            if avg_time > 100:  # Operations taking >100ms
                slow_operations.append((test_type, avg_time))
        
        if slow_operations:
            print("🐌 Slow Operations (>100ms average):")
            for op, avg_time in sorted(slow_operations, key=lambda x: x[1], reverse=True):
                print(f"   {op}: {avg_time:.2f}ms average")
                recommendations.append(f"Optimize {op} (currently {avg_time:.2f}ms average)")
        
        # Check for operations getting worse over time
        degrading_operations = []
        for test_type, trend_data in trends.items():
            if trend_data['overall_change_pct'] > 20:  # >20% slower over time
                degrading_operations.append((test_type, trend_data['overall_change_pct']))
        
        if degrading_operations:
            print("📈 Operations Getting Slower Over Time:")
            for op, change_pct in sorted(degrading_operations, key=lambda x: x[1], reverse=True):
                print(f"   {op}: {change_pct:+.1f}% slower overall")
                recommendations.append(f"Investigate {op} performance degradation ({change_pct:+.1f}%)")
        
        # Regression-specific recommendations
        if regressions:
            print("🔥 Recent Regression Fixes Needed:")
            for reg in regressions:
                print(f"   {reg['test_type']}: {reg['change_pct']:+.1f}% regression in {reg['new_version']}")
                recommendations.append(f"Fix {reg['test_type']} regression in {reg['new_version']}")
        
        if not (slow_operations or degrading_operations or regressions):
            print("✅ No major performance issues detected!")
            recommendations.append("Performance looks good! Consider micro-optimizations.")
        
        return recommendations
    
    def save_report(self, df, trends, regressions, recommendations):
        """Save detailed report to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.reports_dir / f"performance_report_{timestamp}.md"
        
        latest_version = df['version_id'].iloc[-1] if len(df) > 0 else "unknown"
        
        with open(report_file, 'w') as f:
            f.write(f"# LogLog GUI Performance Report\\n")
            f.write(f"**Generated:** {datetime.now()}\\n")
            f.write(f"**Version:** {latest_version}\\n\\n")
            
            # Summary stats
            f.write("## Summary Statistics\\n\\n")
            if len(df) > 0:
                f.write(f"- Total benchmark runs: {len(df['version_id'].unique())}\\n")
                f.write(f"- Test types covered: {len(df['test_type'].unique())}\\n")
                f.write(f"- Date range: {df['timestamp'].min()} to {df['timestamp'].max()}\\n\\n")
            
            # Performance trends
            f.write("## Performance Trends\\n\\n")
            for test_type, trend_data in trends.items():
                f.write(f"### {test_type}\\n")
                f.write(f"- Latest change: {trend_data['latest_change_pct']:+.1f}%\\n")
                f.write(f"- Overall change: {trend_data['overall_change_pct']:+.1f}%\\n")
                f.write(f"- Versions: {' → '.join(trend_data['versions'])}\\n\\n")
            
            # Regressions
            if regressions:
                f.write("## 🚨 Performance Regressions\\n\\n")
                for reg in regressions:
                    f.write(f"- **{reg['test_type']}**: {reg['old_time']:.2f}ms → {reg['new_time']:.2f}ms ")
                    f.write(f"({reg['change_pct']:+.1f}%) in {reg['new_version']}\\n")
                f.write("\\n")
            
            # Recommendations
            f.write("## 🎯 Recommendations\\n\\n")
            for i, rec in enumerate(recommendations, 1):
                f.write(f"{i}. {rec}\\n")
            
            f.write("\\n---\\n")
            f.write("*Report generated by LogLog Performance Monitoring System*\\n")
        
        print(f"\\n📄 Detailed report saved to: {report_file}")
        return report_file
    
    def generate_report(self):
        """Generate complete performance report"""
        print("🔍 Generating LogLog GUI Performance Report...")
        
        df = self.load_data()
        if df is None:
            return
        
        print(f"📊 Loaded {len(df)} benchmark records across {len(df['version_id'].unique())} versions")
        
        # Generate analysis
        trends = self.generate_trend_analysis(df)
        regressions = self.detect_regressions(df)
        scaling_data = self.analyze_file_size_scaling(df)
        recommendations = self.generate_recommendations(trends, regressions)
        
        # Save comprehensive report
        report_file = self.save_report(df, trends, regressions, recommendations)
        
        return {
            'trends': trends,
            'regressions': regressions,
            'scaling_data': scaling_data,
            'recommendations': recommendations,
            'report_file': report_file
        }

def main():
    """Generate performance report"""
    reporter = PerformanceReporter()
    reporter.generate_report()

if __name__ == "__main__":
    main()