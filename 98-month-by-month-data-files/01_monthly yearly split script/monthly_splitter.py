#!/usr/bin/env python3
"""
Monthly CSV Splitter for Futures Trading Data

This script splits large CSV files containing OHLCV futures data into monthly files.
Handles the Sunday-Monday edge case by placing Sunday data in the same month as Monday.
"""

import os
import csv
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path

# Try to import tqdm for progress bars, fallback if not available
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    print("Note: Install 'tqdm' for enhanced progress bars: pip install tqdm")
    
    # Simple fallback progress indicator
    class tqdm:
        def __init__(self, iterable=None, total=None, desc="", unit="", **kwargs):
            self.iterable = iterable if iterable is not None else range(total) if total else []
            self.total = total if total is not None else len(self.iterable) if hasattr(self.iterable, '__len__') else 0
            self.desc = desc
            self.unit = unit
            self.current = 0
            self.start_time = time.time()
            print(f"{desc}: Starting...")
            
        def __iter__(self):
            for item in self.iterable:
                yield item
                self.update(1)
            
        def update(self, n=1):
            self.current += n
            if self.total > 0:
                percent = (self.current / self.total) * 100
                elapsed = time.time() - self.start_time
                if self.current > 0:
                    eta = (elapsed / self.current) * (self.total - self.current)
                    print(f"\r{self.desc}: {self.current}/{self.total} ({percent:.1f}%) - ETA: {eta:.1f}s", end="")
                    
        def close(self):
            elapsed = time.time() - self.start_time
            print(f"\n{self.desc}: Complete in {elapsed:.1f}s")


def get_month_mapping():
    """Return mapping of month numbers to names with prefixes for sorting."""
    return {
        1: "01-January",
        2: "02-Febuary",  # Using existing directory spelling
        3: "03-March",
        4: "04-April",
        5: "05-May",
        6: "06-June",
        7: "07-July",
        8: "08-August",
        9: "09-September",
        10: "10-October",
        11: "11-November",
        12: "12-December"
    }


def get_month_name_for_filename(month_number):
    """Return month name for filename in format: 01_January, 02_February, etc."""
    month_names = {
        1: "01_January",
        2: "02_February", 
        3: "03_March",
        4: "04_April",
        5: "05_May",
        6: "06_June",
        7: "07_July",
        8: "08_August",
        9: "09_September",
        10: "10_October",
        11: "11_November",
        12: "12_December"
    }
    return month_names.get(month_number, f"{month_number:02d}_Unknown")


def parse_date(date_str):
    """Parse date string in DD/MM/YYYY format."""
    try:
        return datetime.strptime(date_str, "%d/%m/%Y")
    except ValueError as e:
        print(f"Error parsing date '{date_str}': {e}")
        return None


def handle_sunday_monday_case(current_date, next_date):
    """
    Handle the Sunday-Monday edge case.
    If Sunday is in one month and Monday is in the next month,
    place Sunday data in the same month as Monday.
    """
    if current_date is None or next_date is None:
        return current_date.month if current_date else None
    
    # Check if current day is Sunday (6) and next day is Monday (0)
    if current_date.weekday() == 6 and next_date.weekday() == 0:
        # Check if they're in different months
        if current_date.month != next_date.month:
            # Place Sunday data in Monday's month
            return next_date.month
    
    return current_date.month


def create_directory_structure(base_path, instrument_name, years):
    """Create directory structure for the instrument."""
    month_mapping = get_month_mapping()
    instrument_path = Path(base_path) / instrument_name
    
    for year in years:
        year_path = instrument_path / str(year)
        year_path.mkdir(parents=True, exist_ok=True)
        
        for month_folder in month_mapping.values():
            month_path = year_path / month_folder
            month_path.mkdir(exist_ok=True)
    
    return instrument_path


