# 🚀 **LRDBenchMark: Long-Range Dependence Benchmarking Toolkit**

A comprehensive Python package for benchmarking long-range dependence estimators on synthetic and real-world time series data. LRDBench provides ready-to-use implementations of classical, machine learning, and neural network estimators with built-in analytics and performance monitoring.

## 🎯 **What is LRDBench?**

LRDBench is designed for researchers, data scientists, and practitioners who need to:
- **Compare different long-range dependence estimation methods**
- **Generate synthetic data from stochastic processes**
- **Benchmark estimator performance across various data types**
- **Monitor usage patterns and performance metrics**
- **Use pre-trained models without additional training**

## ✨ **Key Features**

### **🔬 12 Built-in Estimators**
- **Temporal Methods**: DFA, DMA, Higuchi, R/S (4 estimators)
- **Spectral Methods**: Periodogram, Whittle, GPH (3 estimators)
- **Wavelet Methods**: CWT, Wavelet Variance, Wavelet Log Variance, Wavelet Whittle (4 estimators)
- **Multifractal Methods**: MFDFA (1 estimator)
- **🚀 Auto-Optimized**: All estimators with NUMBA/JAX performance optimizations

### **📊 5 Stochastic Data Models**
- **FBMModel**: Fractional Brownian Motion
- **FGNModel**: Fractional Gaussian Noise
- **ARFIMAModel**: AutoRegressive Fractionally Integrated Moving Average
- **MRWModel**: Multifractal Random Walk
- **Neural fSDE**: Neural network-based fractional SDEs

### **⚡ High Performance**
- **JAX Optimization**: GPU acceleration for large-scale computations
- **Numba JIT**: Just-in-time compilation for critical loops
- **Parallel Processing**: Multi-core benchmark execution
- **Memory Efficient**: Optimized data structures and algorithms

### **🎯 Production Ready**
- **Pre-trained Models**: All ML and neural models work immediately
- **No Training Required**: Models ready to use after installation
- **Built-in Analytics**: Usage tracking and performance monitoring
- **Robust Error Handling**: Graceful fallbacks and comprehensive reporting
- **🧪 Data Contamination**: Comprehensive contamination testing system for robustness analysis
- **🌐 Web Dashboard**: Interactive Streamlit interface with real-time benchmarking

## 🚀 **Quick Start**

### **Installation**

```bash
pip install lrdbench
```

### **Basic Usage**

```python
import lrdbench

# Generate synthetic data
from lrdbench import FBMModel
fbm = FBMModel(H=0.7, sigma=1.0)
data = fbm.generate(1000)

# Run comprehensive benchmark
from lrdbench import ComprehensiveBenchmark
benchmark = ComprehensiveBenchmark()
results = benchmark.run_comprehensive_benchmark()

# Get analytics summary
summary = lrdbench.get_analytics_summary()
print(summary)
```

### **Advanced Usage**

```python
# Generate data with contamination
from lrdbench import FGNModel
from lrdbench.models.contamination.contamination_models import ContaminationModel

fgn = FGNModel(H=0.6, sigma=1.0)
clean_data = fgn.generate(1000)

# Add comprehensive contamination
contamination_model = ContaminationModel()
contaminated_data = contamination_model.add_noise_gaussian(clean_data, std=0.1)
contaminated_data = contamination_model.add_trend_linear(contaminated_data, slope=0.01)

# Run comprehensive benchmark with contamination analysis
results = benchmark.run_comprehensive_benchmark()
```

## 📚 **Documentation**

- **📖 [User Guide](documentation/user_guides/getting_started.md)**: Getting started tutorial
- **🚀 [Web Dashboard](documentation/user_guides/web_dashboard.md)**: Complete web dashboard guide
- **🧪 [Contamination System](documentation/api_reference/contamination.md)**: Data contamination documentation
- **🔧 [API Reference](documentation/api_reference/README.md)**: Complete API documentation
- **📊 [Examples](examples/)**: Usage examples and demonstrations
- **🔬 [Model Theory](documentation/technical/model_theory.md)**: Mathematical foundations

## 🌐 **Web Dashboard**

**🚀 Interactive Web Interface**: Access LRDBenchmark through a modern web dashboard built with Streamlit.

