# LogLog GUI Performance Benchmarking System

A comprehensive performance monitoring and regression detection system for LogLog GUI development.

## 🎯 Purpose

This benchmarking system tracks performance metrics across different versions to:
- **Detect regressions** before they reach production
- **Measure optimization impact** quantitatively  
- **Guide development priorities** based on performance data
- **Ensure scalability** as features are added

## 📊 What It Measures

### File Opening Performance
- Small files (~10 items)
- Medium files (~50 items)  
- Large files (~200 items)
- Extra large files (~500 items)
- Huge files (~1000 items)
- Massive files (~2000 items)

### Tab Switching Performance
- 2, 3, 5, and 8 tabs open simultaneously
- Switch time between different tabs
- Memory usage with multiple tabs

### Folding/Unfolding Operations
- Fold to level 1, 2, 3
- Unfold all operations
- Performance at different tree depths

## 🚀 Quick Start

### Run Benchmark
```bash
# Automatic mode (commits changes and runs benchmark)
./benchmark/run_benchmark.sh

# Manual mode (run benchmark without committing)
cd benchmark
python3 benchmark_runner.py
```

### Generate Performance Report
```bash
cd benchmark
python3 performance_report.py
```

### Generate Test Files
```bash
cd benchmark
python3 generate_test_files.py
```

## 📁 Files Structure

```
benchmark/
├── run_benchmark.sh           # Main benchmark runner script
├── benchmark_runner.py        # Core benchmarking engine
├── generate_test_files.py     # Creates test LogLog files
├── performance_report.py      # Generates analysis reports
├── performance_results.csv    # Historical performance data
├── reports/                   # Generated performance reports
├── small.log                  # Test file (~10 items)
├── medium.log                 # Test file (~50 items)
├── large.log                  # Test file (~200 items)
├── xlarge.log                 # Test file (~500 items)
├── huge.log                   # Test file (~1000 items)
├── massive.log                # Test file (~2000 items)
└── README.md                  # This file
```

## 📈 Understanding Results

### Performance CSV Format
```csv
timestamp,version_id,test_type,file_name,file_size_bytes,line_count,num_tabs,level,mean_time_ms,median_time_ms,min_time_ms,max_time_ms,std_time_ms,memory_mb
```

### Key Metrics
- **mean_time_ms**: Average execution time across multiple runs
- **std_time_ms**: Standard deviation (consistency indicator)
- **memory_mb**: Memory usage during operation
- **version_id**: Git commit hash for version tracking

### Test Types
- `file_open`: File opening performance
- `tab_switch`: Tab switching performance  
- `fold_level`: Folding operations
- `unfold_level`: Unfolding operations

## 🔍 Regression Detection

The system automatically detects performance regressions by:
1. Comparing latest run with previous run
2. Flagging >10% performance degradation
3. Tracking long-term performance trends
4. Generating actionable recommendations

### Example Output
```
=== Performance Comparison ===
Comparing abc123 → def456
  file_open      :  45.23ms →  52.18ms ⬆️  +15.4%  ⚠️ REGRESSION
  tab_switch     :  12.45ms →  11.32ms ⬇️   -9.1%  ✅ IMPROVED  
  fold_level     :  23.67ms →  18.91ms ⬇️  -20.1%  ✅ IMPROVED
```

## 🛠️ Development Workflow

### Before Making Changes
```bash
# Run baseline benchmark
./benchmark/run_benchmark.sh
```

### After Making Changes
```bash
# Run benchmark to measure impact
./benchmark/run_benchmark.sh

# Generate detailed report
cd benchmark && python3 performance_report.py
```

### Example Workflow
1. **Baseline**: Run benchmark before optimization
2. **Develop**: Implement viewport-based architecture  
3. **Measure**: Run benchmark after changes
4. **Analyze**: Check for improvements/regressions
5. **Document**: Note performance impact in commit message

## 📋 Integration with Git

The benchmark system integrates with Git for version tracking:
- Automatically commits uncommitted changes
- Uses commit hash as version identifier
- Tracks performance across development history
- Enables bisecting performance regressions

