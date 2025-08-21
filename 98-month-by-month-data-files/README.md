# 📊 Monthly CSV Splitter for Futures Trading Data

A powerful Python script that splits large CSV files containing 17+ years of OHLCV futures trading data into organized monthly files with intelligent progress tracking and time estimation.

## 🚀 Features

### **Core Functionality**
- **Automatic Monthly Splitting** - Divides large CSV files by month for easier analysis
- **Sunday-Monday Edge Case Handling** - Places Sunday data in the same month as Monday when they span different months
- **Multi-Instrument Support** - Processes multiple trading instruments (MGC, MCL, MES, NG, SI)
- **Intelligent File Naming** - Creates descriptive filenames: `MGC_2023_01_January.csv`
- **Directory Structure Creation** - Automatically builds organized folder hierarchies
- **Professional CSV Headers** - Adds descriptive column headers to each monthly file

### **Advanced Progress Tracking**
- **Real-Time Progress Bars** - Visual progress indicators for each processing stage
- **Time Estimation** - Accurate ETA calculations based on file sizes and processing speed
- **Performance Metrics** - Shows processing rates (rows/sec, MB/min, files/sec)
- **Batch Progress** - Overall progress across multiple instruments
- **Memory Optimization** - Efficient processing with batched updates

### **User Experience**
- **Pre-Processing Analysis** - File size scanning and time estimation before starting
- **Interactive Confirmation** - User approval before processing large datasets
- **Comprehensive Reporting** - Detailed statistics and final summaries
- **Error Handling** - Graceful handling of missing files and parsing errors
- **Fallback Support** - Works with or without the `tqdm` library

## 📁 File Structure

### Input Files
```
month by month data files/
├── MGC-1m_data.csv     # Gold futures (17+ years)
├── MCL-1m_data.csv     # Crude oil futures
├── mes-1m_data.csv     # E-mini S&P 500 futures
├── ng-1m_bk.csv        # Natural gas futures
├── si-1m_bk.csv        # Silver futures
└── monthly yearly split script/
    └── monthly_splitter.py
```

### Output Structure
```
month by month data files/
├── MGC/                # Gold instrument folder
│   ├── 2008/
│   │   ├── 01-January/
│   │   │   └── MGC_2008_01_January.csv
│   │   ├── 02-Febuary/
│   │   │   └── MGC_2008_02_February.csv
│   │   └── ...
│   ├── 2009/
│   └── ...
├── MCL/                # Crude oil instrument folder
├── MES/                # E-mini S&P 500 instrument folder
├── NG/                 # Natural gas instrument folder
└── SI/                 # Silver instrument folder
```

## 🔧 Installation & Setup

### Prerequisites
```bash
# Ensure Python 3.6+ is installed
python --version

# Install required library for enhanced progress bars
python -m pip install tqdm
```

### Configuration
The script is pre-configured to process all your CSV files. To modify paths or add instruments, edit the `CONFIGURATION` section in `main()`:

```python
# CONFIGURATION - MODIFY THESE PATHS AS NEEDED
source_directory = r"C:\Users\salte\ClaudeProjects\github-repos\month by month data files"
target_base_directory = r"C:\Users\salte\ClaudeProjects\github-repos\month by month data files"

# List of CSV files to process
instruments = [
    ("MGC-1m_data.csv", "MGC"),
    ("MCL-1m_data.csv", "MCL"),
    ("mes-1m_data.csv", "MES"),
    ("ng-1m_bk.csv", "NG"),
    ("si-1m_bk.csv", "SI")
]
```

## 🏃‍♂️ Usage

### Running the Script
```bash
# Navigate to the script directory
cd "C:\Users\salte\ClaudeProjects\github-repos\month by month data files\monthly yearly split script"

# Run the script
python monthly_splitter.py
```

