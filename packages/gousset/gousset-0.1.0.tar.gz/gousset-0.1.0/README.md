# 🕰️ Gousset

> *Your pocket profiler* - Elegant, friendly timing for Python functions


[![CI](https://github.com/etienne87/gousset/workflows/CI/badge.svg)](https://github.com/etienne87/gousset/actions)

**Gousset** (pronounced "goo-SAY") is a simple, unobtrusive timing profiler for Python. Like a elegant pocket watch, it sits quietly and tells you exactly what you need to know about your function performance.

## ✨ Features

- **🎯 One-line setup** - Just `gousset.instrument(my_module)`
- **🔍 Automatic nested call detection** - Captures internal function calls
- **📊 Rich statistics** - Mean, std dev, min, max, call counts
- **🚫 Zero code changes** - Your modules stay clean
- **📈 Production ready** - Minimal overhead, comprehensive insights

## 🚀 Quick Start

```python
import gousset
import my_module

# Instrument your module - that's it!
gousset.instrument(my_module)

# Use your functions normally
result = my_module.some_function()

# Statistics automatically print at program exit
```

## 📦 Installation

```bash
pip install gousset
```

## 🎭 Why Gousset?

**Other tools are intimidating:**
```python
# cProfile - overwhelming output
python -m cProfile my_script.py  # 😵‍💫 Wall of text

# line_profiler - pollutes your code
@profile  # 😤 Decorators everywhere!
def my_function():
    pass
```

**Gousset is friendly:**
```python
import gousset
gousset.instrument(my_module)  # 😌 One line, done!
```

## 📊 Sample Output

```
=== Gousset Timing Statistics for Module: my_module ===
----------------------------------------------------------------------
Function: slow_function
  Calls:        5
  Sum:     0.025123s
  Average: 0.005025s
  Std Dev: 0.000012s
  Min:     0.005008s
  Max:     0.005045s

Function: fast_function
  Calls:        8
  Sum:     0.008034s
  Average: 0.001004s
  Std Dev: 0.000003s
  Min:     0.001001s
  Max:     0.001009s
```

## 🔍 Advanced Example

```python
import gousset
import requests_module
import database_module
import utils

# Instrument multiple modules
gousset.instrument(requests_module)
gousset.instrument(database_module)
gousset.instrument(utils)

# Your application runs normally
app.run()

# Exit statistics show timing for ALL instrumented modules:
# - Which functions are bottlenecks?
# - How many times is each function called?
# - What's the performance distribution?
```

## 🧪 Development

```bash
# Clone repository
git clone https://github.com/yourusername/gousset.git
cd gousset

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run example
python examples/basic_usage.py
```

## 🤝 Contributing

Contributions welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md).

## 📝 License

MIT License - see [LICENSE](LICENSE) file.

## 🎯 Philosophy

> *"The best profiler is the one you actually use."*

Gousset follows the principle of **friendly tooling** - powerful capabilities with zero friction. Like a trusted pocket watch, it should be:

- **Elegant** - Beautiful, clean output
- **Reliable** - Always works, minimal overhead
- **Unobtrusive** - Doesn't interfere with your work
- **Insightful** - Shows you exactly what you need to know

---

**Gousset** - *Timing, reimagined* ⚡