# 📦 MemViz (v1.1.0): Embedded Low-Level Memory Visualization for C++

[![Docs](https://img.shields.io/badge/docs-Doxygen-blue)](https://la-10.github.io/MemViz)
![GitHub license](https://img.shields.io/github/license/LA-10/MemViz)
![GitHub issues](https://img.shields.io/github/issues/LA-10/MemViz)
![GitHub stars](https://img.shields.io/github/stars/LA-10/MemViz?style=social)
![GitHub repo size](https://img.shields.io/github/repo-size/LA-10/MemViz)
![version](https://img.shields.io/badge/version-v1.1.0-blue.svg)

---

> **MemViz** is a zero-overhead, developer-focused C++20 library for **introspecting memory layouts, vtables, allocations, and raw bit patterns** — directly inside your own programs. 
>
>**⚡ MemViz is fast.** In benchmarks, our new sorted-vector design is ~7.5× faster than the old version and performs within ~10–20% of standard C++ new/delete in typical workloads — while adding full allocation tracking and leak detection.

👉 **Get Started**: [Documentation & Examples](https://la-10.github.io/MemViz/)  
👉 **Contribute**: See [CONTRIBUTING.md](CONTRIBUTING.md)  
👉 **Roadmap**: See [ROADMAP.md](ROADMAP.md)  

⭐ If you find this project interesting, please give it a **star** — it helps others discover it!

---

## 🎯 Mission Statement

MemViz integrates directly into your C++ codebase, giving you **X-ray vision** into how objects are laid out and managed in memory — at runtime.  
All features are **header-only** and can be toggled at compile time, with **zero performance overhead** when disabled.

---

## 🧠 Core Features

| Feature                                  | Example Usage                                   |
| ---------------------------------------- | ----------------------------------------------- |
| 📐 Visualize object layout & padding      | `memviz::dumpLayout(obj);`     |
| 🌀 Inspect vtables & virtual dispatch     | `memviz::inspectVTable(ptrToBase);`             |
| 🔍 Safe bitwise casting & inspection      | `memviz::castAndPrint<To>(from);`               |
| 💧 Track allocations & detect leaks       | `memviz::reportLeaks();`                        |
| 📊 Allocation logging at runtime          | `memviz::printAllocationLog();`                 |
| 🎓 Education & teaching aid               | Perfect for visualizing padding, ABI, vtables   |

---

## ⚡ Performance

MemViz has been benchmarked against both the original linear-scan implementation and standard C++ `new/delete`.

| Test                      | Mean (ns) | StdDev (ns) | Min (ns) | Max (µs) |
| ------------------------- | --------- | ----------- | -------- | -------- |
| **Before (linear scan)**  | 296.68    | 762.48      | 264      | 72.81    |
| **After (sorted vector)** | 39.34     | 26.69       | 35       | 4.55     |
| **New/Delete (tracked)**  | 45.15     | 170.44      | 38       | 26.56    |

---

### Key insights

* The new **sorted vector + `lower_bound`** implementation is **\~7.5× faster** on average compared to the old linear scan design.
* **Stability improved drastically**: standard deviation fell from \~762 ns to \~27 ns, and worst-case spikes dropped from \~73 µs to \~5 µs.
* In **ideal conditions**, MemViz `new/delete` performs on par with standard C++ `new/delete` (\~40 ns per operation).
* In **typical workloads**, it remains within \~10–20% of baseline, while adding leak detection and allocation tracking.

---

### 📊 Benchmark results

![Performance comparison](benchmark/img/Figure_1.png)

*Each test was run with 50,000 iterations. Bars show mean, StdDev, min, and max for alloc/free cycles.*

---

## 🚀 Quick Start

### 1️⃣ Install
Header-only — just drop `include/memviz/` into your project, or add via CMake:

```cmake
add_subdirectory(memviz)
target_link_libraries(your_target PRIVATE memviz)
````

### 2️⃣ Define and Register a Type

```cpp
struct Person {
    int age;
    char gender;
    double height;
};

MEMVIZ_REGISTER(Person, std::make_tuple(
    std::make_pair("age", &Person::age),
    std::make_pair("gender", &Person::gender),
    std::make_pair("height", &Person::height)
));
```

### 3️⃣ Inspect Its Layout

```cpp
Person p = {25, 'F', 170.5};
memviz::LayoutInspector::dumpLayout(p);
```

**Output:**

```
[Layout] Type: Person
  Size: 16 bytes
  Alignment: 8 bytes
  Location: 0x7ffee7...
  Members:
      age: offset = 0
      gender: offset = 4
      height: offset = 8
```

### 4️⃣ Track Allocations

```cpp
Foo* a = new Foo(1, "Alpha");
Foo* b = new Foo(2, "Beta");
delete a;

memviz::reportLeaks(); // shows b as leaked
```

**Output:**

```
[0] LEAK 0x7fe40e705be0 (32 bytes)
[SUMMARY] 1 potential leak(s), total 32 bytes.
```

---

## 🌍 Use Cases

* 🔍 Debugging ABI alignment/padding across compilers
* 🎓 Teaching memory layouts, object models, and inheritance
* 🛠 Diagnosing memory leaks in tests and CI pipelines
* 🌀 Exploring vtables and polymorphic dispatch
* 📊 Visualizing object layouts for performance tuning and serialization

---

## 🔗 Resources

* [📘 Full Documentation](https://la-10.github.io/MemViz/)
* [🛠 Examples](./examples)
* [📝 Changelog](CHANGELOG.md)

---

## ⚡️ Summary

MemViz gives developers **deep insight into C++ memory behavior**:

* Inspect layouts
* Track allocations
* Explore vtables
* Debug smarter
* Learn faster

All in **pure C++20**, header-only, with **zero overhead when disabled**.