### **Features**
- **📈 Interactive Data Generation**: Generate synthetic time series with configurable parameters
- **🔬 Real-time Benchmarking**: Run comprehensive benchmarks with all 12 estimators
- **🧪 Data Contamination**: Add various contamination types and analyze robustness
- **📊 Rich Visualizations**: Interactive plots and charts using Plotly
- **📈 Performance Analytics**: Track estimator performance and robustness metrics
- **📥 Results Export**: Download benchmark results in JSON format with proper serialization

### **Quick Start**
```bash
# Navigate to web dashboard
cd web_dashboard

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run streamlit_app.py
```

### **Deploy Online**
- **Streamlit Cloud**: Free hosting at [share.streamlit.io](https://share.streamlit.io)
- **Local Development**: Run locally for development and testing
- **Docker**: Containerized deployment option available

### **Documentation**
- **📖 [Dashboard README](web_dashboard/README.md)**: Complete dashboard documentation
- **🧪 [Test Suite](web_dashboard/test_dashboard.py)**: Verify dashboard functionality

## 🧪 **Examples & Demos**

### **Quick Examples**
- **Basic Usage**: `examples/quick_start_demo.py`
- **Comprehensive API**: `examples/comprehensive_api_demo.py`
- **Benchmark Examples**: `examples/benchmark_examples.py`

### **Advanced Demos**
- **CPU-based**: `demos/cpu_based/`
- **GPU-based**: `demos/gpu_based/`
- **Performance Comparison**: `demos/gpu_based/high_performance_comparison_demo.py`

## 📊 **Analytics & Monitoring**

LRDBench includes a built-in analytics system that tracks:
- **Usage Patterns**: Which estimators are used most
- **Performance Metrics**: Execution times and resource usage
- **Error Analysis**: Failure patterns and reliability scores
- **Workflow Insights**: Common usage sequences and patterns

```python
# Enable analytics (enabled by default)
lrdbench.enable_analytics(True, privacy_mode=True)

# Get usage summary
summary = lrdbench.get_analytics_summary()

# Generate comprehensive report
report_path = lrdbench.generate_analytics_report(days=30)
```

## 🔧 **Configuration & Customization**

### **Analytics Settings**
```python
# Disable analytics
lrdbench.enable_analytics(False)

# Configure privacy mode
lrdbench.enable_analytics(True, privacy_mode=True)
```

### **Benchmark Configuration**
```python
# Customize benchmark parameters
benchmark = ComprehensiveBenchmark(
    data_lengths=[500, 1000, 2000],
    contamination_levels=[0.0, 0.1, 0.2],
    estimators=['classical', 'ml', 'neural']
)
```

## 🏆 **Performance Benchmarks**

LRDBench has been extensively tested and optimized:
- **Data Generation**: < 10ms for 1000 points
- **Estimation**: < 100ms for most estimators
- **Memory Usage**: Optimized for large datasets
- **GPU Acceleration**: Available for JAX-based methods

## 🤝 **Contributing**

We welcome contributions! Please see our [Development Guide](DEVELOPMENT.md) for:
- Development setup instructions
- Contributing guidelines
- Testing procedures
- Code review process

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 **Author**

**Davian R. Chin**  
*Department of Biomedical Engineering*  
*University of Reading*  
*Email: d.r.chin@pgr.reading.ac.uk*

## 📚 **References**

### **Core Research Papers**
- Beran, J. (1994). Statistics for Long-Memory Processes.
- Mandelbrot, B. B. (1982). The Fractal Geometry of Nature.
- Abry, P., & Veitch, D. (1998). Wavelet analysis of long-range-dependent traffic.
- Muzy, J. F., Bacry, E., & Arneodo, A. (1991). Wavelets and multifractal formalism for singular signals.

### **Neural Network Innovations**
- Hayashi, K., & Nakagawa, K. (2022). fSDE-Net: Generating Time Series Data with Long-term Memory.
- Nakagawa, K., & Hayashi, K. (2024). Lf-Net: Generating Fractional Time-Series with Latent Fractional-Net.
- Li, Z., et al. (2020). Fourier Neural Operator for Parametric Partial Differential Equations.
- Raissi, M., et al. (2019). Physics-informed neural networks: A deep learning framework for solving forward and inverse problems.

---

**For questions, contributions, or collaboration opportunities, please refer to our comprehensive documentation or create an issue on GitHub.**
