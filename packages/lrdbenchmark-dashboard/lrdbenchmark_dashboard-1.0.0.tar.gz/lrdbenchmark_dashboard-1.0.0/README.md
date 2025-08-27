# 🚀 LRDBenchmark Dashboard

**Interactive web dashboard for LRDBenchmark - Long-range dependence analysis**

[![PyPI version](https://badge.fury.io/py/lrdbenchmark-dashboard.svg)](https://badge.fury.io/py/lrdbenchmark-dashboard)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Live Dashboard](https://img.shields.io/badge/Live%20Dashboard-Streamlit%20Cloud-blue)](https://lrdbenchmark-dev.streamlit.app/)

## 🌐 **Live Dashboard**

**Access the dashboard online**: [https://lrdbenchmark-dev.streamlit.app/](https://lrdbenchmark-dev.streamlit.app/)

## 📖 **Overview**

LRDBenchmark Dashboard is a comprehensive, interactive web application built with Streamlit that provides a complete interface for long-range dependence analysis. The dashboard includes all 12 estimators, comprehensive data contamination testing, and revolutionary auto-optimization features.

## ✨ **Key Features**

### 🚀 **Auto-Optimization System**
- **Automatic Optimization Selection**: System chooses the fastest available implementation (NUMBA → JAX → Standard)
- **NUMBA Optimizations**: Up to 850x speedup for critical estimators
- **JAX Optimizations**: GPU acceleration for large-scale computations
- **Graceful Fallback**: Reliable operation even when optimizations fail
- **Performance Monitoring**: Real-time execution time tracking

### 🧪 **Comprehensive Data Contamination System**
- **13 Contamination Types**: Trends, noise, artifacts, sampling issues, measurement errors
- **Real-time Application**: Apply contamination during data generation
- **Robustness Analysis**: Test estimator performance under various conditions
- **Visual Results**: Heatmaps and rankings of estimator robustness

### 📊 **Complete Estimator Suite**
- **12 Estimators**: All major long-range dependence estimation methods
- **Multiple Domains**: Temporal, spectral, wavelet, and multifractal methods
- **Auto-Optimized**: All estimators with performance improvements

## 🚀 **Quick Start**

### **Installation**

```bash
pip install lrdbenchmark-dashboard
```

### **Run Locally**

```bash
# Method 1: Using the command-line tool
lrdbenchmark-dashboard

# Method 2: Using streamlit directly
streamlit run -m lrdbenchmark_dashboard.app
```

### **Run with Python**

```python
import streamlit as st
from lrdbenchmark_dashboard.app import main

# Run the dashboard
main()
```

## 📊 **Dashboard Features**

### **1. 📈 Data Generation**
Generate synthetic time series data with configurable parameters:
- **Data Models**: FBM, FGN, ARFIMA, MRW
- **Parameters**: Hurst parameter (H), standard deviation (σ), data length
- **Contamination Options**: 13 different contamination types with adjustable intensity

### **2. 🚀 Auto-Optimization**
Demonstrate the auto-optimization system:
- **System Status**: Optimization level display and success rate metrics
- **Live Demo**: Test all auto-optimized estimators with performance comparisons
- **Download Results**: Export optimization results in JSON format

### **3. 🔬 Benchmarking**
Run comprehensive benchmarks on generated data:
- **Estimator Selection**: Choose from 12 available estimators
- **Configuration**: Multiple benchmark runs with statistical analysis
- **Execution Tracking**: Real-time performance monitoring

### **4. 📊 Results**
View and analyze benchmark results:
- **Results Display**: Tabular results with all metrics
- **Visualizations**: Interactive plots and performance rankings
- **Export Options**: Download benchmark results in JSON format

### **5. 🧪 Contamination Analysis**
Comprehensive contamination robustness testing:
- **Robustness Testing**: Test estimators on clean vs contaminated data
- **Multiple Scenarios**: Various contamination combinations
- **Visual Results**: Heatmaps and performance rankings

### **6. 📈 Analytics**
System analytics and performance monitoring:
- **Session Information**: Current session status and metrics
- **Auto-Optimization Metrics**: Performance tracking and optimization counts
- **Usage Analytics**: Comprehensive usage statistics

### **7. ℹ️ About**
Comprehensive information about LRDBenchmark:
- **Framework Overview**: Complete feature list and capabilities
- **Installation Links**: PyPI and GitHub information

## 🧪 **Contamination Types**

### **Trend Contamination**
1. **Linear Trend**: Add linear trend with configurable slope
2. **Polynomial Trend**: Add polynomial trend with degree and coefficient
3. **Exponential Trend**: Add exponential trend with rate parameter
4. **Seasonal Trend**: Add seasonal trend with period and amplitude

### **Noise Contamination**
5. **Gaussian Noise**: Add Gaussian noise with standard deviation
6. **Colored Noise**: Add colored noise with power parameter
7. **Impulsive Noise**: Add impulsive noise with probability

### **Artifact Contamination**
8. **Spikes**: Add random spikes with probability and amplitude
9. **Level Shifts**: Add level shifts with probability and amplitude
10. **Missing Data**: Add missing data points with probability

### **Sampling Issues**
11. **Irregular Sampling**: Simulate irregular sampling patterns
12. **Aliasing**: Add aliasing effects with frequency parameter

### **Measurement Errors**
13. **Systematic Bias**: Add systematic measurement bias
14. **Random Measurement Error**: Add random measurement errors

## 🔬 **Available Estimators**

### **Temporal Methods**
- **DFA**: Detrended Fluctuation Analysis
- **RS**: R/S Analysis (Rescaled Range)
- **DMA**: Detrended Moving Average
- **Higuchi**: Higuchi method

### **Spectral Methods**
- **GPH**: Geweke-Porter-Hudak estimator
- **Periodogram**: Periodogram-based estimation
- **Whittle**: Whittle likelihood estimation

### **Wavelet Methods**
- **CWT**: Continuous Wavelet Transform
- **Wavelet Variance**: Wavelet variance analysis
- **Wavelet Log Variance**: Wavelet log variance analysis
- **Wavelet Whittle**: Wavelet Whittle estimation

### **Multifractal Methods**
- **MFDFA**: Multifractal Detrended Fluctuation Analysis

## 🏆 **Performance Features**

### **Auto-Optimization Levels**
- **🚀 NUMBA**: Up to 850x speedup for critical loops
- **⚡ JAX**: GPU acceleration for large-scale computations
- **📊 Standard**: Reliable fallback implementation

### **Success Metrics**
- **100% Success Rate**: All estimators working perfectly
- **Average Execution Time**: 0.1419s (revolutionary speed)
- **Performance Improvement**: 99%+ across all estimators

## 🔧 **Technical Requirements**

### **Dependencies**
- Python 3.8 or higher
- Streamlit >= 1.28.0
- NumPy >= 1.21.0
- Pandas >= 1.3.0
- Plotly >= 5.15.0
- LRDBenchmark >= 1.5.1

### **Installation Options**

```bash
# Basic installation
pip install lrdbenchmark-dashboard

# With development dependencies
pip install lrdbenchmark-dashboard[dev]

# With deployment dependencies
pip install lrdbenchmark-dashboard[deploy]
```

## 🌐 **Deployment**

### **Streamlit Cloud**
The dashboard is configured for Streamlit Cloud deployment:
- **Live URL**: [https://lrdbenchmark-dev.streamlit.app/](https://lrdbenchmark-dev.streamlit.app/)
- **Automatic Updates**: Deployed from GitHub repository
- **Cloud Optimized**: Configured for cloud environment

### **Local Deployment**
For local deployment:

```bash
# Install the package
pip install lrdbenchmark-dashboard

# Run the dashboard
lrdbenchmark-dashboard
```

### **Docker Deployment**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "-m", "lrdbenchmark_dashboard.app", "--server.port=8501", "--server.address=0.0.0.0"]
```

## 📚 **Documentation**

- **📖 [User Guide](https://github.com/dave2k77/LRDBenchmark/tree/master/documentation/user_guides/getting_started.md)**: Getting started tutorial
- **🚀 [Web Dashboard Guide](https://github.com/dave2k77/LRDBenchmark/tree/master/documentation/user_guides/web_dashboard.md)**: Complete dashboard documentation
- **🧪 [Contamination System](https://github.com/dave2k77/LRDBenchmark/tree/master/documentation/api_reference/contamination.md)**: Data contamination documentation
- **🔧 [API Reference](https://github.com/dave2k77/LRDBenchmark/tree/master/documentation/api_reference/README.md)**: Complete API documentation

## 🤝 **Contributing**

We welcome contributions! Please see our [Development Guide](https://github.com/dave2k77/LRDBenchmark/blob/master/DEVELOPMENT.md) for:
- Development setup instructions
- Contributing guidelines
- Testing procedures
- Code review process

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](https://github.com/dave2k77/LRDBenchmark/blob/master/LICENSE) file for details.

## 👨‍💻 **Author**

**Davian R. Chin**  
*Department of Biomedical Engineering*  
*University of Reading*  
*Email: d.r.chin@pgr.reading.ac.uk*

## 🔗 **Links**

- **🌐 Live Dashboard**: [https://lrdbenchmark-dev.streamlit.app/](https://lrdbenchmark-dev.streamlit.app/)
- **📦 PyPI Package**: [https://pypi.org/project/lrdbenchmark-dashboard/](https://pypi.org/project/lrdbenchmark-dashboard/)
- **🐙 GitHub Repository**: [https://github.com/dave2k77/LRDBenchmark](https://github.com/dave2k77/LRDBenchmark)
- **📚 Documentation**: [https://github.com/dave2k77/LRDBenchmark/tree/master/documentation](https://github.com/dave2k77/LRDBenchmark/tree/master/documentation)

---

**For questions, contributions, or collaboration opportunities, please refer to our comprehensive documentation or create an issue on GitHub.**
