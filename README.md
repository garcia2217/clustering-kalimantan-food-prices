# Food Price Data Consolidation for Kalimantan

A comprehensive tool for consolidating food price data from multiple Excel files across different cities in Kalimantan, Indonesia. This project provides a robust, modular system for data processing, validation, and consolidation with built-in error handling and logging.

## 🎯 Features

-   **Modular Architecture**: Clean separation of concerns with dedicated modules for validation, loading, cleaning, and consolidation
-   **Robust Data Processing**: Handles missing values, data type conversion, and data validation
-   **Flexible Configuration**: Pydantic-based configuration system with environment variable support
-   **Comprehensive Logging**: Detailed logging with configurable levels
-   **Multiple Output Formats**: Save consolidated data as CSV, Excel, or both
-   **Filtering Options**: Filter by years, cities, and commodities
-   **Easy-to-Use Interface**: High-level pipeline API and command-line script

## 📁 Project Structure

```
clustering-food-prices-kalimantan/
├── data/
│   ├── raw/                    # Raw Excel files organized by province/city/year
│   ├── processed/              # Consolidated output files
│   ├── features/               # Feature-engineered data (for future use)
│   └── results/                # Analysis results (for future use)
├── src/clustering_food_prices_kalimantan/
│   ├── __init__.py             # Main package exports
│   ├── pipelines/              # Pipeline modules for different stages
│   │   ├── __init__.py         # Pipeline exports
│   │   └── consolidation.py    # Data consolidation pipeline
│   ├── config/
│   │   └── settings.py         # Configuration classes
│   └── data/                   # Data processing modules
│       ├── validator.py        # Data validation utilities
│       ├── loader.py           # File loading and discovery
│       ├── cleaner.py          # Data cleaning and transformation
│       └── consolidator.py     # Main consolidation orchestrator
├── scripts/
│   └── run_consolidation.py    # Main consolidation script
├── configs/
│   ├── default_consolidation.yaml   # Standard configuration
│   ├── twelve_cities.yaml           # Twelve cities analysis (2020-2024)
│   ├── 2018_2023.yaml               # Historical year range analysis
│   └── README.md                     # Configuration guide
├── notebooks/                  # Jupyter notebooks (for future analysis)
├── tests/                      # Test files
└── pyproject.toml             # Project configuration and dependencies
```

## 🚀 Quick Start

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd clustering-food-prices-kalimantan
```

2. Install dependencies using Poetry:

```bash
poetry install
```

> **Note**: The project now includes PyYAML for configuration file support, which will be automatically installed.

3. Activate the virtual environment:

```bash
poetry shell
```

### Basic Usage

#### Option 1: Simple Usage (Zero Configuration)

The easiest way to get started:

```bash
# Use built-in defaults (works immediately!)
python scripts/run_consolidation.py

# Show what the defaults are
python scripts/run_consolidation.py --show-defaults

# Test without processing
python scripts/run_consolidation.py --dry-run
```

#### Option 2: Using Configuration Files (RECOMMENDED for Production)

For customized workflows and team collaboration:

```bash
# Use specific configuration file
python scripts/run_consolidation.py configs/twelve_cities.yaml

# List available configurations
python scripts/run_consolidation.py --list-configs

# Test configuration without processing
python scripts/run_consolidation.py configs/2018_2023.yaml --dry-run
```

**Available pre-built configurations:**

-   `configs/default_consolidation.yaml` - Standard full analysis (2022-2024, all cities)
-   `configs/twelve_cities.yaml` - Analysis of 12 representative cities (2020-2024)
-   `configs/2018_2023.yaml` - Historical analysis covering full available period

#### Option 3: Using the Python API

```python
from clustering_food_prices_kalimantan import ConsolidationPipeline

# Simple consolidation
pipeline = ConsolidationPipeline()
consolidated_data = pipeline.run_consolidation()

# Print summary
summary = pipeline.get_data_summary(consolidated_data)
print(f"Total records: {summary['total_records']:,}")
print(f"Cities: {', '.join(summary['cities'])}")
print(f"Commodities: {', '.join(summary['commodities'])}")
```

#### Option 4: Custom Configuration

```python
from clustering_food_prices_kalimantan import ConsolidationPipeline, ConsolidatorConfig

