# Test Suite for Food Price Clustering Project

This directory contains organized test packages for the food price clustering system.

## 📁 **Test Package Structure**

```
tests/
├── __init__.py                    # Test package initialization
├── README.md                      # This file - main testing guide
├── pytest.ini                    # Pytest configuration (moved to root)
├── consolidation/                 # Data consolidation tests
│   ├── __init__.py
│   ├── README.md                  # Consolidation testing guide
│   ├── conftest.py                # Consolidation-specific fixtures
│   ├── test_basic_functionality.py
│   ├── test_consolidation_working.py
│   ├── test_consolidation_system.py
│   └── test_logging_fix.py
├── eda/                          # Exploratory Data Analysis tests (future)
├── clustering/                   # Clustering algorithm tests (future)
└── integration/                  # Integration tests (future)
```

## 🚀 **Quick Start**

### **Run All Consolidation Tests**

```bash
# Run all consolidation tests
poetry run pytest tests/consolidation/ -v

# Run only working consolidation tests (recommended)
poetry run pytest tests/consolidation/test_basic_functionality.py tests/consolidation/test_consolidation_working.py tests/consolidation/test_logging_fix.py -v
```

### **Run Specific Test Categories**

```bash
# Basic functionality only
poetry run pytest tests/consolidation/test_basic_functionality.py -v

# Working functionality only
poetry run pytest tests/consolidation/test_consolidation_working.py -v

# Logging system tests
poetry run pytest tests/consolidation/test_logging_fix.py -v
```

## 📊 **Current Test Status**

| Package           | Tests     | Status    | Coverage                              |
| ----------------- | --------- | --------- | ------------------------------------- |
| **Consolidation** | 45+ tests | ✅ Ready  | Data pipeline, configs, logging       |
| **EDA**           | -         | 🔮 Future | Data exploration, visualization       |
| **Clustering**    | -         | 🔮 Future | K-means, fuzzy clustering, evaluation |
| **Integration**   | -         | 🔮 Future | End-to-end workflows                  |

## 🎯 **Test Package Benefits**

### ✅ **Organized Structure**

-   Each component has its own test suite
-   Clear separation of concerns
-   Easy to navigate and maintain

### ✅ **Selective Testing**

-   Run only consolidation tests: `pytest tests/consolidation/`
-   Skip slow tests during development
-   Focus on specific components

### ✅ **Scalable Development**

-   Add new test packages as features are developed
-   Independent fixtures and configurations
-   Parallel development support

## 📋 **Development Workflow**

### **Before Development**

```bash
# Run consolidation tests to ensure baseline works
poetry run pytest tests/consolidation/test_basic_functionality.py tests/consolidation/test_consolidation_working.py -v
```

### **During Development**

```bash
# Run relevant test package
poetry run pytest tests/consolidation/ -v

# Run specific test file
poetry run pytest tests/consolidation/test_basic_functionality.py -v

# Run single test
poetry run pytest tests/consolidation/test_basic_functionality.py::test_imports -v
```

### **Before Commits**

```bash
# Run all passing consolidation tests
poetry run pytest tests/consolidation/test_basic_functionality.py tests/consolidation/test_consolidation_working.py tests/consolidation/test_logging_fix.py -v
```

## 🔧 **Configuration**

### **Main pytest.ini** (Project Root)

Global pytest configuration for all test packages.

### **Package-Specific conftest.py**

Each test package has its own `conftest.py` with:

-   Package-specific fixtures
-   Custom test configurations
-   Shared test utilities

## 🚀 **Adding New Test Packages**

When adding EDA, clustering, or other components:

1. **Create package directory**: `mkdir tests/new_component/`
2. **Add init file**: `touch tests/new_component/__init__.py`
3. **Create conftest.py**: Component-specific fixtures
4. **Add README.md**: Package-specific documentation
5. **Write tests**: Following established patterns

## 🎯 **Best Practices**

### **Test Organization**

-   Keep related tests in the same package
-   Use descriptive test file names
-   Group tests by functionality, not by file structure

### **Fixtures**

-   Put shared fixtures in package-level `conftest.py`
-   Use project-wide fixtures sparingly
-   Prefer composition over inheritance

### **Naming**

-   `test_basic_*.py` - Core functionality tests
-   `test_*_working.py` - Verified working features
-   `test_*_system.py` - Comprehensive system tests
-   `test_*_integration.py` - Cross-component tests

## 📊 **Current Consolidation Test Results**

```
===================================== test session starts =====================================
collected 45 items

tests/consolidation/test_basic_functionality.py .................. [ 40%]
tests/consolidation/test_consolidation_working.py ................ [ 93%]
tests/consolidation/test_logging_fix.py ...                       [100%]

===================================== 45 passed in 0.11s =====================================
```

## 🔍 **Troubleshooting**

### **Import Issues**

```bash
# If imports fail, ensure you're in project root
cd /path/to/clustering-food-prices-kalimantan
poetry run pytest tests/consolidation/ -v
```

### **Path Issues**

```bash
# Check Python path
poetry run python -c "import sys; print(sys.path)"

# Verify package structure
poetry run python -c "from clustering_food_prices_kalimantan import ConsolidationPipeline; print('OK')"
```

### **Test Discovery Issues**

```bash
# Force test discovery
poetry run pytest --collect-only tests/consolidation/

# Run with full paths
poetry run pytest tests/consolidation/test_basic_functionality.py -v
```

---

## 🎉 **Ready for Development**

The consolidation test package is fully functional and ready for development. When you're ready to add EDA, clustering, or other components, simply create new test packages following the same structure.

**Current Status**: ✅ Consolidation tests organized and working  
**Next Steps**: Develop EDA pipeline and create `tests/eda/` package

---

_Happy Testing!_ 🚀
