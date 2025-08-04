#!/usr/bin/env python3
"""
YAML Configuration-Based Data Consolidation Runner

This is the RECOMMENDED way to run data consolidation using configuration files.
It's cleaner, more maintainable, and version-controllable than CLI arguments.

Usage:
    # Use default configuration
    python scripts/run_consolidation.py
    
    # Use specific configuration file
    python scripts/run_consolidation.py configs/twelve_cities.yaml
    
    # List available configurations
    python scripts/run_consolidation.py --list-configs

Available configurations:
    - configs/default_consolidation.yaml   # Standard full analysis (2022-2024, all cities)
    - configs/twelve_cities.yaml          # 12 representative cities (2020-2024)
    - configs/2018_2023.yaml              # Historical analysis (2018-2023)
"""

import argparse
import sys
import yaml
from pathlib import Path

# Add the src directory to the path so we can import our package
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clustering_food_prices_kalimantan import ConsolidationPipeline, ConsolidatorConfig, PathConfig


def list_available_configs():
    """List all available configuration files."""
    configs_dir = Path("configs")
    if not configs_dir.exists():
        print("❌ No configs directory found")
        return
    
    config_files = list(configs_dir.glob("*.yaml"))
    if not config_files:
        print("❌ No YAML configuration files found in configs/")
        return
    
    print("📋 Available Configuration Files:")
    print("=" * 50)
    
    for config_file in sorted(config_files):
        print(f"\n🔧 {config_file.name}")
        try:
            with open(config_file) as f:
                config_data = yaml.safe_load(f)
            
            # Extract key info for display
            commodities = config_data.get('target_commodities', [])
            years = config_data.get('target_years', 'All years')
            cities = config_data.get('target_cities', 'All cities')
            
            print(f"   📈 Commodities: {len(commodities)} items")
            print(f"   📅 Years: {years}")
            print(f"   🏙️  Cities: {cities if isinstance(cities, str) else f'{len(cities)} cities'}")
            
            # Show first comment line as description
            with open(config_file) as f:
                first_line = f.readline().strip()
                if first_line.startswith('#'):
                    print(f"   📝 {first_line[1:].strip()}")
                    
        except Exception as e:
            print(f"   ❌ Error reading config: {e}")
    
    print(f"\n💡 Usage: python scripts/run_consolidation.py configs/[filename]")
    print(f"💡 Or use built-in defaults: python scripts/run_consolidation.py")


def load_config_file(config_path: Path) -> dict:
    """Load and validate configuration file."""
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    if config_path.suffix.lower() not in ['.yaml', '.yml']:
        raise ValueError(f"Configuration file must be YAML format: {config_path}")
    
    try:
        with open(config_path) as f:
            config_data = yaml.safe_load(f)
        
        if config_data is None:
            raise ValueError("Configuration file is empty or invalid")
        
        return config_data
    
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML format in {config_path}: {e}")