### Sample Output
```
🚀========================================================🚀
  📊 MONTHLY CSV SPLITTER FOR FUTURES TRADING DATA 📊
🚀========================================================🚀

📋 Scanning source files...
  ✅ MGC-1m_data.csv    → MGC  (45.2 MB)
  ✅ MCL-1m_data.csv    → MCL  (67.8 MB)
  ✅ mes-1m_data.csv    → MES  (23.1 MB)
  ✅ ng-1m_bk.csv       → NG   (34.5 MB)
  ✅ si-1m_bk.csv       → SI   (28.9 MB)

📈 PROCESSING SUMMARY:
  📁 Files to process: 5
  💾 Total data size: 199.5 MB
  ⏱️  Estimated time: 3.0 minutes
  🎯 Start time: 14:23:15

☕ This might take a while - perfect time for a coffee break!

▶️  Press Enter to start processing or Ctrl+C to cancel...

📦 Overall Progress |████████████████████| 2/5 [01:23<00:41] Success: 2/2, ETA: 1.2m

==================================================
Processing MGC: MGC-1m_data.csv
==================================================
File size: 45.2 MB
Estimated rows: 1,234,567

📖 Reading data |████████████████████| 1.2M/1.2M [00:15<00:00, 80.5K rows/s]
✅ Successfully read 1,234,567 rows spanning 17 years (2008-2024)
🔄 Sorting data by date...
✅ Sorting complete in 2.3s
📁 Creating directory structure...
📊 Grouping data by month...
🗂️  Grouping by month |████████████████████| 1.2M/1.2M [00:08<00:00, 150K rows/s]
✅ Grouped into 204 monthly datasets
📅 Applied 23 Sunday-Monday adjustments
💾 Writing monthly files...
📝 Writing files |████████████████████| 204/204 [00:03<00:00, 68.0 files/s]

✅ MGC COMPLETE!
   📊 Files created: 204
   📈 Rows processed: 1,234,567
   💾 Rows written: 1,234,567
   ⏱️  Total time: 28.6s
   🚀 Processing rate: 43,171 rows/sec

🎉 MGC processing completed successfully!
```

## 📊 Data Format

### Input CSV Format
```
26/11/2008;01:00;1084.649221;1084.649221;1084.649221;1084.649221;1
26/11/2008;01:01;1085.183992;1085.986148;1085.183992;1085.986148;6
26/11/2008;01:02;1085.58507;1085.58507;1085.050299;1085.050299;11
```
*Note: Input files have no headers - just raw OHLCV data*

### Output CSV Format
Each monthly file includes professional headers and maintains semicolon-delimited format:
```
Date (D);Time (T);Open (O);High (H);Low (L);Close (C);Volume (V)
01/01/2025;17:00:00;2714.94089;2715.352288;2713.399093;2713.707492;163
01/01/2025;17:01:00;2713.913091;2714.015891;2713.399093;2713.707492;61
01/01/2025;17:02:00;2713.609692;2714.29149;2713.399093;2713.810292;74
```

**Header Format:**
- **Date (D)** - Trading date in DD/MM/YYYY format
- **Time (T)** - Trading time in HH:MM:SS format
- **Open (O)** - Opening price for the time period
- **High (H)** - Highest price during the time period
- **Low (L)** - Lowest price during the time period
- **Close (C)** - Closing price for the time period
- **Volume (V)** - Trading volume for the time period

## 🔍 Key Algorithms

### Sunday-Monday Edge Case Handler
```python
def handle_sunday_monday_case(current_date, next_date):
    """
    Handle the Sunday-Monday edge case.
    If Sunday is in one month and Monday is in the next month,
    place Sunday data in the same month as Monday.
    """
    if current_date.weekday() == 6 and next_date.weekday() == 0:
        if current_date.month != next_date.month:
            return next_date.month  # Place Sunday in Monday's month
    return current_date.month
```

### Processing Pipeline
1. **File Analysis** - Scan files, estimate processing time
2. **Data Reading** - Parse CSV with progress tracking
3. **Date Sorting** - Chronological organization
4. **Monthly Grouping** - Apply Sunday-Monday logic
5. **Directory Creation** - Build folder structure
6. **File Writing** - Save monthly CSV files with professional headers
7. **Validation** - Verify data integrity and header formatting

