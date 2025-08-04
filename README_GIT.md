# Git Repository Setup Guide

This document provides guidance for setting up and managing the GitHub repository for the Food Price Consolidation project.

## 🚀 Initial Repository Setup

### 1. Create GitHub Repository

```bash
# Option A: Using GitHub CLI (recommended)
gh repo create clustering-food-prices-kalimantan --public --description "Food price data consolidator and clustering analyzer for Kalimantan cities"

# Option B: Create manually on GitHub.com
# Go to github.com → New repository → clustering-food-prices-kalimantan
```

### 2. Initialize Local Git Repository

```bash
# Initialize git (if not already done)
git init

# Add all files (respecting .gitignore)
git add .

# Initial commit
git commit -m "Initial commit: Food price consolidation system

- Complete modular data processing pipeline
- YAML-based configuration system
- Comprehensive test suite (45+ tests)
- Jupyter notebook for interactive analysis
- Production-ready logging and error handling"

# Connect to GitHub repository
git remote add origin https://github.com/YOUR_USERNAME/clustering-food-prices-kalimantan.git

# Push to GitHub
git push -u origin main
```

## 📁 What Gets Committed vs Ignored

### ✅ **COMMITTED** (Safe for public GitHub):

-   **Source code**: `src/` directory with all Python modules
-   **Scripts**: `scripts/run_consolidation.py`
-   **Configuration**: Template and example YAML configs
-   **Tests**: Complete test suite in `tests/consolidation/`
-   **Documentation**: README files, docstrings, guides
-   **Notebooks**: Jupyter notebooks (with outputs cleaned)
-   **Project structure**: `pyproject.toml`, `.gitignore`, directory structure

### ❌ **IGNORED** (Not committed):

-   **Raw data files**: `data/raw/**` (potentially sensitive, very large)
-   **Processed data**: `data/processed/**` (can be regenerated)
-   **Log files**: `logs/**` (runtime-generated)
-   **Virtual environments**: `.venv/`, `env/`
-   **IDE settings**: `.vscode/`, `.idea/`
-   **Cache files**: `__pycache__/`, `.pytest_cache/`
-   **Temporary files**: `*.log`, `*.tmp`, backup files

## 🔒 Data Privacy & Security

### **Why Data Files Are Ignored:**

1. **Size**: Excel files can be large and hit GitHub's file size limits
2. **Privacy**: Food price data might contain sensitive market information
3. **Reproducibility**: Others can run the system with their own data
4. **Storage**: GitHub has repository size limits

### **Sharing Data Structure:**

-   ✅ Directory structure is preserved with `.gitkeep` files
-   ✅ Documentation explains expected data format
-   ✅ Sample configuration files show how to use the system
-   ✅ Users can add their own data files locally

## 🌿 Branching Strategy

### **Recommended Branch Structure:**

```
main                    # Production-ready code
├── development        # Integration branch
├── feature/eda       # Exploratory Data Analysis
├── feature/clustering # Clustering algorithms
├── feature/analysis  # Results analysis
└── hotfix/*          # Bug fixes
```

### **Workflow:**

```bash
# Create feature branch
git checkout -b feature/eda
git push -u origin feature/eda

# Work on feature, commit changes
git add .
git commit -m "Add EDA pipeline with visualization"

# Push changes
git push origin feature/eda

# Create Pull Request on GitHub
# Merge to development → test → merge to main
```

## 📋 Commit Message Guidelines

### **Format:**

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### **Types:**

-   `feat`: New feature
-   `fix`: Bug fix
-   `docs`: Documentation changes
-   `test`: Adding/updating tests
-   `refactor`: Code refactoring
-   `perf`: Performance improvements
-   `style`: Code style changes

### **Examples:**

```bash
git commit -m "feat(consolidation): Add year range filtering support"
git commit -m "fix(logging): Ensure logs go to logs/ directory"
git commit -m "docs(readme): Update configuration examples"
git commit -m "test(consolidation): Add integration tests for pipeline"
```

## 🏷️ Release Management

### **Semantic Versioning:**

-   `v0.1.0` - Initial consolidation system
-   `v0.2.0` - EDA pipeline addition
-   `v0.3.0` - Clustering algorithms
-   `v1.0.0` - Complete thesis system

### **Creating Releases:**

```bash
# Tag release
git tag -a v0.1.0 -m "Release v0.1.0: Complete data consolidation system"
git push origin v0.1.0

# Or use GitHub releases UI for detailed release notes
```

## 🔄 Keeping Repository Clean

### **Regular Maintenance:**

```bash
# Clean up merged branches
git branch -d feature/old-feature
git push origin --delete feature/old-feature

# Update .gitignore if needed
git add .gitignore
git commit -m "chore: Update .gitignore for new file types"
```

### **Pre-commit Checks:**

```bash
# Before committing, always run:
poetry run pytest tests/consolidation/  # Run tests
poetry run black src/ tests/            # Format code
poetry run ruff check src/ tests/       # Lint code
```

## 👥 Collaboration Guidelines

### **For Contributors:**

1. **Fork** the repository
2. **Clone** your fork locally
3. **Create** feature branch
4. **Make** changes with tests
5. **Submit** Pull Request

### **Code Review Process:**

-   All changes require review
-   Tests must pass
-   Documentation must be updated
-   Follow Python best practices

## 📊 Repository Statistics

### **What to Expect:**

-   **Language**: Python (primary), YAML (configs), Markdown (docs)
-   **Size**: ~50MB (without data files)
-   **Files**: ~30-40 source files + documentation
-   **Tests**: 45+ test cases
-   **Documentation**: Comprehensive README and guides

## 🎯 Benefits of This Setup

✅ **Professional**: Clean, well-organized repository  
✅ **Secure**: No sensitive data exposed  
✅ **Reproducible**: Others can replicate your work  
✅ **Maintainable**: Clear structure and documentation  
✅ **Collaborative**: Easy for others to contribute  
✅ **Academic**: Perfect for thesis documentation

---

**Your repository is now ready for serious academic and professional development!** 🚀
