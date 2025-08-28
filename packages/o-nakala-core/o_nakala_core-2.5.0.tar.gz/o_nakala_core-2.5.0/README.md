# O-Nakala Core

A Python library and CLI toolkit for NAKALA research data repository workflows, designed for digital humanities and academic research teams.

## Installation

```bash
# Complete installation with CLI tools
pip install o-nakala-core[cli]

# Core library only
pip install o-nakala-core

# Development installation
git clone https://github.com/xy-liao/o-nakala-core.git
cd o-nakala-core
pip install -e ".[cli,dev]"
```

## Quick Start

### Python API
```python
from o_nakala_core import NakalaConfig, NakalaUserInfoClient

# Configure connection
config = NakalaConfig(api_key="your-api-key")

# Get user information
client = NakalaUserInfoClient(config)
user_info = client.get_user_info()
print(f"Connected as: {user_info['username']}")
```

### CLI Tools
```bash
# Set your API key
export NAKALA_API_KEY="your-api-key"

# Preview and validate metadata before upload
o-nakala-preview --csv your_data.csv --interactive

# Upload datasets from CSV
o-nakala-upload --csv your_data.csv --api-key $NAKALA_API_KEY

# Create collections
o-nakala-collection --from-folder-collections collections.csv

# Quality analysis and curation
o-nakala-curator --quality-report --scope all
```

## CLI Commands

- **`o-nakala-upload`** - Batch upload datasets with CSV-driven metadata
- **`o-nakala-preview`** - Validate and preview metadata before upload
- **`o-nakala-collection`** - Create and manage thematic collections  
- **`o-nakala-curator`** - Metadata curation and quality analysis
- **`o-nakala-user-info`** - Account management and permissions

## Key Features

- **CSV-based workflows** for reproducible research data management
- **Metadata validation** with real-time feedback and suggestions
- **Complete Dublin Core support** for comprehensive metadata
- **Batch operations** for large-scale data uploads and collection management
- **Quality analysis** tools for metadata curation and enhancement
- **Multilingual metadata** support with French/English templates
- **Production-ready error handling** with comprehensive logging

## Basic Workflow

```bash
# 1. Prepare your data in CSV format
# See examples/sample_dataset/ for format reference

# 2. Validate metadata (recommended)
o-nakala-preview --csv folder_data_items.csv --interactive

# 3. Upload data
o-nakala-upload \
  --csv folder_data_items.csv \
  --mode folder \
  --base-path ./data \
  --output upload_results.csv

# 4. Create collections (optional)
o-nakala-collection \
  --from-upload-output upload_results.csv \
  --from-folder-collections collections.csv

# 5. Quality check (recommended)
o-nakala-curator --quality-report
```

## CSV Format Example

**folder_data_items.csv**:
```csv
title,creator,description,type,file
"Research Analysis Scripts","Dupont,Jean","Python scripts for data analysis","http://purl.org/coar/resource_type/c_5ce6","code/analysis.py"
"Survey Results 2023","Martin,Claire","Raw survey data","http://purl.org/coar/resource_type/c_ddb1","data/survey.csv"
```

The library automatically transforms simple CSV formats into complete NAKALA API metadata structures.

## Documentation & Examples

For comprehensive guides, examples, and API documentation, visit the [project repository](https://github.com/xy-liao/o-nakala-core):

- **Getting Started Guide** - Step-by-step setup and first upload
- **Workflow Examples** - Complete research data workflows
- **Interactive Workshop** - Jupyter notebook with hands-on examples
- **API Reference** - Detailed technical documentation
- **Sample Datasets** - Ready-to-use example data and configurations

## Environment Setup

```bash
# Required - Get API key from NAKALA platform
export NAKALA_API_KEY="your-api-key"

# Optional - Set environment (defaults to test)
export NAKALA_BASE_URL="https://apitest.nakala.fr"  # Test environment
# export NAKALA_BASE_URL="https://api.nakala.fr"     # Production
```

## Requirements

- Python 3.9+
- Active NAKALA account with API access
- CSV files with research metadata

## Support

For issues, questions, and contributions:

- **Issues**: [GitHub Issues](https://github.com/xy-liao/o-nakala-core/issues)
- **Documentation**: [Project Repository](https://github.com/xy-liao/o-nakala-core)
- **NAKALA Platform**: [nakala.fr](https://nakala.fr)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions welcome! Please see the repository for development setup and contribution guidelines.

---

**Built for academic and research teams who need reliable, straightforward tools for research data management.**