## 🎯 Performance Targets

### Current Benchmarks (Post-Viewport Architecture - Version 91bc2d8)

#### File Opening Performance
| File Size | Current Performance | Target | Status |
|-----------|-------------------|---------|---------|
| Small (10 items) | 96.94ms ±12.78 | <50ms | ⚠️ Needs optimization |
| Medium (50 items) | 190.08ms ±7.95 | <100ms | ⚠️ Needs optimization |
| Large (200 items) | 534.81ms ±52.61 | <200ms | ⚠️ Needs optimization |
| XLarge (500 items) | 1,326.27ms ±10.73 | <500ms | ⚠️ Needs optimization |
| Huge (1000 items) | 2,776.48ms ±45.18 | <1000ms | ⚠️ Needs optimization |
| Massive (2000 items) | 5,830.65ms ±6.86 | <2000ms | ⚠️ Needs optimization |

#### Tab Switching Performance
| Tab Count | Current Performance | Target | Status |
|-----------|-------------------|---------|---------|
| 2 tabs | 484.25ms ±60.90 | <50ms | ⚠️ Needs optimization |
| 3 tabs | 994.23ms ±21.62 | <100ms | ⚠️ Needs optimization |
| 5 tabs | 5,112.59ms ±36.01 | <200ms | ⚠️ Needs optimization |
| 8 tabs | 10,256.34ms ±887.04 | <500ms | ⚠️ Needs optimization |

#### Folding/Unfolding Performance
| Operation | Current Performance | Target | Status |
|-----------|-------------------|---------|---------|
| Fold Level 1-3 | ~485-495ms | <100ms | ⚠️ Needs optimization |
| Unfold Level 1-3 | ~433-508ms | <100ms | ⚠️ Needs optimization |

**Memory Usage**: 103.22 MB (Target: <100MB) ⚠️

### Architecture Status
- ✅ **Error-Free**: Eliminated `'TreeRenderer' object has no attribute 'node_widgets'` errors
- ✅ **Clean Architecture**: Viewport-based design implemented
- ⚠️ **Performance Regression**: Significant slowdown after architecture changes needs investigation
- 🔧 **Next Steps**: Optimize viewport rendering and caching mechanisms

### Regression Thresholds
- **Critical**: >50% performance degradation
- **Warning**: >10% performance degradation  
- **Acceptable**: <10% variation between runs

## 🔧 Customization

### Adding New Benchmarks
1. Add test function to `benchmark_runner.py`
2. Update `run_full_benchmark()` to include new test
3. Add analysis to `performance_report.py`

### Modifying Test Files
Edit `generate_test_files.py` to change:
- File sizes and complexity
- Content patterns
- Tree depth and structure

### Changing Thresholds
Update regression detection thresholds in:
- `detect_regressions()` function
- Performance targets in this README

## 📊 Sample Report Output

```
🔍 Generating LogLog GUI Performance Report...
📊 Loaded 45 benchmark records across 8 versions

=== Performance Trend Analysis ===
file_open           : Latest:   -23.4%, Overall:   -45.2%
tab_switch          : Latest:   -67.8%, Overall:   -89.1%  
fold_level          : Latest:   -12.3%, Overall:   -34.5%

=== Regression Detection (>10% threshold) ===
✅ No performance regressions detected!

=== Optimization Recommendations ===
✅ Performance looks good! Consider micro-optimizations.

📄 Detailed report saved to: reports/performance_report_20241201_143022.md
```

## 🤝 Contributing

When contributing performance-related changes:
1. **Always run benchmarks** before and after changes
2. **Include performance impact** in commit messages
3. **Investigate regressions** immediately
4. **Document optimization techniques** for future reference

### Commit Message Examples
```
✅ Good: "Implement viewport architecture - 89% faster tab switching"
✅ Good: "Optimize folding operations - 34% performance improvement"  
❌ Bad: "Fixed some performance issues"
```

---

*This benchmarking system helps maintain LogLog's performance standards as the codebase evolves.*