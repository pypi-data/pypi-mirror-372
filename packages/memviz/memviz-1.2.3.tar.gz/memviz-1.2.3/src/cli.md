# MemViz

[![PyPI version](https://img.shields.io/pypi/v/memviz.svg)](https://pypi.org/project/memviz/)
[![Python versions](https://img.shields.io/pypi/pyversions/memviz.svg)](https://pypi.org/project/memviz/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](../LICENSE)

**MemViz** is a teaching & visualization tool for **C++ memory performance**.  
It helps students and developers understand:

- 📦 **Memory layout** (structs, padding, vtables)  
- 💾 **Cache behavior** (L1/L2/L3 misses, read vs write)  
- 🚀 **Performance costs** of poor data locality  

MemViz is designed as a **CLI tool + Python library**.  
It integrates with **Valgrind/Cachegrind** and shows results in a **clear, color-coded summary**.

---

## ✨ Features

- ✅ Run your C++ program under Valgrind/Cachegrind  
- ✅ Parse cache statistics into a clean report  
- ✅ Color-coded traffic light indicators (green/yellow/red)  
- ✅ Read vs Write miss rates shown side-by-side  
- ✅ Works with Docker fallback (for macOS/Apple Silicon)  
- ✅ Great for teaching cache locality, struct packing, and memory efficiency  

---

## 🔧 Installation

From **PyPI**:

```bash
pip install memviz
```

⸻

## 🚀 Quickstart

1.	Compile your C++ program with debug info:
```bash
g++ -g -O2 ./examples/memTracker.cpp -o ./examples/memTracker
```
2.	Run MemViz Cachegrind:

```bash
memviz cachegrind ./examples/memTracker
```
3.	See results:

```bash
=======================  SUMMARY   =======================
INSTRUCTIONS MISS RATE: 
        1. L1 I-cache miss rate: 0.1% ✅
        2. Last-level instruction miss rate: 0.1% ✅

DATA MISS RATE: 
        1. L1 D-cache miss rate: 1.94% ✅
        2. Last-level D-cache miss rate: 1.21% 🟨

OVERALL LAST LEVEL MISS RATE: 66.56% 🔴

READ       vs    WRITE     
-------------------------
3.6%          1.95% 
```


## 📦 Docker Support

On macOS (especially ARM/M1/M2), Valgrind may not be available.
MemViz automatically falls back to Docker if needed.


## 📚 Documentation
	•	CLI Usage Guide
	•	Valgrind Documentation
	•	Background on Cache Locality



## 🛠 Development

Clone and install in editable mode:

```bash
git clone https://github.com/yourname/memviz.git
cd memviz
pip install -e .
```


## 📄 License

This project is licensed under the MIT License.
See the LICENSE file for details.

⸻