## 📈 Performance

### Typical Processing Speeds
- **Reading**: 50,000 - 100,000 rows/second
- **Grouping**: 100,000 - 200,000 rows/second
- **Writing**: 50 - 100 files/second
- **Overall**: ~1.5 minutes per 100MB

### Memory Usage
- **Optimized for large files** - Processes data in memory for speed
- **Batched progress updates** - Reduces overhead
- **Efficient sorting algorithms** - Handles millions of rows

## 🛠️ Technical Details

### Dependencies
- **Python 3.6+** (Built-in libraries: csv, datetime, pathlib, time)
- **tqdm** (Optional - for enhanced progress bars)
- **Fallback mode** if tqdm not available

### File Naming Convention
- **Directories**: `01-January`, `02-Febuary` (matches existing structure)
- **Files**: `{instrument}_{year}_{month}_{monthname}.csv`
- **Example**: `MGC_2023_01_January.csv`

### Error Handling
- **Missing files** - Graceful skipping with warnings
- **Invalid date formats** - Row-level error reporting
- **Disk space** - File write error handling
- **Memory limits** - Efficient data processing

## 🔧 Customization

### Adding New Instruments
```python
instruments = [
    ("MGC-1m_data.csv", "MGC"),
    ("your-new-file.csv", "SYMBOL"),  # Add here
]
```

### Changing File Naming
Modify the `get_month_name_for_filename()` function:
```python
def get_month_name_for_filename(month_number):
    # Customize the naming format here
    return f"{month_number:02d}_YourFormat"
```

### Adjusting Progress Updates
```python
# Update frequency (every N rows)
if row_num % 10000 == 0:  # Change 10000 to desired frequency
    pbar.set_postfix({"Valid rows": len(all_rows)})
```

## 🚨 Troubleshooting

### Common Issues

**"No valid source files found"**
- Check file paths in configuration
- Ensure CSV files exist in source directory

**"Error parsing date"**
- Verify CSV format matches DD/MM/YYYY;HH:MM
- Check for corrupted data rows

**"Permission denied writing file"**
- Ensure write permissions in target directory
- Check available disk space

**Progress bars not showing**
- Install tqdm: `python -m pip install tqdm`
- Script works without tqdm (fallback mode)

### Performance Tips
- **SSD drives** provide faster processing
- **Close other applications** to free memory
- **Large files** benefit from more RAM

## 📝 Output Summary

After processing, you'll have:
- **Organized monthly files** for each trading instrument
- **17+ years of data** split by month for efficient analysis
- **Preserved data integrity** with all OHLCV information
- **Professional CSV headers** for immediate Excel/analysis compatibility
- **Chronologically sorted** files for time series analysis
- **Sunday-Monday adjustments** applied where necessary
- **Self-documenting files** with clear column descriptions

## 🎯 Use Cases

### Trading Analysis
- **Seasonal patterns** - Analyze monthly trading behaviors
- **Performance metrics** - Monthly P&L calculations
- **Backtesting** - Strategy testing on monthly datasets
- **Risk management** - Monthly volatility analysis

### Data Management
- **Reduced file sizes** - Easier to work with monthly chunks
- **Faster queries** - Load only relevant months
- **Parallel processing** - Analyze multiple months simultaneously
- **Storage efficiency** - Organized data structure
- **Excel Ready** - Professional headers for immediate spreadsheet analysis
- **Analysis Tools** - Compatible with pandas, R, and other data analysis frameworks

## 📞 Support

For questions or issues:
1. Check the troubleshooting section above
2. Verify file formats and paths
3. Review the console output for specific error messages
4. Ensure Python and required libraries are properly installed

---

*Script created for processing 17+ years of futures trading data with intelligent monthly splitting and comprehensive progress tracking.*