def get_file_line_count(file_path):
    """Get approximate line count for progress tracking."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except:
        return 0


def split_csv_by_month(source_file, target_base_path, instrument_name):
    """
    Split CSV file by month, handling Sunday-Monday edge case.
    """
    print(f"\n{'='*50}")
    print(f"Processing {instrument_name}: {source_file.name}")
    print(f"{'='*50}")
    
    start_time = time.time()
    
    # Get file size for progress estimation
    file_size_mb = source_file.stat().st_size / (1024 * 1024)
    line_count = get_file_line_count(source_file)
    
    print(f"File size: {file_size_mb:.1f} MB")
    print(f"Estimated rows: {line_count:,}")
    
    # Read all data first to handle Sunday-Monday cases
    all_rows = []
    years = set()
    
    try:
        with open(source_file, 'r', newline='', encoding='utf-8') as f:
            # Check if file is semicolon or comma delimited
            sample = f.read(1024)
            f.seek(0)
            delimiter = ';' if ';' in sample else ','
            
            reader = csv.reader(f, delimiter=delimiter)
            
            # Progress bar for reading
            with tqdm(total=line_count, desc="📖 Reading data", unit=" rows", 
                     bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]") as pbar:
                
                for row_num, row in enumerate(reader, 1):
                    if len(row) >= 2:  # Ensure we have at least date and time
                        date_str = row[0]
                        parsed_date = parse_date(date_str)
                        if parsed_date:
                            years.add(parsed_date.year)
                            all_rows.append((parsed_date, row))
                        else:
                            if row_num <= 10:  # Only show first few invalid rows
                                print(f"Skipping invalid row {row_num}: {row}")
                    
                    pbar.update(1)
                    
                    # Update every 10000 rows for better performance
                    if row_num % 10000 == 0:
                        pbar.set_postfix({"Valid rows": len(all_rows), "Years": len(years)})
    
    except Exception as e:
        print(f"❌ Error reading source file: {e}")
        return False
    
    if not all_rows:
        print("❌ No valid data found in source file")
        return False
    
    print(f"✅ Successfully read {len(all_rows):,} rows spanning {len(years)} years ({min(years)}-{max(years)})")
    
    # Sort rows by date
    print("🔄 Sorting data by date...")
    sort_start = time.time()
    all_rows.sort(key=lambda x: x[0])
    sort_time = time.time() - sort_start
    print(f"✅ Sorting complete in {sort_time:.1f}s")
    
    # Create directory structure
    print("📁 Creating directory structure...")
    instrument_path = create_directory_structure(target_base_path, instrument_name, years)
    month_mapping = get_month_mapping()
    
    # Group data by month, handling Sunday-Monday case
    print("📊 Grouping data by month...")
    monthly_data = {}
    sunday_adjustments = 0
    
    with tqdm(total=len(all_rows), desc="🗂️  Grouping by month", unit=" rows",
             bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]") as pbar:
        
        for i, (current_date, row) in enumerate(all_rows):
            # Look ahead to next row for Sunday-Monday check
            next_date = None
            if i + 1 < len(all_rows):
                next_date = all_rows[i + 1][0]
            
            # Determine which month this row belongs to
            original_month = current_date.month
            target_month = handle_sunday_monday_case(current_date, next_date)
            if target_month is None:
                target_month = current_date.month
            elif target_month != original_month:
                sunday_adjustments += 1
            
            year = current_date.year
            month_key = (year, target_month)
            
            if month_key not in monthly_data:
                monthly_data[month_key] = []
            
            monthly_data[month_key].append(row)
            pbar.update(1)
            
            # Update postfix every 10000 rows
            if i % 10000 == 0:
                pbar.set_postfix({"Months": len(monthly_data), "Sunday adj.": sunday_adjustments})
    
    print(f"✅ Grouped into {len(monthly_data)} monthly datasets")
    if sunday_adjustments > 0:
        print(f"📅 Applied {sunday_adjustments} Sunday-Monday adjustments")
    
    # Write monthly files
    print("💾 Writing monthly files...")
    files_created = 0
    total_rows_written = 0
    
    with tqdm(total=len(monthly_data), desc="📝 Writing files", unit=" files",
             bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]") as pbar:
        
        for (year, month), rows in monthly_data.items():
            month_folder = month_mapping[month]
            output_dir = instrument_path / str(year) / month_folder
            month_name_for_file = get_month_name_for_filename(month)
            output_file = output_dir / f"{instrument_name}_{year}_{month_name_for_file}.csv"
            
            try:
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f, delimiter=';')  # Using semicolon as in original
                    
                    # Write header row
                    header = ['Date (D)', 'Time (T)', 'Open (O)', 'High (H)', 'Low (L)', 'Close (C)', 'Volume (V)']
                    writer.writerow(header)
                    
                    # Write data rows
                    writer.writerows(rows)
                
                files_created += 1
                total_rows_written += len(rows)
                pbar.set_postfix({"Rows written": total_rows_written})
                
            except Exception as e:
                print(f"❌ Error writing file {output_file}: {e}")
            
            pbar.update(1)
    
    # Final summary
    elapsed_total = time.time() - start_time
    print(f"\n✅ {instrument_name} COMPLETE!")
    print(f"   📊 Files created: {files_created}")
    print(f"   📈 Rows processed: {len(all_rows):,}")
    print(f"   💾 Rows written: {total_rows_written:,}")
    print(f"   ⏱️  Total time: {elapsed_total:.1f}s")
    print(f"   🚀 Processing rate: {len(all_rows)/elapsed_total:,.0f} rows/sec")
    
    return True


def estimate_processing_time(source_files, source_directory):
    """Estimate total processing time based on file sizes."""
    total_size_mb = 0
    valid_files = 0
    
    for filename, _ in source_files:
        file_path = Path(source_directory) / filename
        if file_path.exists():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            total_size_mb += size_mb
            valid_files += 1
    
    if valid_files == 0:
        return 0, 0
    
    # Rough estimate: ~1-2 minutes per 100MB (depends on CPU and disk speed)
    estimated_minutes = (total_size_mb / 100) * 1.5
    return total_size_mb, estimated_minutes


def main():
    """Main function - configure these paths as needed."""
    
    # CONFIGURATION - MODIFY THESE PATHS AS NEEDED
    source_directory = r"C:\Users\salte\ClaudeProjects\github-repos\month by month data files\source files not for backtesting"
    target_base_directory = r"C:\Users\salte\ClaudeProjects\github-repos\month by month data files"
    
    # List of CSV files to process (without extension)
    instruments = [
        ("MGC-1m_data.csv", "MGC"),
        ("MCL-1m_data.csv", "MCL"),
        ("mes-1m_data.csv", "MES"),
        ("ng-1m_bk.csv", "NG"),
        ("si-1m_bk.csv", "SI")
    ]
    
    print("🚀" + "=" * 58 + "🚀")
    print("  📊 MONTHLY CSV SPLITTER FOR FUTURES TRADING DATA 📊")
    print("🚀" + "=" * 58 + "🚀")
    
    # Calculate file sizes and estimate processing time
    print("\n📋 Scanning source files...")
    total_size_mb, estimated_minutes = estimate_processing_time(instruments, source_directory)
    
    existing_files = []
    missing_files = []
    
    for filename, instrument_name in instruments:
        source_file = Path(source_directory) / filename
        if source_file.exists():
            size_mb = source_file.stat().st_size / (1024 * 1024)
            existing_files.append((filename, instrument_name, source_file, size_mb))
            print(f"  ✅ {filename:<20} → {instrument_name:<4} ({size_mb:.1f} MB)")
        else:
            missing_files.append((filename, instrument_name))
            print(f"  ❌ {filename:<20} → {instrument_name:<4} (NOT FOUND)")
    
    if missing_files:
        print(f"\n⚠️  {len(missing_files)} files not found - they will be skipped")
    
    if not existing_files:
        print("\n❌ No valid source files found! Please check the file paths.")
        return
    
    print(f"\n📈 PROCESSING SUMMARY:")
    print(f"  📁 Files to process: {len(existing_files)}")
    print(f"  💾 Total data size: {total_size_mb:.1f} MB")
    print(f"  ⏱️  Estimated time: {estimated_minutes:.1f} minutes")
    print(f"  🎯 Start time: {datetime.now().strftime('%H:%M:%S')}")
    
    if estimated_minutes > 2:
        print(f"\n☕ This might take a while - perfect time for a coffee break!")
    
    input("\n▶️  Press Enter to start processing or Ctrl+C to cancel...")
    
    # Start overall processing timer
    overall_start = time.time()
    successful_processes = 0
    total_files_created = 0
    total_rows_processed = 0
    
    print(f"\n{'🔄 STARTING BATCH PROCESSING 🔄':^60}")
    print("=" * 60)
    
    with tqdm(total=len(existing_files), desc="📦 Overall Progress", unit=" instruments",
             bar_format="{l_bar}{bar}| {n}/{total} [{elapsed}<{remaining}] {postfix}") as overall_pbar:
        
        for i, (filename, instrument_name, source_file, size_mb) in enumerate(existing_files, 1):
            overall_pbar.set_description(f"📦 Processing {instrument_name}")
            
            success = split_csv_by_month(source_file, target_base_directory, instrument_name)
            
            if success:
                successful_processes += 1
                print(f"🎉 {instrument_name} processing completed successfully!")
            else:
                print(f"💥 {instrument_name} processing failed!")
            
            overall_pbar.update(1)
            
            # Update progress postfix
            elapsed = time.time() - overall_start
            remaining_files = len(existing_files) - i
            avg_time_per_file = elapsed / i
            eta_seconds = remaining_files * avg_time_per_file
            
            overall_pbar.set_postfix({
                "Success": f"{successful_processes}/{i}",
                "ETA": f"{eta_seconds/60:.1f}m"
            })
    
    # Final summary
    total_elapsed = time.time() - overall_start
    actual_minutes = total_elapsed / 60
    
    print(f"\n🏁" + "=" * 58 + "🏁")
    print(f"  🎯 BATCH PROCESSING COMPLETE!")
    print(f"🏁" + "=" * 58 + "🏁")
    print(f"\n📊 FINAL SUMMARY:")
    print(f"  ✅ Successful: {successful_processes}/{len(existing_files)} instruments")
    print(f"  ⏱️  Total time: {actual_minutes:.1f} minutes")
    print(f"  📈 Data processed: {total_size_mb:.1f} MB")
    print(f"  🚀 Average speed: {total_size_mb/actual_minutes:.1f} MB/min")
    print(f"  🏁 Finished at: {datetime.now().strftime('%H:%M:%S')}")
    
    if successful_processes == len(existing_files):
        print(f"\n🎉 ALL FILES PROCESSED SUCCESSFULLY! 🎉")
    elif successful_processes > 0:
        print(f"\n⚠️  {len(existing_files) - successful_processes} files failed to process")
    else:
        print(f"\n❌ NO FILES WERE PROCESSED SUCCESSFULLY")
    
    print(f"\n💡 Tip: Install 'tqdm' for better progress bars: pip install tqdm")
    print("=" * 60)


if __name__ == "__main__":
    main()