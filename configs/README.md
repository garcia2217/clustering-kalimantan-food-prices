# Configuration Files

This directory contains YAML configuration files for different data consolidation scenarios. Using configuration files is the **recommended approach** as it's more maintainable than long command-line arguments.

## 📋 Available Configurations

### 🔧 `default_consolidation.yaml`

**Standard full analysis configuration**

git -   All 5 default commodities (comprehensive coverage)
-   Years: 2022-2024 (recent data focus)
-   All available cities (no filtering)
-   Both CSV and Excel output

**Usage:**

```bash
python scripts/run_consolidation.py configs/default_consolidation.yaml
```

### 🏙️ `twelve_cities.yaml`

**Comprehensive 12-city analysis**

-   All default commodities (Beras, Telur Ayam, Daging Ayam, Bawang Merah, Bawang Putih)
-   Years: 2020-2024 (5-year period)
-   12 representative cities from all 5 Kalimantan provinces
-   Custom output filenames for easy identification

**Usage:**

```bash
python scripts/run_consolidation.py configs/twelve_cities.yaml
```

**Cities included:**

-   **Kalimantan Barat**: kab-sintang, kota-pontianak, kota-singkawang
-   **Kalimantan Selatan**: kota-banjarmasin, kota-tanjung
-   **Kalimantan Tengah**: kota-palangkaraya, kota-sampit
-   **Kalimantan Timur**: kota-balikpapan, kota-samarinda, kota-bontang
-   **Kalimantan Utara**: kab-bulungan, kota-tarakan

### 📅 `2018_2023.yaml`

**Historical year range analysis**

-   All default commodities
-   Years: 2018-2023 (historical period focus)
-   All available cities (no city filtering)
-   Standard output filenames

**Usage:**

```bash
python scripts/run_consolidation.py configs/2018_2023.yaml
```

## 🛠️ Creating Custom Configurations

### 1. Copy an existing configuration:

```bash
cp configs/default_consolidation.yaml configs/my_custom_analysis.yaml
```

### 2. Edit the YAML file:

```yaml
# My custom analysis configuration
target_commodities:
    - "Beras"
    - "Telur Ayam"

target_years:
    - 2024

target_cities:
    - "kota-pontianak"
    - "kota-banjarmasin"

log_level: "DEBUG"
output_formats: ["csv"]
csv_filename: "my_custom_output.csv"
```

### 3. Run with your configuration:

```bash
python scripts/run_consolidation.py configs/my_custom_analysis.yaml
```

## 📖 Configuration Reference

### Required Fields

-   `target_commodities`: List of commodities to process
-   `data_root`: Path to raw data directory
-   `log_level`: Logging level (DEBUG, INFO, WARNING, ERROR)

### Optional Fields

-   `target_years`: List of specific years (e.g., [2022, 2023, 2024])
-   `year_range_start`: Start year (alternative to target_years)
-   `year_range_end`: End year (alternative to target_years)
-   `target_cities`: List of cities to process (omit for all cities)
-   `output_dir`: Output directory path
-   `output_formats`: List of formats ["csv", "excel"]
-   `csv_filename`: Custom CSV filename
-   `excel_filename`: Custom Excel filename
-   `enable_logging`: Enable/disable logging (true/false)
-   `file_pattern`: File search pattern (default: "\*.xlsx")
-   `missing_value_indicators`: List of values to treat as missing

### Example Complete Configuration:

```yaml
# Complete configuration example
target_commodities:
    - "Beras"
    - "Telur Ayam"
    - "Daging Ayam"

target_years: [2022, 2023, 2024]
# OR use year range:
# year_range_start: 2020
# year_range_end: 2024

target_cities:
    - "kota-pontianak"
    - "kota-banjarmasin"

data_root: "data/raw"
output_dir: "data/processed"
output_formats: ["csv", "excel"]

log_level: "INFO"
enable_logging: true
file_pattern: "*.xlsx"

missing_value_indicators: ["-", "", "nan", "NaN", "null", "NULL"]

csv_filename: "consolidated_data.csv"
excel_filename: "consolidated_data.xlsx"
```

## 💡 Best Practices

1. **Use descriptive filenames**: `thesis_2024_analysis.yaml` vs `config1.yaml`
2. **Add comments**: Explain why you chose specific settings
3. **Version control**: Commit your configuration files to git
4. **Share configurations**: Team members can use the same settings
5. **Test configurations**: Use `--dry-run` to validate before running

## 🔄 Migration from CLI Arguments

**Old way (not recommended):**

```bash
# This would require a very long command line with many arguments - NOT SUPPORTED ANYMORE
# python some_script.py --commodities "Beras,Telur Ayam" --years "2023,2024" --cities "kota-pontianak,kota-banjarmasin" --format csv --log-level DEBUG
```

**New way (recommended):**

```yaml
# configs/my_analysis.yaml
target_commodities: ["Beras", "Telur Ayam"]
target_years: [2023, 2024]
target_cities: ["kota-pontianak", "kota-banjarmasin"]
output_formats: ["csv"]
log_level: "DEBUG"
```

```bash
python scripts/run_consolidation.py configs/my_analysis.yaml
```

## 🎯 Quick Commands

```bash
# List all available configurations
python scripts/run_consolidation.py --list-configs

# Test configuration without processing
python scripts/run_consolidation.py configs/twelve_cities.yaml --dry-run

# Process without saving (just see results)
python scripts/run_consolidation.py configs/2018_2023.yaml --no-save
```