# Create custom configuration
config = ConsolidatorConfig(
    target_commodities=['Beras', 'Telur Ayam', 'Daging Ayam'],
    target_years=[2022, 2023, 2024],
    target_cities=['kota-pontianak', 'kota-banjarmasin'],
    log_level="DEBUG"
)

# Run with custom configuration
pipeline = ConsolidationPipeline(config=config)
consolidated_data = pipeline.run_consolidation()
```

## ⚙️ Configuration

The system uses Pydantic for configuration management. You can configure the system in several ways:

### 1. Environment Variables

Create a `.env` file in the project root:

```env
CONSOLIDATOR_TARGET_COMMODITIES=Beras,Telur Ayam,Daging Ayam
CONSOLIDATOR_TARGET_YEARS=2022,2023,2024
CONSOLIDATOR_LOG_LEVEL=INFO
```

### 2. Configuration Class

```python
from clustering_food_prices_kalimantan import ConsolidatorConfig

config = ConsolidatorConfig(
    target_commodities=['Beras', 'Telur Ayam'],
    target_years=[2023, 2024],
    log_level="DEBUG",
    enable_logging=True
)
```

### Available Configuration Options

-   `target_commodities`: List of commodities to extract
-   `target_years`: List of specific years to process
-   `year_range_start/end`: Year range (alternative to target_years)
-   `target_cities`: List of cities to process
-   `log_level`: Logging level (DEBUG, INFO, WARNING, ERROR)
-   `enable_logging`: Whether to enable detailed logging
-   `missing_value_indicators`: Values to treat as missing
-   `file_pattern`: File pattern to search for (default: "\*.xlsx")

## 📊 Data Structure Requirements

The system expects Excel files organized in the following structure:

```
data/raw/
├── kalimantan-barat/
│   ├── kota-pontianak/
│   │   ├── 2022.xlsx
│   │   ├── 2023.xlsx
│   │   └── 2024.xlsx
│   └── kab-sintang/
│       ├── 2022.xlsx
│       └── 2023.xlsx
├── kalimantan-selatan/
│   └── kota-banjarmasin/
│       ├── 2022.xlsx
│       └── 2023.xlsx
└── ...
```

### Excel File Format

Each Excel file should have:

-   A column named "Komoditas (Rp)" containing commodity names
-   Date columns in "dd/ mm/ yyyy" format
-   Price data with commas as thousands separators

## 🔍 Output

The consolidated data includes:

-   **Commodities**: Standardized commodity names
-   **City**: City name extracted from file path
-   **Date**: Parsed date in datetime format
-   **Price**: Cleaned numeric price data

Output files are saved to `data/processed/` by default:

-   `master_data_consolidated.csv`: CSV format
-   `master_data_consolidated.xlsx`: Excel format

## 🧪 Testing and Validation

The system includes comprehensive validation:

```python
# Validate data structure before processing
pipeline = ConsolidationPipeline()
validation_results = pipeline.validate_data_structure()

if validation_results['issues']:
    print("Issues found:", validation_results['issues'])
else:
    print(f"✅ {len(validation_results['valid_files'])} valid files found")
```

## 📝 Logging

The system provides detailed logging:

-   File processing status
-   Data validation results
-   Missing value handling
-   Data type conversion results
-   Summary statistics

Logs are written to both console and `logs/food_price_consolidation.log`.

## 🤝 Contributing

This project uses Poetry for dependency management and follows Python best practices:

1. Install development dependencies: `poetry install --with dev`
2. Run tests: `poetry run pytest tests/consolidation/`
3. Format code: `black src/ tests/`
4. Lint code: `ruff check src/ tests/`

## 📄 License

This project is part of a thesis research on food price clustering analysis in Kalimantan.

## 🔮 Future Development

This consolidation system is the foundation for:

-   Exploratory Data Analysis (EDA)
-   Feature Engineering
-   Clustering Analysis
-   Interactive Visualizations
-   Geographic Analysis

Each component will be developed in separate branches to maintain clean version control.