def show_built_in_defaults():
    """Show the built-in default configuration."""
    config = ConsolidatorConfig()
    paths = PathConfig()
    
    print("🔧 Built-in Default Configuration:")
    print("=" * 50)
    print()
    
    print("📈 Target Commodities:")
    for i, commodity in enumerate(config.target_commodities, 1):
        print(f"   {i}. {commodity}")
    
    print(f"\n📅 Years: All available years (no filtering)")
    print(f"🏙️  Cities: {len(config.target_cities)} cities ({", ".join(config.target_cities)})")
    
    print(f"\n📁 Data Paths:")
    print(f"   📂 Input: {paths.raw_data_dir}")
    print(f"   📂 Output: {paths.processed_data_dir}")
    
    print(f"\n📊 Output Settings:")
    print(f"   📄 CSV: {config.default_csv_output}")
    print(f"   📊 Excel: {config.default_excel_output}")
    print(f"   📋 Formats: Both CSV and Excel")
    
    print(f"\n🔧 Processing Settings:")
    print(f"   📊 Log Level: {config.log_level}")
    print(f"   🔍 File Pattern: {config.file_pattern}")
    print(f"   ❌ Missing Indicators: {', '.join(config.missing_value_indicators[:3])}...")
    
    print(f"\n💡 To customize these settings:")
    print(f"   1. Create a YAML config: cp configs/default_consolidation.yaml my_config.yaml")
    print(f"   2. Edit my_config.yaml to your needs")
    print(f"   3. Run: python scripts/run_consolidation.py my_config.yaml")
    
    print(f"\n💡 Or use built-in defaults: python scripts/run_consolidation.py")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run data consolidation using YAML configuration files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_consolidation.py                           # Use built-in defaults
  python scripts/run_consolidation.py configs/recent_years.yaml # Use specific config
  python scripts/run_consolidation.py --list-configs            # Show available configs
  python scripts/run_consolidation.py --show-defaults           # Show built-in defaults
        """
    )
    
    parser.add_argument(
        "config_file",
        nargs="?",
        default=None,
        help="Path to YAML configuration file (optional: uses built-in defaults if not provided)"
    )
    
    parser.add_argument(
        "--list-configs",
        action="store_true",
        help="List all available configuration files and exit"
    )
    
    parser.add_argument(
        "--show-defaults",
        action="store_true",
        help="Show built-in default configuration and exit"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be processed without actually running consolidation"
    )
    
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Run consolidation but don't save output files"
    )
    
    return parser.parse_args()


def main():
    """Main function."""
    args = parse_arguments()
    
    print("🍚 Food Price Data Consolidator for Kalimantan")
    print("=" * 50)
    
    # Handle list configs command
    if args.list_configs:
        list_available_configs()
        return 0
    
    # Handle show defaults command
    if args.show_defaults:
        show_built_in_defaults()
        return 0
    
    try:
        # Load configuration (YAML file or built-in defaults)
        if args.config_file:
            config_path = Path(args.config_file)
            print(f"📁 Loading configuration: {config_path}")
            config_data = load_config_file(config_path)
            config_source = f"YAML file: {config_path}"
        else:
            print("🔧 Using built-in default configuration")
            config_data = {}  # Empty dict means use all defaults
            config_source = "Built-in defaults"
        
        # Extract and clean configuration data
        consolidated_config = {}
        
        # Map YAML keys to ConsolidatorConfig parameters
        config_mapping = {
            'target_commodities': 'target_commodities',
            'target_years': 'target_years', 
            'year_range_start': 'year_range_start',
            'year_range_end': 'year_range_end',
            'target_cities': 'target_cities',
            'log_level': 'log_level',
            'enable_logging': 'enable_logging',
            'file_pattern': 'file_pattern',
            'missing_value_indicators': 'missing_value_indicators',
            'csv_filename': 'default_csv_output',
            'excel_filename': 'default_excel_output'
        }
        
        for yaml_key, config_key in config_mapping.items():
            if yaml_key in config_data and config_data[yaml_key] is not None:
                consolidated_config[config_key] = config_data[yaml_key]
        
        # Create configuration objects
        config = ConsolidatorConfig(**consolidated_config)
        
        # Handle paths
        paths = PathConfig()
        if 'data_root' in config_data:
            data_root = config_data['data_root']
        else:
            data_root = None
            
        if 'output_dir' in config_data:
            paths.processed_data_dir = Path(config_data['output_dir'])
        
        # Show configuration summary
        print(f"✅ Configuration loaded successfully!")
        print(f"   🔧 Source: {config_source}")
        print(f"   📈 Commodities: {len(config.target_commodities)} items")
        if config.target_years:
            years_display = f"{config.target_years}"
        elif config.year_range_start or config.year_range_end:
            start = config.year_range_start or "any"
            end = config.year_range_end or "any"
            years_display = f"{start} to {end}"
        else:
            years_display = "All years"
        print(f"   📅 Years: {years_display}")
        print(f"   🏙️ Cities: {config.target_cities or 'All cities'}")
        print(f"   📊 Log level: {config.log_level}")
        
        if args.dry_run:
            print("\n🔍 DRY RUN MODE - Would process:")
            print(f"   Data root: {data_root or paths.raw_data_dir}")
            print(f"   Output dir: {paths.processed_data_dir}")
            print(f"   Commodities: {', '.join(config.target_commodities)}")
            return 0
        
        # Initialize consolidation pipeline
        pipeline = ConsolidationPipeline(
            data_root=data_root,
            config=config,
            paths=paths
        )
        
        # Validate data structure first
        print("\n📋 Validating data structure...")
        validation_results = pipeline.validate_data_structure()
        
        if validation_results['issues']:
            print("❌ Validation issues found:")
            for issue in validation_results['issues']:
                print(f"  - {issue}")
            
            if not validation_results['valid_files']:
                print("\n❌ No valid files found. Please check your data directory.")
                return 1
        
        print(f"✅ Found {len(validation_results['valid_files'])} valid files")
        
        # Determine output formats
        output_formats = config_data.get('output_formats', ['csv', 'excel'])
        
        # Run consolidation
        print("\n🔄 Running data consolidation...")
        consolidated_df = pipeline.run_consolidation(
            save_outputs=not args.no_save,
            output_formats=output_formats if not args.no_save else None
        )
        
        if consolidated_df.empty:
            print("❌ No data was consolidated. Please check your configuration and data files.")
            return 1
        
        # Show summary
        print("\n📊 Consolidation Summary:")
        summary = pipeline.get_data_summary(consolidated_df)
        
        print(f"  📈 Total records: {summary['total_records']:,}")
        print(f"  🏙️  Cities: {summary['num_cities']}")
        print(f"  🥘 Commodities: {summary['num_commodities']}")
        print(f"  📅 Unique dates: {summary['num_unique_dates']}")
        
        if 'price_statistics' in summary:
            price_stats = summary['price_statistics']  
            print(f"  💰 Price range: {price_stats['min']:,.0f} - {price_stats['max']:,.0f}")
            print(f"  💵 Average price: {price_stats['mean']:,.0f}")
        
        print(f"\n🏙️  Cities: {', '.join(summary['cities'])}")
        print(f"🥘 Commodities: {', '.join(summary['commodities'])}")
        
        # Check for missing values
        total_missing = sum(summary['missing_values'].values())
        if total_missing > 0:
            print(f"\n⚠️  Warning: {total_missing} missing values found")
        
        if not args.no_save:
            print(f"\n💾 Output saved to: {paths.processed_data_dir}")
            for fmt in output_formats:
                if fmt == 'csv':
                    print(f"  📄 CSV: {config.default_csv_output}")
                elif fmt == 'excel':
                    print(f"  📊 Excel: {config.default_excel_output}")
        
        print("\n✅ Data consolidation completed successfully!")
        print(f"🔧 Used configuration: {config_source}")
        return 0
        
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())