# Patsnap SDK Command Line Interface

The Patsnap SDK includes a powerful CLI that helps users discover namespaces, methods, and get started quickly.

## 🚀 Installation & Setup

After installing the SDK, the CLI will be available as the `patsnap` command:

```bash
pip install patsnap-pythonsdk
```

## 📋 Available Commands

### Basic Help
```bash
# Show complete help with all namespaces
patsnap help

# Or run directly from the package directory
python cli.py
```

### Namespace Information
```bash
# List all namespaces
patsnap help namespaces
# or
patsnap help --list

# Get detailed info about a specific namespace
patsnap help -n patents
patsnap help -n analytics
```

### Usage Examples
```bash
# Show common usage examples
patsnap help examples
```

### Getting Started Guide
```bash
# Show step-by-step getting started guide
patsnap help start
```

## 🎯 CLI Features

### ✅ Dynamic Namespace Discovery
The CLI automatically detects which namespaces are implemented vs. planned:
- **✅ Implemented** - Ready to use
- **🚧 Planned** - Coming soon

### 📊 Current Status
```
📁 PATENTS ✅ Implemented
   • search.by_number() - Search patents by patent number

📁 ANALYTICS ✅ Implemented  
   • search.query_count() - Get total patent count
   • search.query_search() - Get full patent data

📁 AI 🚧 Planned
📁 DRUGS 🚧 Planned
📁 LITERATURE 🚧 Planned
📁 CHEMICAL 🚧 Planned
📁 MONITORING 🚧 Planned
```

### 🔍 Detailed Information
For each namespace, the CLI shows:
- Description and purpose
- Available categories and methods
- Usage examples
- Implementation status

## 💡 Example Output

### Main Help Screen
```
🔍 Patsnap Python SDK - Command Line Help
==================================================

📋 Overview:
The Patsnap SDK provides access to patent data, analytics, AI analysis,
drug research, literature search, and more through a clean namespace-based API.

🚀 Quick Start:
  import patsnap_pythonSDK as patsnap
  patsnap.configure(client_id='...', client_secret='...')
  results = patsnap.patents.search.by_number(pn='US123456')

🎯 Available Namespaces:
------------------------------

📁 PATENTS ✅ Implemented
   Patent operations - search, data retrieval, legal information
   Categories:
     • search: Patent search operations
       - by_number(): Search patents by patent number or application number
   Example: patsnap.patents.search.by_number(pn='US123456')

📁 ANALYTICS ✅ Implemented
   Patent analytics, trends, and statistical analysis
   Categories:
     • search: Analytics search operations
       - query_count(): Get total patent count for analytics queries
       - query_search(): Search patents using analytics queries with full data
   Example: patsnap.analytics.search.query_count(query_text='TACD: AI')
```

### Namespace Details
```bash
patsnap help -n analytics
```

```
📁 ANALYTICS Namespace ✅ Implemented
========================================
Description: Patent analytics, trends, and statistical analysis

🔧 Categories:

  📂 search
     Analytics search operations
     Available methods:
       • query_count(): Get total patent count for analytics queries
       • query_search(): Search patents using analytics queries with full data

💡 Example Usage:
  patsnap.analytics.search.query_count(query_text='TACD: AI')

📚 More Information:
  • Examples: examples/analytics/
  • Tests: tests/analytics/
  • Documentation: docs/implementation/
```

## 🛠️ Development Usage

When developing or testing locally:

```bash
# Run from package directory
python cli.py

# Run with specific commands
python cli.py namespaces
python cli.py examples
python cli.py -n patents
```

## 🔗 Integration with Package

The CLI integrates seamlessly with the package structure:
- **Auto-discovery** of implemented namespaces
- **Links to examples** and documentation
- **Consistent with API** design patterns
- **Up-to-date information** as new endpoints are added

## 📈 Future Enhancements

As more endpoints are implemented, the CLI will automatically:
- ✅ Detect new namespaces
- ✅ Show updated method lists
- ✅ Provide relevant examples
- ✅ Guide users to new functionality

The CLI grows with the SDK! 🚀
